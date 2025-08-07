from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from quickstart.models.blog_models import BlogModel, BlogPostCommentModel
from quickstart.serializers.blog_post_serializer import CommentSerializer
from quickstart.utils.logger import log_error
from quickstart.utils.response_handler import ResponseHandler

class CommentBlogPost(APIView):
    permission_classes = [IsAuthenticated]
    def handle_exception(self, exc):
        if isinstance(exc, NotAuthenticated):
            return ResponseHandler.error(
                message='Authentication required to comment on blogs.',
                code=-2
            )
        return super().handle_exception(exc)
    def post(self, request):
        current_user = request.user
        data = request.data
        blog_id = data.get('blog')
        comment_text = data.get('comment')
        if not blog_id or not comment_text:
            log_error(request, 'Fields are empty', 200)
            return ResponseHandler.error(
                message='Both blog and comment fields are required.',
                code=1
            )
        try:
            blog = BlogModel.objects.get(pk=blog_id)
        except BlogModel.DoesNotExist:
            log_error(request, 'No such blog exist', 200)
            return ResponseHandler.error(
                message='Blog does not exist.',
                code=1
            )
        if blog.user == current_user:
            log_error(request, 'Trying to comment on own blog', 200)
            return ResponseHandler.error(
                message='You cannot comment on your own blog.',
                code=1
            )
        existing_comment = BlogPostCommentModel.objects.filter(user=current_user, blog=blog).first()
        if existing_comment:
            existing_comment.comment = comment_text
            existing_comment.save()
            serializer = CommentSerializer(existing_comment)

            return ResponseHandler.success(
                message='Your previous comment has been updated.',
                data=serializer.data
            )
        else:
            comment = BlogPostCommentModel.objects.create(
                user=current_user,
                blog=blog,
                comment=comment_text
            )
            serializer = CommentSerializer(comment)
            return ResponseHandler.success(
                message='Comment added successfully.',
                data=serializer.data
            )


    def http_method_not_allowed(self, request, *args, **kwargs):
        log_error(request, 'Other than POST Request being used', 200)
        return ResponseHandler.error(
            message='Only POST is allowed for commenting',
            code=-1
        )