from django.urls import path
from . import views

app_name = 'claims'

urlpatterns = [
    path('', views.index, name='index'),
    path('claim/<str:claim_id>/', views.claim_detail, name='claim_detail'),
    path('claim/<str:claim_id>/details/', views.claim_details_partial, name='claim_details_partial'),
    path('claim/<str:claim_id>/flag/', views.flag_claim, name='flag_claim'),
    path('flag/<int:flag_id>/remove/', views.remove_flag, name='remove_flag'),
    path('claim/<str:claim_id>/note/', views.add_note, name='add_note'),
    path('note/<int:note_id>/remove/', views.remove_note, name='remove_note'),

    # APIs/exports (public)
    # path('api/admin/stats/', views.api_admin_stats, name='api_admin_stats'),  # dashboard removed
    path('api/claims/', views.api_claims, name='api_claims'),
    path('export/claims/json/', views.export_claims_json, name='export_claims_json'),
    path('export/claims/csv/', views.export_claims_csv, name='export_claims_csv'),

    # Auth and profile
    path('auth/register/', views.user_register, name='user_register'),
    path('auth/login/', views.user_login, name='user_login'),
    path('auth/logout/', views.user_logout, name='user_logout'),
    # path('auth/profile/', views.user_profile, name='user_profile'),  # profile removed

    # SSE events for live updates
    path('events', views.admin_events, name='events'),

    # Dashboard removed

]
