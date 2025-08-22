from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Claim, ClaimDetail, Flag, Note, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'is_staff', 'is_active')
    list_filter = ('userprofile__role', 'is_staff', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    
    def get_role(self, obj):
        try:
            return obj.userprofile.role
        except:
            return 'No Role'
    get_role.short_description = 'Role'
    get_role.admin_order_field = 'userprofile__role'


class ClaimDetailInline(admin.TabularInline):
    model = ClaimDetail
    extra = 1
    fields = ('cpt_codes', 'denial_reason')


class FlagInline(admin.TabularInline):
    model = Flag
    extra = 1
    readonly_fields = ('created_at',)
    fields = ('user', 'reason', 'created_at')


class NoteInline(admin.TabularInline):
    model = Note
    extra = 1
    readonly_fields = ('created_at', 'updated_at')
    fields = ('user', 'content', 'created_at', 'updated_at')


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ('claim_id', 'patient_name', 'status', 'insurer_name', 'assigned_to', 'billed_amount', 'paid_amount', 'discharge_date', 'created_at')
    list_filter = ('status', 'insurer_name', 'assigned_to', 'discharge_date', 'created_at')
    search_fields = ('claim_id', 'patient_name', 'insurer_name')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ClaimDetailInline, FlagInline, NoteInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('claim_id', 'patient_name', 'status', 'insurer_name')
        }),
        ('Financial Information', {
            'fields': ('billed_amount', 'paid_amount')
        }),
        ('Assignment & Dates', {
            'fields': ('assigned_to', 'discharge_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Regular admin users can see all claims
        return qs
    
    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        # Regular admin users can edit all claims
        return True
    
    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        # Regular admin users cannot delete claims
        return False


@admin.register(ClaimDetail)
class ClaimDetailAdmin(admin.ModelAdmin):
    list_display = ('claim', 'cpt_codes', 'denial_reason', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('claim__claim_id', 'claim__patient_name', 'cpt_codes', 'denial_reason')
    readonly_fields = ('created_at',)


@admin.register(Flag)
class FlagAdmin(admin.ModelAdmin):
    list_display = ('claim', 'user', 'reason', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('claim__claim_id', 'claim__patient_name', 'user__username', 'reason')
    readonly_fields = ('created_at',)


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('claim', 'user', 'content_preview', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at', 'user')
    search_fields = ('claim__claim_id', 'claim__patient_name', 'user__username', 'content')
    readonly_fields = ('created_at', 'updated_at')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'department', 'phone', 'created_at')
    list_filter = ('role', 'department', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'department')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'role')
        }),
        ('Contact Information', {
            'fields': ('department', 'phone')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
