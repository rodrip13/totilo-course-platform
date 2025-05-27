from django.contrib import admin
from .models import Instructor, Course, UserProfile, Comment # Added Comment

# Register your models here.
admin.site.register(Instructor)
admin.site.register(Course)
admin.site.register(UserProfile)
admin.site.register(Comment) # Registered Comment
