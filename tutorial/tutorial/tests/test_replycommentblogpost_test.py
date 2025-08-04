from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from quickstart.models.blog_models import BlogModel, BlogPostCommentModel, ReplyCommentModel
from quickstart.models.authentication_models import User_Data

User = get_user_model()


class ReplyCommentBlogPostTest(APITestCase):
    def setUp(self):
        self.writer = User.objects.create_user(username='writer', password='testpass123')
        self.commenter = User.objects.create_user(username='commenter', password='testpass456')
        self.replier = User.objects.create_user(username='replier', password='testpass789')

        # Create User_Data profiles with roles
        User_Data.objects.create(user=self.writer, role='writer')
        User_Data.objects.create(user=self.commenter, role='viewer')
        User_Data.objects.create(user=self.replier, role='viewer')

        # Auth tokens if needed
        self.writer_token = str(AccessToken.for_user(self.writer))
        self.commenter_token = str(AccessToken.for_user(self.commenter))
        self.replier_token = str(AccessToken.for_user(self.replier))

        # Create test blog post and comment
        self.blog = BlogModel.objects.create(user=self.writer, title='Test Blog', content='Test Content')
        self.comment = BlogPostCommentModel.objects.create(
            user=self.commenter,
            blog=self.blog,
            comment='This is a test comment'
        )

        self.url = '/api/reply/'

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_both_comment_and_reply_fields_required(self):
        self.authenticate(self.replier)
        # Missing reply field
        data = {'comment': self.comment.id}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Both comment and reply fields are required.')

        # Missing comment field
        data = {'reply': 'Test reply'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Both comment and reply fields are required.')

    def test_comment_does_not_exist(self):
        self.authenticate(self.replier)
        data = {'comment': 999, 'reply': 'Test reply'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Comment does not exist.')

    def test_reply_added_successfully(self):
        self.authenticate(self.replier)
        data = {'comment': self.comment.id, 'reply': 'This is a great comment!'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Reply added successfully.')
        self.assertEqual(ReplyCommentModel.objects.count(), 1)

    def test_previous_reply_updated(self):
        # First reply
        self.authenticate(self.replier)
        data = {'comment': self.comment.id, 'reply': 'First reply'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.json()['message'], 'Reply added successfully.')

        # Second reply on same comment - should update previous
        data = {'comment': self.comment.id, 'reply': 'Updated reply'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Your previous reply has been updated.')
        self.assertEqual(ReplyCommentModel.objects.count(), 1)

        # Verify reply was updated
        reply = ReplyCommentModel.objects.first()
        self.assertEqual(reply.reply, 'Updated reply')

    def test_can_reply_on_own_comments(self):
        self.authenticate(self.commenter)
        data = {'comment': self.comment.id, 'reply': 'Replying to my own comment'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Reply added successfully.')
        self.assertEqual(ReplyCommentModel.objects.count(), 1)

    def test_unauthenticated_user_cannot_reply(self):
        # Don't authenticate - test without login
        data = {'comment': self.comment.id, 'reply': 'Unauthenticated reply'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Authentication required to reply on blogs.')

    def test_only_post_method_allowed(self):
        self.authenticate(self.replier)

        # Test GET method
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Only POST is allowed for replying')

        # Test PUT method
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Only POST is allowed for replying')

        # Test DELETE method
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Only POST is allowed for replying')