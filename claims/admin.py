from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Claim, ClaimDetail, Flag, Note, UserProfile


class UserProfileInline(admin.StackedInline):
    """Inline admin for UserProfile"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'


class UserAdmin(BaseUserAdmin):
    """Custom User admin with profile inline"""
    inlines = (UserProfileInline,)


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ['claim_id', 'patient_name', 'insurer_name', 'status', 'billed_amount', 'paid_amount', 'discharge_date', 'created_at']
    list_filter = ['status', 'insurer_name', 'created_at', 'discharge_date']
    search_fields = ['claim_id', 'patient_name', 'insurer_name']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 25
    
    fieldsets = (
        ('Claim Information', {
            'fields': ('claim_id', 'patient_name', 'insurer_name', 'status')
        }),
        ('Financial Details', {
            'fields': ('billed_amount', 'paid_amount')
        }),
        ('Dates', {
            'fields': ('discharge_date', 'created_at', 'updated_at')
        }),
    )


@admin.register(ClaimDetail)
class ClaimDetailAdmin(admin.ModelAdmin):
    list_display = ['id', 'claim', 'cpt_codes', 'denial_reason', 'created_at']
    list_filter = ['created_at']
    search_fields = ['claim__claim_id', 'claim__patient_name']
    readonly_fields = ['created_at']


@admin.register(Flag)
class FlagAdmin(admin.ModelAdmin):
    list_display = ['id', 'claim', 'user', 'reason', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['claim__claim_id', 'claim__patient_name', 'reason']
    readonly_fields = ['created_at']


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['id', 'claim', 'user', 'content_preview', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['claim__claim_id', 'claim__patient_name', 'content']
    readonly_fields = ['created_at', 'updated_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'department', 'phone', 'created_at']
    list_filter = ['department', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'department']
    readonly_fields = ['created_at']


# Re-register User admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
