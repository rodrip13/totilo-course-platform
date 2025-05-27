from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse
from .models import Instructor, Course, Comment
from .forms import CommentForm

def home_view(request):
    instructor = None
    try:
        instructor = Instructor.objects.first()
    except Instructor.DoesNotExist:
        pass # instructor remains None
    return render(request, 'courses/home.html', {'instructor': instructor})

@login_required
def course_list_view(request):
    courses = Course.objects.all()
    return render(request, 'courses/course_list.html', {'courses': courses})

@login_required
def course_detail_view(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    comments = course.comments.all().order_by('-created_at') # Fetch comments

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.course = course
            new_comment.user = request.user
            new_comment.save()
            return redirect('course_detail', course_id=course.id) # Redirect to clear POST
    else:
        comment_form = CommentForm() # Empty form for GET

    context = {
        'course': course,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'courses/course_detail.html', context)

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # Optional: messages.success(request, 'Registration successful. Please log in.')
            return redirect(reverse('login'))
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
