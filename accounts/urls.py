from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('role-selection/', views.role_selection, name='role_selection'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/update/', views.ProfileUpdateView.as_view(), name='profile_update'),
    path('verify/phone/', views.phone_verification, name='phone_verification'),
    path('verify/documents/', views.document_verification, name='document_verification'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('volunteer-dashboard/', views.volunteer_dashboard, name='volunteer_dashboard'),
    path('poster-dashboard/', views.poster_dashboard, name='poster_dashboard'),
]
