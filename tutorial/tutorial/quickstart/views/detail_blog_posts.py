from django.db.models import Count, Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from quickstart.models.blog_models import BlogModel, BlogPostCommentModel,ReplyCommentModel
from quickstart.models.reaction_models import ReplyReactionModel, CommentReactionModel
from quickstart.models.subscription_models import SubscribeTable
from quickstart.serializers.blog_post_serializer import BlogPostSerializer, CommentSerializer, ReplySerializer
from quickstart.utils.logger import log_error
from quickstart.utils.response_handler import ResponseHandler

class DetailBlogPost(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user=None):
        try:
            if user:
                return BlogModel.objects.get(pk=pk, user=user)
            return BlogModel.objects.get(pk=pk)
        except BlogModel.DoesNotExist:
            return None

    def get(self, request, pk):
        current_user = request.user
        if current_user.profile.role.lower() == 'viewer' or current_user.profile.role.lower() == 'writer':
            try:
                specific_blog = BlogModel.objects.select_related('user').get(pk=pk)
            except BlogModel.DoesNotExist:
                log_error(request, f'No blog exist with id {pk}', 200)
                return ResponseHandler.error(
                    message='Blog not found',
                    code=-1,
                )

            serializer = BlogPostSerializer(specific_blog)
            response_data = serializer.data.copy()
            response_data['author'] = specific_blog.user.username
            response_data['author_id'] = specific_blog.user.id
            response_data['is_subscribed'] = self.check_subscription_status(current_user, specific_blog.user)
            response_data['author_subscribers_count'] = self.get_active_subscriber_count(specific_blog.user)
            response_data['comments'] = self.get_comments_with_replies(specific_blog, current_user)

            return ResponseHandler.success(
                message='Blog Post Successfully Fetched',
                data=response_data
            )

        else:
            log_error(request, 'Other roles trying to fetch blogs', 200)
            return ResponseHandler.error(
                code = -1,
                message='No other Roles Allowed',
                errors="NONE"
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
        comments = BlogPostCommentModel.objects.filter(blog=blog).order_by('created')
        comments_data = []

        for comment in comments:
            # Get comment data
            comment_serializer = CommentSerializer(comment)
            comment_data = comment_serializer.data.copy()

            # Removing unwanted unwanted fields
            comment_data.pop('comment_likes', None)
            comment_data.pop('comment_dislikes', None)

            # Calculate comment likes and dislikes using the duncition
            comment_reactions = CommentReactionModel.objects.filter(comment=comment).aggregate(
                likes=Count('id', filter=Q(reaction='like')),
                dislikes=Count('id', filter=Q(reaction='dislike'))
            )

            comment_data['likes'] = comment_reactions['likes'] or 0
            comment_data['dislikes'] = comment_reactions['dislikes'] or 0

            # Get replies for this comment
            replies = ReplyCommentModel.objects.filter(comment=comment).order_by('created')
            replies_data = []

            for reply in replies:
                reply_serializer = ReplySerializer(reply)
                reply_data = reply_serializer.data.copy()

                # Calculate reply likes and dislikes
                reply_reactions = ReplyReactionModel.objects.filter(reply=reply).aggregate(
                    likes=Count('id', filter=Q(reaction='like')),
                    dislikes=Count('id', filter=Q(reaction='dislike'))
                )

                reply_data['likes'] = reply_reactions['likes'] or 0
                reply_data['dislikes'] = reply_reactions['dislikes'] or 0

                replies_data.append(reply_data)

            comment_data['replies'] = replies_data

            comments_data.append(comment_data)

        return comments_data


    def put(self, request, pk):
        current_user = request.user
        if current_user.profile.role.lower() == 'writer':
            try:
                specific_blog = BlogModel.objects.select_related('user').get(pk=pk, user=current_user)
            except BlogModel.DoesNotExist:
                log_error(request, 'Specific Blog not found', 200)
                return ResponseHandler.error(message='Blog not found', code=-1)


            serializer = BlogPostSerializer(specific_blog, data=request.data)
            if serializer.is_valid():
                serializer.save()
                response_data = serializer.data.copy()
                response_data['author'] = specific_blog.user.username
                response_data['author_id'] = specific_blog.user.id

                return ResponseHandler.success(
                    message='You have changed the blog',
                    data=response_data
                )
            else:
                log_error(request, 'validation failed', 200)
                return ResponseHandler.error(
                    message='Validation failed',
                    code=1,
                    errors=serializer.errors
                )

        elif current_user.profile.role.lower() == 'viewer':
            log_error(request, 'Viewer is trying to change blogs', 200)
            return ResponseHandler.error(
                code = -1,
                message='You are Viewer you are not allowed to change this blog',
                errors="NONE"
            )
        else:
            log_error(request, 'No other roles allowed', 200)
            return ResponseHandler.error(
                code = -1,
                message='No Other Roles Allowed',
                errors="NONE"
            )

    def patch(self, request, pk):
        current_user = request.user
        if current_user.profile.role.lower() == 'writer':
            try:
                specific_blog = BlogModel.objects.select_related('user').get(pk=pk, user=current_user)
            except BlogModel.DoesNotExist:
                log_error(request, 'Specific Blog not found', 200)
                return ResponseHandler.error(message='Blog not found', code=-1)

            serializer = BlogPostSerializer(specific_blog, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                response_data = serializer.data.copy()
                response_data['author'] = specific_blog.user.username
                response_data['author_id'] = specific_blog.user.id

                return ResponseHandler.success(
                    message='You have changed the blog',
                    data=response_data
                )
            else:
                log_error(request, 'validation failed', 200)
                return ResponseHandler.error(
                    message='Validation failed',
                    code=1,
                    errors=serializer.errors
                )

        elif current_user.profile.role.lower() == 'viewer':
            log_error(request, 'Viewer is trying to change blogs', 200)
            return ResponseHandler.error(
                code = -1,
                message='You are Viewer you are not allowed to Patch this blog',
                errors="NONE"
            )
        else:
            log_error(request, 'No other roles allowed', 200)
            return ResponseHandler.error(
                code = -1,
                message='No Other Roles Allowed',
                errors="NONE"
            )

    def delete(self, request, pk):
        current_user = request.user
        if current_user.profile.role.lower() == 'writer':
            try:
                specific_blog = BlogModel.objects.get(pk=pk, user=current_user)
                author_name = specific_blog.user.username
            except BlogModel.DoesNotExist:
                log_error(request, 'Specific Blog not found', 200)
                return ResponseHandler.error(message='Blog not found', code=-1)

            specific_blog.delete()

            return ResponseHandler.success(
                message='Yes Your Post is Successfully Deleted',
                data={
                    'deleted_post_author': author_name,
                    'deleted_post_id': pk
                }
            )

        elif current_user.profile.role.lower() == 'viewer':
            log_error(request, 'Viewer is trying to delete blog', 200)
            return ResponseHandler.error(
                code=-1,
                message='You are Viewer you are not allowed to change Delete blog',
                errors="NONE"
            )
        else:
            log_error(request, 'No other roles allowed', 200)
            return ResponseHandler.error(
                code = -1,
                message='No Other Roles Allowed',
                errors="NONE"
            )
