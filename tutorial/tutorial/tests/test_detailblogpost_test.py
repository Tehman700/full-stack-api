from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from quickstart.models.blog_models import BlogModel
from quickstart.models.authentication_models import User_Data

User = get_user_model()

class DetailBlogPostTest(APITestCase):
    def setUp(self):
        self.writer1 = User.objects.create_user(username='writer1', password='testpass123')
        self.writer2 = User.objects.create_user(username='writer2', password='testpass456')
        self.viewer = User.objects.create_user(username='viewer', password='testpass789')

        User_Data.objects.create(user=self.writer1, role='writer')
        User_Data.objects.create(user=self.writer2, role='writer')
        User_Data.objects.create(user=self.viewer, role='viewer')

        self.blog1 = BlogModel.objects.create(user=self.writer1, title='Writer1 Blog', content='Content by writer1')
        self.blog2 = BlogModel.objects.create(user=self.writer2, title='Writer2 Blog', content='Content by writer2')

        self.url = '/api/blog/'

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_writer_can_view_blog_by_id(self):
        self.authenticate(self.writer1)
        response = self.client.get(f'{self.url}{self.blog1.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Blog Post Successfully Fetched')
        self.assertEqual(response.json()['data']['title'], 'Writer1 Blog')

    def test_viewer_can_view_blog_by_id(self):
        self.authenticate(self.viewer)
        response = self.client.get(f'{self.url}{self.blog1.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Blog Post Successfully Fetched')
        self.assertEqual(response.json()['data']['title'], 'Writer1 Blog')

    def test_blog_not_found(self):
        self.authenticate(self.writer1)
        response = self.client.get(f'{self.url}999/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Blog not found')

    def test_writer_can_update_own_blog(self):
        self.authenticate(self.writer1)
        data = {'title': 'Updated Title', 'content': 'Updated Content'}
        response = self.client.put(f'{self.url}{self.blog1.id}/', data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'You have changed the blog')
        self.assertEqual(response.json()['data']['title'], 'Updated Title')

    def test_writer_cannot_update_other_writer_blog(self):
        self.authenticate(self.writer1)
        data = {'title': 'Trying to Update', 'content': 'Should not work'}
        response = self.client.put(f'{self.url}{self.blog2.id}/', data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Blog not found')

    def test_viewer_cannot_update_blog(self):
        self.authenticate(self.viewer)
        data = {'title': 'Viewer Update', 'content': 'Should not be allowed'}
        response = self.client.put(f'{self.url}{self.blog1.id}/', data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'You are Viewer you are not allowed to change this blog')

    def test_writer_can_patch_own_blog(self):
        self.authenticate(self.writer1)
        data = {'title': 'Patched Title'}
        response = self.client.patch(f'{self.url}{self.blog1.id}/', data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'You have changed the blog')
        self.assertEqual(response.json()['data']['title'], 'Patched Title')

    def test_writer_cannot_patch_other_writer_blog(self):
        self.authenticate(self.writer1)
        data = {'title': 'Trying to Patch'}
        response = self.client.patch(f'{self.url}{self.blog2.id}/', data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Blog not found')

    def test_viewer_cannot_patch_blog(self):
        self.authenticate(self.viewer)
        data = {'title': 'Viewer Patch'}
        response = self.client.patch(f'{self.url}{self.blog1.id}/', data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'You are Viewer you are not allowed to Patch this blog')

    def test_writer_can_delete_own_blog(self):
        self.authenticate(self.writer1)
        response = self.client.delete(f'{self.url}{self.blog1.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Yes Your Post is Successfully Deleted')
        self.assertEqual(response.json()['data']['deleted_post_author'], 'writer1')
        self.assertFalse(BlogModel.objects.filter(id=self.blog1.id).exists())

    def test_writer_cannot_delete_other_writer_blog(self):
        self.authenticate(self.writer1)
        response = self.client.delete(f'{self.url}{self.blog2.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Blog not found')
        self.assertTrue(BlogModel.objects.filter(id=self.blog2.id).exists())

    def test_viewer_cannot_delete_blog(self):
        self.authenticate(self.viewer)
        response = self.client.delete(f'{self.url}{self.blog1.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'You are Viewer you are not allowed to change Delete blog')
        self.assertTrue(BlogModel.objects.filter(id=self.blog1.id).exists())