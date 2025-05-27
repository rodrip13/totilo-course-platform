from django.test import TestCase, Client
from django.urls import reverse
from .models import Instructor, Course

class CourseModelTests(TestCase):

    def test_instructor_creation(self):
        """Test the creation of an Instructor instance."""
        instructor = Instructor.objects.create(
            name="John Doe",
            bio="A passionate instructor."
        )
        self.assertEqual(instructor.name, "John Doe")
        self.assertEqual(instructor.bio, "A passionate instructor.")
        self.assertEqual(str(instructor), "John Doe")

    def test_course_creation(self):
        """Test the creation of a Course instance."""
        instructor = Instructor.objects.create(
            name="Jane Smith",
            bio="Loves teaching."
        )
        course = Course.objects.create(
            title="Introduction to Django",
            description="A beginner-friendly course on Django.",
            instructor=instructor
        )
        self.assertEqual(course.title, "Introduction to Django")
        self.assertEqual(course.description, "A beginner-friendly course on Django.")
        self.assertEqual(course.instructor, instructor)
        self.assertEqual(str(course), "Introduction to Django")


class CourseViewTests(TestCase):

    def setUp(self):
        """Set up common test resources."""
        self.client = Client()
        self.instructor = Instructor.objects.create(
            name="Test Instructor",
            bio="Bio for Test Instructor."
        )
        self.course = Course.objects.create(
            title="Test Course",
            description="Description for Test Course.",
            instructor=self.instructor
        )

    def test_home_view_status_code(self):
        """Test the home view status code."""
        # An instructor should exist for the home view to render correctly as per its logic
        if not Instructor.objects.exists():
             Instructor.objects.create(name="Default Instructor", bio="Default Bio")
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_course_list_view_status_code(self):
        """Test the course list view status code."""
        response = self.client.get(reverse('course_list'))
        self.assertEqual(response.status_code, 200)

    def test_course_detail_view_status_code(self):
        """Test the course detail view status code for an existing course."""
        response = self.client.get(reverse('course_detail', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)

    def test_course_detail_view_not_found(self):
        """Test the course detail view for a non-existent course."""
        non_existent_course_id = 999
        response = self.client.get(reverse('course_detail', args=[non_existent_course_id]))
        # The view itself handles DoesNotExist and returns a template with context,
        # which results in a 200 OK, not a 404, unless explicitly raised.
        # For a true 404, the view would need to raise Http404.
        # Current view logic:
        # try: course = Course.objects.get(pk=course_id)
        # except Course.DoesNotExist: pass # course remains None
        # return render(request, 'courses/course_detail.html', {'course': course})
        # This will render the template with course=None, resulting in 200.
        # To test the "not found" *template content*, one would inspect response.content.
        # However, the requirement is to check status code 404.
        # To meet this, the view needs to be changed.
        # For now, I will assert 200 as per current view behavior.
        # If a strict 404 is desired, the view logic for course_detail_view needs modification.
        # Given the prompt asks to *assert* 404, I will assume the view *should* return 404.
        # I will write the test expecting 404, and if it fails, it indicates a mismatch
        # between test expectation and view implementation.
        
        # Re-evaluating: The prompt is to *test* for 404. If the view doesn't currently
        # return 404, the test *should* fail, highlighting this.
        # The view *should* ideally return a 404 if the object is not found.
        # Django's get_object_or_404 is typically used for this.
        # Since the view currently doesn't do that, this test will fail.
        # This is a valid test case.
        self.assertEqual(response.status_code, 404)
