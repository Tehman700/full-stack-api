from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from quickstart.models.blog_models import BlogModel, BlogPostCommentModel, ReplyCommentModel
from quickstart.models.reaction_models import BlogReactionModel, CommentReactionModel, ReplyReactionModel
from quickstart.models.authentication_models import User_Data

User = get_user_model()


class ReactionViewsTest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='testpass123')
        self.other_user = User.objects.create_user(username='other_user', password='testpass456')

        User_Data.objects.create(user=self.owner, role='writer')
        User_Data.objects.create(user=self.other_user, role='viewer')

        self.owner_token = str(AccessToken.for_user(self.owner))
        self.other_user_token = str(AccessToken.for_user(self.other_user))

        self.blog = BlogModel.objects.create(user=self.owner, title='Test Blog', content='Test Content')
        self.comment = BlogPostCommentModel.objects.create(
            user=self.owner,
            blog=self.blog,
            comment='Owner comment'
        )
        self.reply = ReplyCommentModel.objects.create(
            user=self.owner,
            comment=self.comment,
            reply='Owner reply'
        )

        self.blog_like_url = f'/api/blog/like/{self.blog.id}/'
        self.blog_dislike_url = f'/api/blog/dislike/{self.blog.id}/'
        self.comment_like_url = f'/api/comment/like/{self.comment.id}/'
        self.comment_dislike_url = f'/api/comment/dislike/{self.comment.id}/'
        self.reply_like_url = f'/api/reply/like/{self.reply.id}/'
        self.reply_dislike_url = f'/api/reply/dislike/{self.reply.id}/'

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_can_like_own_blog(self):
        self.authenticate(self.owner)
        response = self.client.post(self.blog_like_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(BlogReactionModel.objects.filter(user=self.owner, blog=self.blog).exists())

    def test_cannot_dislike_own_blog(self):
        self.authenticate(self.owner)
        response = self.client.post(self.blog_dislike_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('cannot', response.json()['message'].lower())

    def test_can_like_own_comment(self):
        self.authenticate(self.owner)
        response = self.client.post(self.comment_like_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(CommentReactionModel.objects.filter(user=self.owner, comment=self.comment).exists())

    def test_cannot_dislike_own_comment(self):
        self.authenticate(self.owner)
        response = self.client.post(self.comment_dislike_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('cannot', response.json()['message'].lower())

    def test_can_like_own_reply(self):
        self.authenticate(self.owner)
        response = self.client.post(self.reply_like_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ReplyReactionModel.objects.filter(user=self.owner, reply=self.reply).exists())

    def test_cannot_dislike_own_reply(self):
        self.authenticate(self.owner)
        response = self.client.post(self.reply_dislike_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('cannot', response.json()['message'].lower())

    def test_can_like_dislike_other_blog(self):
        self.authenticate(self.other_user)
        response = self.client.post(self.blog_like_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            BlogReactionModel.objects.filter(user=self.other_user, blog=self.blog, reaction='like').exists())

        response = self.client.post(self.blog_dislike_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            BlogReactionModel.objects.filter(user=self.other_user, blog=self.blog, reaction='dislike').exists())

    def test_can_like_dislike_other_comment(self):
        self.authenticate(self.other_user)

        response = self.client.post(self.comment_like_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            CommentReactionModel.objects.filter(user=self.other_user, comment=self.comment, reaction='like').exists())

        response = self.client.post(self.comment_dislike_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(CommentReactionModel.objects.filter(user=self.other_user, comment=self.comment,
                                                            reaction='dislike').exists())

    def test_can_like_dislike_other_reply(self):
        self.authenticate(self.other_user)

        response = self.client.post(self.reply_like_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            ReplyReactionModel.objects.filter(user=self.other_user, reply=self.reply, reaction='like').exists())

        response = self.client.post(self.reply_dislike_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            ReplyReactionModel.objects.filter(user=self.other_user, reply=self.reply, reaction='dislike').exists())

    def test_unauthenticated_user_cannot_react(self):
        response = self.client.post(self.blog_like_url)
        self.assertEqual(response.status_code, 401)

        response = self.client.post(self.comment_like_url)
        self.assertEqual(response.status_code, 401)

        response = self.client.post(self.reply_like_url)
        self.assertEqual(response.status_code, 401)

    def test_one_reaction_at_time_and_toggle(self):
        self.authenticate(self.other_user)

        # First like
        response = self.client.post(self.blog_like_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(BlogReactionModel.objects.filter(user=self.other_user, blog=self.blog).count(), 1)

        # Like again (should remove)
        response = self.client.post(self.blog_like_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(BlogReactionModel.objects.filter(user=self.other_user, blog=self.blog).count(), 0)

        # Now dislike
        response = self.client.post(self.blog_dislike_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            BlogReactionModel.objects.filter(user=self.other_user, blog=self.blog, reaction='dislike').exists())

    def test_blog_not_found(self):
        self.authenticate(self.other_user)
        response = self.client.post('/api/blog/like/999/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Blog not found')

    def test_comment_not_found(self):
        self.authenticate(self.other_user)
        response = self.client.post('/api/comment/like/999/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Comment not found')

    def test_reply_not_found(self):
        self.authenticate(self.other_user)
        response = self.client.post('/api/reply/like/999/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Reply not found.')

    def test_only_post_method_allowed(self):
        self.authenticate(self.other_user)

        # Test GET method on blog reaction
        response = self.client.get(self.blog_like_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Only POST is allowed on register')

        # Test PUT method on comment reaction
        response = self.client.put(self.comment_like_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Only POST is allowed for reacting to comments.')

        # Test DELETE method on reply reaction - should trigger http_method_not_allowed
        response = self.client.delete(self.reply_like_url)
        self.assertEqual(response.status_code, 200)