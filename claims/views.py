from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone
from django.template.loader import render_to_string
from django.contrib.auth.models import User
import json
import queue
from .models import Claim, ClaimDetail, Flag, Note, UserProfile
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, NoteForm, FlagForm

# Simple in-process real-time event hub (SSE)
_event_clients = set()

def notify_clients(event_type: str, payload: dict) -> None:
    event = { 'type': event_type, 'timestamp': timezone.now().isoformat(), **payload }
    for client_q in list(_event_clients):
        try:
            client_q.put_nowait(event)
        except Exception:
            _event_clients.discard(client_q)


def admin_events(request):
    """Server-Sent Events endpoint for admin dashboard real-time updates."""
    def event_stream():
        client_q = queue.Queue()
        _event_clients.add(client_q)
        try:
            # Initial connection message
            yield f"data: {json.dumps({'type': 'connection', 'message': 'connected'})}\n\n"
            while True:
                try:
                    event = client_q.get(timeout=15)
                    yield f"data: {json.dumps(event)}\n\n"
                except queue.Empty:
                    yield f"data: {json.dumps({'type': 'heartbeat', 'ts': timezone.now().isoformat()})}\n\n"
        finally:
            _event_clients.discard(client_q)

    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    return response


def index(request):
    """Main claims list view"""
    page = request.GET.get('page', 1)
    per_page = 10
    
    # Search and filter functionality
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    insurer_filter = request.GET.get('insurer', '')
    
    claims = Claim.objects.all()
    
    if search:
        claims = claims.filter(
            Q(patient_name__icontains=search) |
            Q(claim_id__icontains=search) |
            Q(insurer_name__icontains=search)
        )
    
    if status_filter:
        claims = claims.filter(status=status_filter)
    
    if insurer_filter:
        claims = claims.filter(insurer_name=insurer_filter)
    
    claims = claims.order_by('-created_at')
    
    # Get unique statuses and insurers for filter dropdowns
    statuses = Claim.objects.values_list('status', flat=True).distinct()
    insurers = Claim.objects.values_list('insurer_name', flat=True).distinct()
    # KPI stats
    total_claims = Claim.objects.count()
    flagged_claims = Flag.objects.count()
    total_billed = Claim.objects.aggregate(total=Sum('billed_amount'))['total'] or 0
    total_paid = Claim.objects.aggregate(total=Sum('paid_amount'))['total'] or 0
    average_underpayment = total_billed - total_paid
    
    context = {
        'claims': claims,
        'search': search,
        'status_filter': status_filter,
        'insurer_filter': insurer_filter,
        'statuses': statuses,
        'insurers': insurers,
        'user': request.user,
        'stats': {
            'total_claims': total_claims,
            'flagged_claims': flagged_claims,
            'total_billed': total_billed,
            'average_underpayment': average_underpayment,
        }
    }
    
    # If this is an HTMX request, return just the table fragment to avoid duplicating the page UI
    if request.headers.get('HX-Request'):
        return render(request, 'partials/claims_table.html', context)

    return render(request, 'index.html', context)


def user_register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('claims:index')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'auth/register.html', {'form': form})


def user_login(request):
    """User login view"""
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                remember_me = form.cleaned_data.get('remember_me')
                if not remember_me:
                    request.session.set_expiry(0)
                messages.success(request, f'Welcome back, {user.first_name}!')
                return redirect('claims:index')
    else:
        form = UserLoginForm()
    
    return render(request, 'auth/login.html', {'form': form})


def user_logout(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('claims:index')


@login_required
def user_profile(request):
    """User profile view"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('claims:user_profile')
    else:
        form = UserProfileForm(instance=profile)
    
    context = {
        'profile': profile,
        'form': form,
        'user': request.user,
    }
    return render(request, 'auth/profile.html', context)


@login_required
def claim_detail(request, claim_id):
    """Claim detail view with HTMX integration"""
    claim = get_object_or_404(Claim, claim_id=claim_id)
    
    # Prepare CPT codes list for display badges
    cpt_codes_list = []
    if hasattr(claim, 'details') and claim.details.exists():
        detail_obj = claim.details.first()
        if detail_obj and detail_obj.cpt_codes:
            raw = str(detail_obj.cpt_codes)
            # Split on comma or whitespace, normalize and dedupe while preserving order
            parts = [p.strip() for p in raw.replace('\n', ',').replace('\t', ',').split(',') if p.strip()]
            seen = set()
            for p in parts:
                if p not in seen:
                    seen.add(p)
                    cpt_codes_list.append(p)

    # Get user-specific notes and flags
    user_notes = claim.notes.filter(user=request.user).order_by('-created_at')
    user_flags = claim.flags.filter(user=request.user).order_by('-created_at')
    
    # Get all notes and flags for admin users
    all_notes = claim.notes.all().order_by('-created_at')
    all_flags = claim.flags.all().order_by('-created_at')
    
    context = {
        'claim': claim,
        'user_notes': user_notes,
        'user_flags': user_flags,
        'all_notes': all_notes,
        'all_flags': all_flags,
        'user': request.user,
        'note_form': NoteForm(),
        'flag_form': FlagForm(),
        'cpt_codes_list': cpt_codes_list,
    }
    
    # If this is an HTMX request, return the partial template
    if request.headers.get('HX-Request'):
        return render(request, 'partials/claim_details.html', context)
    
    return render(request, 'claim_detail.html', context)


def claim_details_partial(request, claim_id):
    """HTMX partial for claim details"""
    claim = get_object_or_404(Claim, claim_id=claim_id)
    cpt_codes_list = []
    if hasattr(claim, 'details') and claim.details.exists():
        detail_obj = claim.details.first()
        if detail_obj and detail_obj.cpt_codes:
            raw = str(detail_obj.cpt_codes)
            parts = [p.strip() for p in raw.replace('\n', ',').replace('\t', ',').split(',') if p.strip()]
            seen = set()
            for p in parts:
                if p not in seen:
                    seen.add(p)
                    cpt_codes_list.append(p)

    # Build lists according to user role
    user_notes = claim.notes.filter(user=request.user).order_by('-created_at') if request.user.is_authenticated else claim.notes.none()
    user_flags = claim.flags.filter(user=request.user).order_by('-created_at') if request.user.is_authenticated else claim.flags.none()
    all_notes = claim.notes.all().order_by('-created_at')
    all_flags = claim.flags.all().order_by('-created_at')

    context = {
        'claim': claim,
        'cpt_codes_list': cpt_codes_list,
        'user_notes': user_notes,
        'user_flags': user_flags,
        'all_notes': all_notes,
        'all_flags': all_flags,
        'user': request.user,
    }
    return render(request, 'partials/claim_details.html', context)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def flag_claim(request, claim_id):
    """Flag a claim for review"""
    claim = get_object_or_404(Claim, claim_id=claim_id)
    
    try:
        # Accept JSON or form-encoded (HTMX default)
        if request.META.get('CONTENT_TYPE', '').startswith('application/json'):
            data = json.loads(request.body or '{}')
        else:
            data = request.POST

        reason = (data.get('reason') or '').strip()
        # Resolve user: prefer current user; fallback to first superuser or any user
        current_user = request.user if request.user.is_authenticated else None
        if not current_user:
            current_user = User.objects.filter(is_superuser=True).first() or User.objects.first()
        if not current_user:
            raise ValueError('No user available to attribute this action')

        flag = Flag.objects.create(
            claim=claim,
            user=current_user,
            reason=reason
        )

        # Notify SSE listeners
        flag_payload = {
            'id': flag.id,
            'claim_id': claim.claim_id,
            'patient_name': claim.patient_name,
            'reason': flag.reason,
            'user': getattr(flag.user, 'username', flag.user_id),
            'created_at': flag.created_at.strftime('%m/%d/%Y %I:%M %p')
        }
        notify_clients('flag_added', {'flag': flag_payload})
        
        # If HTMX, return fragment HTML for immediate DOM swap
        if request.META.get('HTTP_HX_REQUEST'):
            html = render_to_string('partials/flag_item.html', {'flag': flag})
            return HttpResponse(html)
        
        # JSON fallback
        return JsonResponse({'success': True, 'message': 'Claim flagged successfully'})
        
    except Exception as e:
        if request.META.get('HTTP_HX_REQUEST'):
            return HttpResponse(f"<div class='px-4 py-2 text-sm text-red-600'>Error: {str(e)}</div>", status=400)
        return JsonResponse({'success': False, 'message': f'Error flagging claim: {str(e)}'})


@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def remove_flag(request, flag_id):
    """Remove a flag from a claim"""
    flag = get_object_or_404(Flag, id=flag_id)
    flag_id_copy = flag.id
    flag.delete()

    # Notify SSE listeners
    notify_clients('flag_removed', {'flag_id': flag_id_copy})
    
    return JsonResponse({'success': True, 'message': 'Flag removed successfully'})


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def add_note(request, claim_id):
    """Add a note to a claim"""
    claim = get_object_or_404(Claim, claim_id=claim_id)
    
    try:
        if request.META.get('CONTENT_TYPE', '').startswith('application/json'):
            data = json.loads(request.body or '{}')
        else:
            data = request.POST

        content = (data.get('content') or '').strip()
        current_user = request.user if request.user.is_authenticated else None
        if not current_user:
            current_user = User.objects.filter(is_superuser=True).first() or User.objects.first()
        if not current_user:
            raise ValueError('No user available to attribute this action')

        note = Note.objects.create(
            claim=claim,
            user=current_user,
            content=content
        )

        # Optionally notify (not consumed yet by dashboard)
        # notify_clients('note_added', {...})

        if request.META.get('HTTP_HX_REQUEST'):
            html = render_to_string('partials/note_item.html', {'note': note})
            return HttpResponse(html)
        
        return JsonResponse({'success': True, 'message': 'Note added successfully'})
        
    except Exception as e:
        if request.META.get('HTTP_HX_REQUEST'):
            return HttpResponse(f"<div class='px-4 py-2 text-sm text-red-600'>Error: {str(e)}</div>", status=400)
        return JsonResponse({'success': False, 'message': f'Error adding note: {str(e)}'})


@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def remove_note(request, note_id):
    """Remove a note from a claim"""
    note = get_object_or_404(Note, id=note_id)
    
    # Only allow users to remove their own notes or admin users
    if note.user == request.user or request.user.is_staff:
        note.delete()
        return JsonResponse({
            'success': True, 
            'message': 'Note removed successfully'
        })
    else:
        return JsonResponse({
            'success': False, 
            'message': 'You can only remove your own notes'
        }, status=403)


def admin_dashboard(request):
    """Admin dashboard with statistics"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('claims:index')
    
    total_claims = Claim.objects.count()
    flagged_claims = Flag.objects.count()
    total_billed = Claim.objects.aggregate(total=Sum('billed_amount'))['total'] or 0
    total_paid = Claim.objects.aggregate(total=Sum('paid_amount'))['total'] or 0
    average_underpayment = total_billed - total_paid
    
    # Get recent flags for real-time updates
    recent_flags = Flag.objects.select_related('claim').order_by('-created_at')[:10]
    
    stats = {
        'total_claims': total_claims,
        'flagged_claims': flagged_claims,
        'total_billed': total_billed,
        'total_paid': total_paid,
        'average_underpayment': average_underpayment,
        'recent_flags': recent_flags
    }
    
    return render(request, 'admin_dashboard.html', {'stats': stats})


def api_admin_stats(request):
    """API endpoint for admin dashboard stats with real-time updates"""
    total_claims = Claim.objects.count()
    flagged_claims = Flag.objects.count()
    total_billed = Claim.objects.aggregate(total=Sum('billed_amount'))['total'] or 0
    total_paid = Claim.objects.aggregate(total=Sum('paid_amount'))['total'] or 0
    average_underpayment = total_billed - total_paid
    
    # Get recent flags
    recent_flags = Flag.objects.select_related('claim').order_by('-created_at')[:10]
    
    flags_data = []
    for flag in recent_flags:
        flags_data.append({
            'id': flag.id,
            'claim_id': flag.claim.claim_id,
            'patient_name': flag.claim.patient_name,
            'reason': flag.reason,
            'user_id': flag.user_id,
            'created_at': flag.created_at.strftime('%m/%d/%Y %I:%M %p')
        })
    
    return JsonResponse({
        'total_claims': total_claims,
        'flagged_claims': flagged_claims,
        'total_billed': float(total_billed),
        'total_paid': float(total_paid),
        'average_underpayment': float(average_underpayment),
        'recent_flags': flags_data
    })


def api_claims(request):
    """API endpoint for claims data"""
    claims = Claim.objects.all()
    claims_data = [{
        'id': claim.claim_id,
        'patient_name': claim.patient_name,
        'billed_amount': float(claim.billed_amount),
        'paid_amount': float(claim.paid_amount),
        'status': claim.status,
        'insurer_name': claim.insurer_name,
        'discharge_date': claim.discharge_date.strftime('%Y-%m-%d') if claim.discharge_date else None
    } for claim in claims]
    
    return JsonResponse(claims_data, safe=False)


@login_required
def export_claims_json(request):
    """Export claims data as JSON"""
    claims = Claim.objects.all()
    claims_data = []
    
    for claim in claims:
        claim_data = {
            'id': claim.claim_id,
            'patient_name': claim.patient_name,
            'billed_amount': float(claim.billed_amount),
            'paid_amount': float(claim.paid_amount),
            'status': claim.status,
            'insurer_name': claim.insurer_name,
            'discharge_date': claim.discharge_date.strftime('%Y-%m-%d') if claim.discharge_date else None
        }
        
        # Add claim details if available
        if hasattr(claim, 'details') and claim.details.exists():
            detail = claim.details.first()
            claim_data['cpt_codes'] = detail.cpt_codes if detail.cpt_codes else None
            claim_data['denial_reason'] = detail.denial_reason if detail.denial_reason else None
        
        claims_data.append(claim_data)
    
    response = HttpResponse(
        json.dumps(claims_data, indent=2),
        content_type='application/json'
    )
    response['Content-Disposition'] = 'attachment; filename=claim_list_data.json'
    return response


@login_required
def export_claims_csv(request):
    """Export claims data as CSV"""
    import csv
    
    claims = Claim.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=claim_list_data.csv'
    
    writer = csv.writer(response, delimiter='|')
    
    # Write header
    writer.writerow(['id', 'patient_name', 'billed_amount', 'paid_amount', 'status', 'insurer_name', 'discharge_date'])
    
    # Write data
    for claim in claims:
        writer.writerow([
            claim.claim_id,
            claim.patient_name,
            claim.billed_amount,
            claim.paid_amount,
            claim.status,
            claim.insurer_name,
            claim.discharge_date.strftime('%Y-%m-%d') if claim.discharge_date else ''
        ])
    
    return response
