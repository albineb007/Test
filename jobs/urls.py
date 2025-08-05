from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    # Job listing and details
    path('', views.job_list, name='job_list'),
    path('job/<int:pk>/', views.job_detail, name='job_detail'),
    path('job/<int:pk>/track-contact/', views.track_contact_click, name='track_contact_click'),
    path('save/<int:pk>/', views.toggle_save_job, name='toggle_save_job'),
    
    # Job management
    path('post/', views.job_create, name='job_create'),
    path('job/<int:pk>/edit/', views.job_update, name='job_update'),
    path('job/<int:pk>/delete/', views.job_delete, name='job_delete'),
    
    # Applications
    path('job/<int:pk>/apply/', views.job_apply, name='job_apply'),
    path('applications/', views.my_applications, name='my_applications'),
    path('job/<int:pk>/manage-applications/', views.job_applications_manage, name='manage_applications'),
    path('application/<int:pk>/<str:action>/', views.application_action, name='application_action'),
    path('job/<int:pk>/bulk-action/', views.bulk_application_action, name='bulk_application_action'),
    
    # Reviews
    path('job/<int:job_id>/review/<int:user_id>/', views.leave_review, name='leave_review'),
    path('job/<int:job_id>/quick-review/<int:user_id>/', views.quick_review, name='quick_review'),
    path('reviews/<int:user_id>/', views.user_reviews, name='user_reviews'),
    path('review/<int:pk>/', views.ReviewDetailView.as_view(), name='review_detail'),
    path('review/<int:review_id>/helpful/', views.mark_review_helpful, name='mark_review_helpful'),
    path('review/<int:review_id>/report/', views.report_review, name='report_review'),
    
    # Dashboards (now using different view names)
    path('volunteer-dashboard/', views.volunteer_dashboard, name='volunteer_dashboard'),
    path('poster-dashboard/', views.poster_dashboard, name='poster_dashboard'),
]
