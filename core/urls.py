from django.urls import path
from . import views
from .views import hello_world

app_name = 'core'

urlpatterns = [
    path('', hello_world),
    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('how-it-works/', views.how_it_works, name='how_it_works'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
    path('terms/', views.terms_of_service, name='terms_of_service'),
]
