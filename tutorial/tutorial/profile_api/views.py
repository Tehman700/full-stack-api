from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from quickstart.models.blog_models import BlogPostCommentModel, ReplyCommentModel, BlogModel
from quickstart.models.reaction_models import CommentReactionModel, ReplyReactionModel
from quickstart.models.subscription_models import SubscribeTable
from quickstart.serializers.blog_post_serializer import BlogPostSerializer, CommentSerializer, ReplySerializer
from quickstart.utils.response_handler import ResponseHandler


class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        current_user = request.user

        if current_user.profile.role.lower() != 'writer':
            return ResponseHandler.error(
                message='You are not a writer user',
                code=1,
                errors=None
            )

        specific_blogs = BlogModel.objects.filter(user=current_user)
        total_blogs_count = specific_blogs.count()
        subscribers_count = SubscribeTable.objects.filter(author=current_user, is_active=True).count()
        total_subscriptions_ever = SubscribeTable.objects.filter(author=current_user).count()

        unsubscribed_count = total_subscriptions_ever - subscribers_count

        # Check if user has any blogs
        if total_blogs_count == 0:
            user_data = {
                "username": current_user.username,
                "email": current_user.email or "Not provided",
                "first_name": current_user.profile.first_name or "Not provided",
                "last_name": current_user.profile.last_name or "Not provided",
                "date_joined": current_user.date_joined,
                "is_active": current_user.is_active,
                "mobile_number": current_user.profile.mobile_number,
                "role": current_user.profile.role,
                "total_blogs_count": total_blogs_count,
            }
            second = {
                "blogs" : "No Blogs You haven't Posted yet"
            }
            return JsonResponse({
                "user": user_data,
                "blog_details": second,
            }, status=200)


        # Create simple blog data with title, likes, dislikes, comments count
        simple_blogs = []
        total_blog_likes = 0
        total_blog_dislikes = 0
        total_comments_received = 0

        for blog in specific_blogs:
            # Count comments for this blog
            comments_count = BlogPostCommentModel.objects.filter(blog=blog).count()
            total_comments_received += comments_count

            # Add to totals
            total_blog_likes += blog.likes
            total_blog_dislikes += blog.dislikes

            simple_blog = {
                "title": blog.title,
                "likes": blog.likes,
                "dislikes": blog.dislikes,
                "comments_count": comments_count
            }
            simple_blogs.append(simple_blog)

        user_data_second = {
            "blogs": simple_blogs,
            "total_blog_likes": total_blog_likes,
            "total_blog_dislikes": total_blog_dislikes,
            "total_comments_received": total_comments_received,
        }
        # Get list of subscribers' emails
        subscribers = SubscribeTable.objects.filter(author=current_user, is_active=True).select_related('subscriber')

        # We will use this below list somewhere else for email notification mechanism
        subscribers_emails = [sub.subscriber.email for sub in subscribers if sub.subscriber.email]

        user_data = {
            "username": current_user.username,
            "email": current_user.email or "Not provided",
            "first_name": current_user.profile.first_name or "Not provided",
            "last_name": current_user.profile.last_name or "Not provided",
            "date_joined": current_user.date_joined,
            "is_active": current_user.is_active,
            "mobile_number": current_user.profile.mobile_number,
            "role": current_user.profile.role,
            "total_blogs_count": total_blogs_count,
            "total_subscribers_count": subscribers_count,
            "total_ever_subscriptions_count": total_subscriptions_ever,
            "total_unsubscribe_count" : unsubscribed_count,
            "subscribers_emails": subscribers_emails
        }

        return JsonResponse({
            "user": user_data,
            "blog_details": user_data_second,
        }, status=200)