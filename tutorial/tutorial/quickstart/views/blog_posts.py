from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from quickstart.models.blog_models import BlogPostCommentModel, ReplyCommentModel, BlogModel
from quickstart.models.subscription_models import SubscribeTable
from quickstart.serializers.blog_post_serializer import BlogPostSerializer, CommentSerializer, ReplySerializer
from quickstart.utils.response_handler import ResponseHandler
from quickstart.tasks.email_tasks import send_blog_notification_email


class BlogPostAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        current_user = request.user

        if current_user.profile.role.lower() != 'writer':
            return ResponseHandler.error(
                message='Only Writers are allowed to post',
                code=0,
                errors=None
            )

        post_data = request.data
        allowed_fields = {'title', 'content'}
        extra_fields = set(post_data.keys()) - allowed_fields
        if extra_fields:
            return ResponseHandler.error(
                message='Only title and content are allowed.',
                errors="NONE",
                code=1
            )

        serializer = BlogPostSerializer(data=post_data)
        if serializer.is_valid():
            serializer.save(user=current_user)
            blog_title = serializer.data.get('title', 'Untitled')

            response_data = serializer.data.copy()
            response_data['author'] = current_user.username
            response_data['author_id'] = current_user.id

            # Fetch subscribers' emails
            subscribers = SubscribeTable.objects.filter(author=current_user, is_active=True).select_related('subscriber')
            subscribers_emails = [sub.subscriber.email for sub in subscribers if sub.subscriber.email]

            # Below function is doing all the celery jobs needed for scheduling

            send_blog_notification_email.delay(current_user.username, blog_title, subscribers_emails)

            return ResponseHandler.success(
                message="Blog created and notifications sent.",
                data=response_data
            )
        else:
            return ResponseHandler.rest_error(
                message='Please Enter Correct fields',
                errors=serializer.errors,
                code=1
            )



    def get(self, request):
        current_user = request.user

        if current_user.profile.role.lower() == 'viewer' or current_user.profile.role.lower() == 'writer':
            # Viewer sees all blog posts with author information
            blogs = BlogModel.objects.select_related('user').all().order_by('id')
            serializer = BlogPostSerializer(blogs, many=True)

            data_with_authors = []
            for i, blog in enumerate(blogs):
                blog_data = serializer.data[i].copy()
                blog_data['author'] = blog.user.username
                blog_data['author_id'] = blog.user.id
                # Add subscription status using separate tables
                blog_data['is_subscribed'] = self.check_subscription_status(current_user, blog.user)

                # Add active subscriber count for the author
                blog_data['author_subscribers_count'] = self.get_active_subscriber_count(blog.user)
                blog_data['comments'] = self.get_comments_with_replies(blog, current_user)
                data_with_authors.append(blog_data)
            return ResponseHandler.success(
                code = 0,
                message = "Blog Post Successfully Fetched",
                data = data_with_authors
            )
        else:
            return ResponseHandler.error(
                message='No other Roles are Allowed',
                code=-1
            )

    def check_subscription_status(self, current_user, author):
        if current_user == author:
            return None

        return SubscribeTable.objects.filter(
            subscriber=current_user,
            author=author,
            is_active=True
        ).exists()

    def get_active_subscriber_count(self, author):
        return SubscribeTable.objects.filter(
            author=author,
            is_active=True
        ).count()

    def get_comments_with_replies(self, blog, current_user):
        """Helper method to get comments with their replies using database fields"""
        comments = BlogPostCommentModel.objects.filter(blog=blog).order_by('created')
        comments_data = []

        for comment in comments:
            # Get comment data - now includes likes/dislikes from database
            comment_serializer = CommentSerializer(comment)
            comment_data = comment_serializer.data.copy()

            # Get replies for this comment
            replies = ReplyCommentModel.objects.filter(comment=comment).order_by('created')
            replies_data = []

            for reply in replies:
                reply_serializer = ReplySerializer(reply)
                reply_data = reply_serializer.data.copy()
                # Now includes likes/dislikes from database fields
                replies_data.append(reply_data)

            comment_data['replies'] = replies_data
            comments_data.append(comment_data)

        return comments_data


    def http_method_not_allowed(self, request, *args, **kwargs):
        return ResponseHandler.error(
            message='No other Methods Allowed',
            code=-1,
            errors="NONE"
        )
