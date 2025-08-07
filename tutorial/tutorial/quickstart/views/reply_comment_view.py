from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from quickstart.models.blog_models import BlogModel, BlogPostCommentModel, ReplyCommentModel
from quickstart.serializers.blog_post_serializer import ReplySerializer
from quickstart.utils.logger import log_error
from quickstart.utils.response_handler import ResponseHandler

class ReplyCommentBlogPost(APIView):
    permission_classes = [IsAuthenticated]

    def handle_exception(self, exc):
        if isinstance(exc, NotAuthenticated):
            return ResponseHandler.error(
                message='Authentication required to reply on blogs.',
                code=-2
            )
        return super().handle_exception(exc)

    def post(self, request):
        current_user = request.user
        data = request.data
        comment_id = data.get('comment')
        reply_text = data.get('reply')
        if not comment_id or not reply_text:
            log_error(request, 'Both or one field is missing', 200)
            return ResponseHandler.error(
                message='Both comment and reply fields are required.',
                code=1
            )

        try:
            comment = BlogPostCommentModel.objects.select_related('blog', 'user').get(pk=comment_id)
        except BlogPostCommentModel.DoesNotExist:
            log_error(request, 'No comment exist', 200)
            return ResponseHandler.error(
                message='Comment does not exist.',
                code=1
            )
        # Check if user has already replied to this comment
        existing_reply = ReplyCommentModel.objects.filter(user=current_user, comment=comment).first()

        if existing_reply:
            # Update the existing reply
            existing_reply.reply = reply_text
            existing_reply.save()
            serializer = ReplySerializer(existing_reply)

            return ResponseHandler.success(
                message='Your previous reply has been updated.',
                data=serializer.data
            )
        else:
            # Create a new reply
            reply = ReplyCommentModel.objects.create(
                user=current_user,
                comment=comment,
                reply=reply_text
            )
            serializer = ReplySerializer(reply)

            return ResponseHandler.success(
                message='Reply added successfully.',
                data=serializer.data
                )

    def http_method_not_allowed(self, request, *args, **kwargs):
        log_error(request, 'Methods other than POST being used', 200)
        return ResponseHandler.error(
            message='Only POST is allowed for replying',
            code=-1
        )