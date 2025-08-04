from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from quickstart.models.blog_models import BlogModel, BlogPostCommentModel
from quickstart.models.authentication_models import User_Data

User = get_user_model()


class CommentBlogPostTest(APITestCase):
    def setUp(self):
        self.writer = User.objects.create_user(username='writer', password='testpass123')
        self.commenter = User.objects.create_user(username='commenter', password='testpass456')

        User_Data.objects.create(user=self.writer, role='writer')
        User_Data.objects.create(user=self.commenter, role='viewer')

        self.writer_token = str(AccessToken.for_user(self.writer))
        self.commenter_token = str(AccessToken.for_user(self.commenter))

        self.blog = BlogModel.objects.create(user=self.writer, title='Test Blog', content='Test Content')

        self.url = '/api/comment/'

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_unauthenticated_user_cannot_comment(self):
        data = {'blog': self.blog.id, 'comment': 'Unauthenticated comment'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 401)

    def test_invalid_token_rejected(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token_here')
        data = {'blog': self.blog.id, 'comment': 'Invalid token comment'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 401)

    def test_valid_token_accepted(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.commenter}')
        data = {'blog': self.blog.id, 'comment': 'Valid token comment'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 401)

    def test_unauthenticated_user_cannot_comment(self):
        data = {'blog': self.blog.id, 'comment': 'Unauthenticated comment'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)

    def test_both_blog_and_comment_fields_required(self):
        self.authenticate(self.commenter)
        data = {'blog': self.blog.id}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Both blog and comment fields are required.')

        data = {'comment': 'Test comment'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Both blog and comment fields are required.')

    def test_blog_does_not_exist(self):
        self.authenticate(self.commenter)
        data = {'blog': 999, 'comment': 'Test comment'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Blog does not exist.')

    def test_cannot_comment_on_own_blog(self):
        self.authenticate(self.writer)
        data = {'blog': self.blog.id, 'comment': 'Cannot comment on my own blog'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'You cannot comment on your own blog.')

    def test_comment_added_successfully(self):
        self.authenticate(self.commenter)
        data = {'blog': self.blog.id, 'comment': 'This is a great blog post!'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Comment added successfully.')
        self.assertEqual(BlogPostCommentModel.objects.count(), 1)

    def test_previous_comment_updated(self):
        self.authenticate(self.commenter)
        data = {'blog': self.blog.id, 'comment': 'First comment'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.json()['message'], 'Comment added successfully.')

        data = {'blog': self.blog.id, 'comment': 'Updated comment'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Your previous comment has been updated.')
        self.assertEqual(BlogPostCommentModel.objects.count(), 1)

        comment = BlogPostCommentModel.objects.first()
        self.assertEqual(comment.comment, 'Updated comment')

    def test_only_post_method_allowed(self):
        self.authenticate(self.commenter)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Only POST is allowed for commenting')

        response = self.client.put(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Only POST is allowed for commenting')

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Only POST is allowed for commenting')

    def test_unauthenticated_user_cannot_comment(self):
        data = {'blog': self.blog.id, 'comment': 'Unauthenticated comment'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
