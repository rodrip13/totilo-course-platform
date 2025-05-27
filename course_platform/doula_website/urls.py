from django.urls import path
from . import views

app_name = 'doula_website'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('plans/', views.service_plans_view, name='service_plans'),
    path('contact/', views.contact_view, name='contact'),
]
