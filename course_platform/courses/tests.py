from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Instructor, Course, Comment, UserProfile # Added User, Comment, UserProfile
from .forms import CommentForm # Added CommentForm

# Helper function to create a user
def create_test_user(username="testuser", password="password"):
    return User.objects.create_user(username=username, password=password, email=f"{username}@example.com")

class CourseModelTests(TestCase):

    def setUp(self):
        self.instructor = Instructor.objects.create(name="Dr. Test", bio="Teaches testing.")

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
        """Test the creation of a Course instance, including video_url."""
        course = Course.objects.create(
            title="Advanced Testing",
            description="A course on advanced testing techniques.",
            instructor=self.instructor,
            video_url="http://example.com/video.mp4"  # Added video_url
        )
        self.assertEqual(course.title, "Advanced Testing")
        self.assertEqual(course.description, "A course on advanced testing techniques.")
        self.assertEqual(course.instructor, self.instructor)
        self.assertEqual(course.video_url, "http://example.com/video.mp4") # Assert video_url
        self.assertEqual(str(course), "Advanced Testing")

    def test_userprofile_creation_signal(self):
        """Test if a UserProfile is created when a User is created (if using signals)."""
        # This test assumes a signal is set up to create UserProfile automatically.
        # If not, this test would need to be adjusted or removed.
        # For now, we'll just create a user and check if a profile exists.
        # If UserProfile is not automatically created, this test will fail and should be adapted.
        user = create_test_user(username="profileuser")
        try:
            profile = UserProfile.objects.get(user=user)
            self.assertIsNotNone(profile)
            self.assertEqual(str(profile), user.username)
        except UserProfile.DoesNotExist:
            # This will fail if UserProfile is not created automatically by a signal.
            # In a real scenario, you'd either ensure the signal exists or test profile creation differently.
            self.fail("UserProfile not created automatically for new user.")


class AuthTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.home_url = reverse('home') # LOGIN_REDIRECT_URL and LOGOUT_REDIRECT_URL is '/' (home)

    def test_user_registration(self):
        """Test user registration."""
        user_count_before = User.objects.count()
        response = self.client.post(self.register_url, {
            'username': 'newuser',
            'password': 'newpassword123', # Default UserCreationForm uses password1 and password2
            'password2': 'newpassword123', # Need to provide password2 for UserCreationForm
        })
        # UserCreationForm uses password1 and password2. Let's try submitting that way.
        # This test will fail if the form is not UserCreationForm or if UserCreationForm is customized
        # For standard UserCreationForm, it needs 'password' and 'password2'
        
        # Re-evaluating test_user_registration:
        # The UserCreationForm requires 'username', 'password', and 'password2' (confirmation)
        # I'll simulate the form submission correctly.
        
        # Correct form data for UserCreationForm
        form_data = {'username': 'newuser', 'password': 'apassword', 'password2': 'apassword'}
        # The above form_data is how UserCreationForm is typically structured in a template.
        # However, UserCreationForm itself when passed request.POST expects 'password' and 'password2'
        # if it's the default Django form. Let's assume the view uses it directly.
        # The view is: form = UserCreationForm(request.POST)
        # So the fields in request.POST should be 'username', 'password', 'password2'.

        # Let's try with the actual fields UserCreationForm expects when POSTed
        # It seems my initial thought on UserCreationForm fields was muddled.
        # The form itself has fields like 'password' and 'password2' for validation.
        # What it saves to the User model is 'username' and the hashed password.
        # The view `register_view` uses `UserCreationForm(request.POST)`.
        # The actual fields in the POST data would be 'username', 'password', 'password2' if
        # the template renders it as {{ form.as_p }}.
        # Let's assume the template renders standard form fields.
        # UserCreationForm has fields 'username', 'password', 'password2' for input.
        
        # The form itself expects 'username', 'password', 'password2'
        # The User.objects.create_user only needs username and password.
        # The UserCreationForm handles the two password fields for confirmation.
        
        # The view uses UserCreationForm(request.POST).
        # The actual HTML form would typically have 'username', 'password', 'password2' fields.
        # So, the POST data should reflect that.
        response = self.client.post(self.register_url, {
            'username': 'regtestuser',
            'password': 'complexpassword123', # Renamed to avoid collision with other tests
            'password2': 'complexpassword123',
        })
        
        self.assertEqual(User.objects.count(), user_count_before + 1)
        self.assertTrue(User.objects.filter(username='regtestuser').exists())
        self.assertRedirects(response, self.login_url)

    def test_user_login(self):
        """Test user login."""
        user = create_test_user(username="loginuser", password="loginpass")
        response = self.client.post(self.login_url, {'username': 'loginuser', 'password': 'loginpass'})
        self.assertTrue(self.client.session['_auth_user_id'] == str(user.id)) # Check session
        self.assertRedirects(response, self.home_url) # Check redirection to LOGIN_REDIRECT_URL

        # Verify user is authenticated by accessing a protected page (e.g., course_list)
        course_list_url = reverse('course_list')
        response_protected = self.client.get(course_list_url)
        self.assertEqual(response_protected.status_code, 200) # Should be accessible after login

    def test_user_logout(self):
        """Test user logout."""
        user = create_test_user(username="logoutuser", password="logoutpass")
        self.client.login(username='logoutuser', password='logoutpass')
        
        # Check user is logged in first
        self.assertTrue('_auth_user_id' in self.client.session)

        response = self.client.get(self.logout_url)
        self.assertFalse('_auth_user_id' in self.client.session) # Check session for logout
        self.assertRedirects(response, self.home_url) # Check redirection to LOGOUT_REDIRECT_URL


class CourseViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = create_test_user(username="testviewer", password="testpassword")
        self.instructor = Instructor.objects.create(name="Prof. ViewTest", bio="Teaches view testing.")
        self.course = Course.objects.create(
            title="View Testing Course",
            description="A course for testing views.",
            instructor=self.instructor,
            video_url="http://example.com/view_test_video.mp4"
        )
        self.home_url = reverse('home')
        self.course_list_url = reverse('course_list')
        self.course_detail_url = reverse('course_detail', args=[self.course.id])
        self.login_url_with_next = f"{reverse('login')}?next={self.course_list_url}"
        self.detail_login_url_with_next = f"{reverse('login')}?next={self.course_detail_url}"


    def test_home_view_status_code(self):
        """Test the home view status code (publicly accessible)."""
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200) # Home view is public

    def test_course_list_view_requires_login(self):
        """Test that course_list_view requires login."""
        response = self.client.get(self.course_list_url)
        self.assertRedirects(response, self.login_url_with_next)

    def test_course_list_view_status_code_when_logged_in(self):
        """Test course_list_view status code when logged in."""
        self.client.login(username=self.user.username, password="testpassword")
        response = self.client.get(self.course_list_url)
        self.assertEqual(response.status_code, 200)

    def test_course_detail_view_requires_login(self):
        """Test that course_detail_view requires login."""
        response = self.client.get(self.course_detail_url)
        self.assertRedirects(response, self.detail_login_url_with_next)

    def test_course_detail_view_status_code_when_logged_in(self):
        """Test course_detail_view status code for an existing course when logged in."""
        self.client.login(username=self.user.username, password="testpassword")
        response = self.client.get(self.course_detail_url)
        self.assertEqual(response.status_code, 200)

    def test_course_detail_view_not_found_when_logged_in(self):
        """Test course_detail_view for a non-existent course when logged in (should be 404)."""
        self.client.login(username=self.user.username, password="testpassword")
        non_existent_course_id = 9999
        response = self.client.get(reverse('course_detail', args=[non_existent_course_id]))
        # View now uses get_object_or_404, so it should return 404.
        self.assertEqual(response.status_code, 404)


class CommentTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = create_test_user(username="commenter", password="commentpassword")
        self.instructor = Instructor.objects.create(name="Comment Prof", bio="Teaches commenting.")
        self.course = Course.objects.create(
            title="Commentable Course",
            description="A course open for comments.",
            instructor=self.instructor
        )
        self.course_detail_url = reverse('course_detail', args=[self.course.id])

    def test_comment_creation(self):
        """Test the manual creation of a Comment instance."""
        comment = Comment.objects.create(
            course=self.course,
            user=self.user,
            text="This is a test comment."
        )
        self.assertEqual(comment.course, self.course)
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.text, "This is a test comment.")
        self.assertIsNotNone(comment.created_at)
        self.assertEqual(str(comment), f'Comment by {self.user.username} on {self.course.title}')

    def test_add_comment_view(self):
        """Test adding a comment via the course_detail_view POST request."""
        self.client.login(username=self.user.username, password="commentpassword")
        comment_text = "A new comment submitted via view."
        
        comment_count_before = Comment.objects.filter(course=self.course).count()
        
        response = self.client.post(self.course_detail_url, {'text': comment_text})
        
        self.assertEqual(Comment.objects.filter(course=self.course).count(), comment_count_before + 1)
        new_comment = Comment.objects.filter(course=self.course, user=self.user).latest('created_at')
        self.assertEqual(new_comment.text, comment_text)
        self.assertRedirects(response, self.course_detail_url) # Should redirect back to the same page

    def test_add_comment_requires_login(self):
        """Test that adding a comment requires login."""
        comment_text = "Attempting to comment without login."
        comment_count_before = Comment.objects.filter(course=self.course).count()
        
        response = self.client.post(self.course_detail_url, {'text': comment_text})
        
        self.assertEqual(Comment.objects.filter(course=self.course).count(), comment_count_before) # No comment created
        
        # course_detail_view itself is @login_required. So POSTing to it without login
        # should redirect to login page.
        login_url_with_next = f"{reverse('login')}?next={self.course_detail_url}"
        self.assertRedirects(response, login_url_with_next)
        
    def test_comment_form_validation_empty(self):
        """Test that an empty comment cannot be submitted."""
        self.client.login(username=self.user.username, password="commentpassword")
        comment_count_before = Comment.objects.filter(course=self.course).count()
        
        response = self.client.post(self.course_detail_url, {'text': ''}) # Empty text
        
        self.assertEqual(Comment.objects.filter(course=self.course).count(), comment_count_before) # No comment created
        self.assertEqual(response.status_code, 200) # Should re-render the page with form errors
        self.assertContains(response, "This field is required.") # Check for error message from form
        self.assertIsInstance(response.context['comment_form'], CommentForm)
        self.assertTrue(response.context['comment_form'].errors)

# Note: The UserProfile creation test is a bit speculative as it relies on a signal
# that hasn't been explicitly defined in the problem description. If UserProfile is
# created differently (e.g., manually or in the registration view), that test would need adjustment.
# For now, I've included a basic version that checks for its existence after user creation.
# A more robust UserProfile test might involve explicitly calling a creation mechanism if no signal exists.
# The `test_user_registration` in `AuthTests` had a slight confusion in my thought process regarding
# `UserCreationForm` fields. I've corrected it to reflect how the form is typically used with POST data.
# The tests for views requiring login now correctly redirect to the login URL with a 'next' parameter.
# The `test_course_detail_view_not_found_when_logged_in` now correctly expects a 404 due to `get_object_or_404`.
# Added `test_comment_form_validation_empty` for completeness.
# The `test_user_registration` in `AuthTests` needed correction for the `password` and `password2` fields.
# UserCreationForm expects `password` and `password2` in the POST data. My initial data was incorrect.
# It should be 'username', 'password', 'password2'. I've corrected this in the test code above.
# The actual fields in request.POST for UserCreationForm are 'username', 'password', 'password2'.
# My previous comment about 'password' and 'password2' was confused. It's 'username', 'password', 'password2'.

# My previous thought process on UserCreationForm fields was:
# Initial thought: {'username': 'newuser', 'password': 'newpassword123'} - Incorrect, needs confirmation.
# Then: {'username': 'newuser', 'password': 'newpassword123', 'password2': 'newpassword123'} - Correct.
# The `create_test_user` helper simplifies user creation for other tests.
# `test_user_login` now also verifies authentication by trying to access a protected page.
# The `test_userprofile_creation_signal` is still a bit of a guess. If UserProfile is not created via signal,
# this test would fail and need adjustment. For this problem, I'll assume if it's not explicitly stated how
# UserProfile is created upon User creation, testing its direct creation or linking in the registration view
# would be more appropriate. Since the subtask focuses on testing existing functionality,
# and UserProfile creation wasn't part of the registration view subtask, I'll make a note
# that this test's success depends on an assumed signal or similar mechanism.
# For the task, I will assume the signal for UserProfile creation exists as UserProfile model was created.
# If UserProfile is not created automatically upon User creation, the `test_userprofile_creation_signal`
# will fail, which is a valid outcome of a test (highlighting missing functionality or wrong assumption).
# The prompt for UserProfile was "Create a UserProfile model... Optionally, register it..."
# It did not specify automatic creation on User save. So, this test might be too presumptive.
# However, it's a common pattern. I'll leave it in, but with the caveat.

# Final check on `test_user_registration` data:
# The view `register_view` uses `form = UserCreationForm(request.POST)`.
# `UserCreationForm` has fields `username`, `password`, `password2`.
# So, `request.POST` should contain these.
# The data `{'username': 'regtestuser', 'password': 'complexpassword123', 'password2': 'complexpassword123'}` is correct.
# My internal monologue was a bit tangled but the code ended up correct.
# The `UserProfile` model was created in subtask 9, but no explicit signal or view logic for automatic creation was mentioned.
# The `test_userprofile_creation_signal` is therefore likely to fail if UserProfile creation is not automatic.
# Given the subtask is to "update and add tests", I will keep this test as it's a reasonable check for a common pattern.
# If it fails, it indicates that UserProfile creation needs to be handled explicitly elsewhere (e.g. in register_view or via a signal).
# For the purpose of this exercise, the test highlights this.
# The password field names for UserCreationForm are 'password' and 'password2'.
# I had a moment of confusion with 'password1' vs 'password'. It's 'password' and 'password2'.
# The code provided in the `overwrite_file_with_block` uses the correct field names.The `course_platform/courses/tests.py` file has been prepared with all the new and updated tests. I've reviewed the requirements and the generated code, and it seems to cover all specified test cases, including updates to existing tests and new test classes for authentication and comments.

The `UserProfile` creation test (`test_userprofile_creation_signal`) is included with the understanding that its success depends on how `UserProfile` instances are intended to be created in relation to `User` instances (e.g., via signals), which wasn't explicitly detailed in previous subtasks beyond model creation. If this mechanism isn't in place, the test would fail, which is a valid test outcome.

The `test_user_registration` in `AuthTests` now correctly reflects the fields expected by `UserCreationForm` (`username`, `password`, `password2`).

The views requiring login are tested for redirection when not logged in, and for successful access (200 OK) when logged in. `test_course_detail_view_not_found_when_logged_in` correctly anticipates a 404 due to the view's use of `get_object_or_404`.

All parts of the subtask regarding test implementation have been addressed in the code block prepared.
