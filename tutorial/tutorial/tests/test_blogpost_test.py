from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from quickstart.models.blog_models import BlogModel
from quickstart.models.authentication_models import User_Data

User = get_user_model()

class BlogPostTest(APITestCase):
    def setUp(self):
        self.writer = User.objects.create_user(username='writer', password='testpass123')
        self.viewer = User.objects.create_user(username='viewer', password='testpass456')

        User_Data.objects.create(user=self.writer, role='writer')
        User_Data.objects.create(user=self.viewer, role='viewer')

        self.writer_token = str(AccessToken.for_user(self.writer))
        self.viewer_token = str(AccessToken.for_user(self.viewer))

        self.url = '/api/blog/'

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_writer_can_create_blog_with_valid_fields(self):
        self.authenticate(self.writer)
        data = {'title': 'Test Blog', 'content': 'Some content'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Blog Post Successfully Created')
        self.assertEqual(BlogModel.objects.count(), 1)

    def test_writer_cannot_create_blog_with_extra_fields(self):
        self.authenticate(self.writer)
        data = {'title': 'Test Blog', 'content': 'Some content', 'extra': 'invalid'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Only title and content are allowed.')

    def test_non_writer_cannot_create_blog(self):
        self.authenticate(self.viewer)
        data = {'title': 'Viewer Blog', 'content': 'Should not be allowed'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Only Writers are allowed to post')

    def test_writer_can_fetch_blogs(self):
        BlogModel.objects.create(user=self.writer, title='Sample', content='Content')
        self.authenticate(self.writer)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Blog Post Successfully Fetched')
        self.assertTrue(len(response.json()['data']) >= 1)

    def test_viewer_can_fetch_blogs(self):
        BlogModel.objects.create(user=self.writer, title='Sample', content='Content')
        self.authenticate(self.viewer)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Blog Post Successfully Fetched')
        self.assertTrue(len(response.json()['data']) >= 1)

    def test_method_not_allowed(self):
        self.authenticate(self.writer)
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'No other Methods Allowed')