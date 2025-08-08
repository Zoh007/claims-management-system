from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app.models import Claim, ClaimDetail, Flag, Note
from app import db
from datetime import datetime
import json

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Main claims list view with robustness features"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Search and filter functionality
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    insurer_filter = request.args.get('insurer', '')
    
    query = Claim.query
    
    if search:
        query = query.filter(
            db.or_(
                Claim.patient_name.contains(search),
                Claim.claim_id.contains(search),
                Claim.insurer_name.contains(search)
            )
        )
    
    if status_filter:
        query = query.filter(Claim.status == status_filter)
    
    if insurer_filter:
        query = query.filter(Claim.insurer_name == insurer_filter)
    
    claims = query.order_by(Claim.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Get unique statuses and insurers for filter dropdowns
    statuses = db.session.query(Claim.status).distinct().all()
    insurers = db.session.query(Claim.insurer_name).distinct().all()
    
    return render_template('index.html', 
                         claims=claims, 
                         search=search,
                         status_filter=status_filter,
                         insurer_filter=insurer_filter,
                         statuses=[s[0] for s in statuses],
                         insurers=[i[0] for i in insurers])

@main_bp.route('/claim/<claim_id>')
def claim_detail(claim_id):
    """Claim detail view with HTMX integration for robustness"""
    claim = Claim.query.filter_by(claim_id=claim_id).first_or_404()
    return render_template('claim_detail.html', claim=claim)

@main_bp.route('/claim/<claim_id>/details')
def claim_details_partial(claim_id):
    """HTMX partial for claim details with robustness features"""
    claim = Claim.query.filter_by(claim_id=claim_id).first_or_404()
    return render_template('partials/claim_details.html', claim=claim)

@main_bp.route('/claim/<claim_id>/flag', methods=['POST'])
def flag_claim(claim_id):
    """Flag a claim for review with robustness features"""
    claim = Claim.query.filter_by(claim_id=claim_id).first_or_404()
    
    data = request.get_json()
    reason = data.get('reason', '')
    user_id = data.get('user_id', 'admin')  # Simple user identification
    
    flag = Flag(
        claim_id=claim.id,
        user_id=user_id,
        reason=reason
    )
    
    db.session.add(flag)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Claim flagged successfully'})

@main_bp.route('/claim/<claim_id>/note', methods=['POST'])
def add_note(claim_id):
    """Add a note to a claim with robustness features"""
    claim = Claim.query.filter_by(claim_id=claim_id).first_or_404()
    
    data = request.get_json()
    content = data.get('content', '')
    user_id = data.get('user_id', 'admin')
    
    note = Note(
        claim_id=claim.id,
        user_id=user_id,
        content=content
    )
    
    db.session.add(note)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Note added successfully'})

@main_bp.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard with statistics for robustness analysis"""
    total_claims = Claim.query.count()
    flagged_claims = Flag.query.count()
    total_billed = db.session.query(db.func.sum(Claim.billed_amount)).scalar() or 0
    total_paid = db.session.query(db.func.sum(Claim.paid_amount)).scalar() or 0
    average_underpayment = total_billed - total_paid
    
    stats = {
        'total_claims': total_claims,
        'flagged_claims': flagged_claims,
        'total_billed': total_billed,
        'total_paid': total_paid,
        'average_underpayment': average_underpayment
    }
    
    return render_template('admin_dashboard.html', stats=stats)

@main_bp.route('/api/claims')
def api_claims():
    """API endpoint for claims data with robustness features"""
    claims = Claim.query.all()
    return jsonify([{
        'id': claim.claim_id,
        'patient_name': claim.patient_name,
        'billed_amount': claim.billed_amount,
        'paid_amount': claim.paid_amount,
        'status': claim.status,
        'insurer_name': claim.insurer_name,
        'discharge_date': claim.discharge_date.strftime('%Y-%m-%d') if claim.discharge_date else None
    } for claim in claims])
