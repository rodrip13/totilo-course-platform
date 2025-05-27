from django.urls import path
from . import views

app_name = 'courses' # Add this line

urlpatterns = [
    path('', views.home_view, name='home'),
    path('courses/', views.course_list_view, name='course_list'),
    path('courses/<int:course_id>/', views.course_detail_view, name='course_detail'),
    path('register/', views.register_view, name='register'), # Added registration URL
]
