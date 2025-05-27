from django.shortcuts import render
from .models import Instructor, Course

def home_view(request):
    instructor = None
    try:
        instructor = Instructor.objects.first()
    except Instructor.DoesNotExist:
        pass # instructor remains None
    return render(request, 'courses/home.html', {'instructor': instructor})

def course_list_view(request):
    courses = Course.objects.all()
    return render(request, 'courses/course_list.html', {'courses': courses})

def course_detail_view(request, course_id):
    course = None
    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        pass # course remains None
    return render(request, 'courses/course_detail.html', {'course': course})
