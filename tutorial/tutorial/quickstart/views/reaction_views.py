from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from quickstart.models.blog_models import BlogModel, BlogPostCommentModel, ReplyCommentModel
from quickstart.models.reaction_models import BlogReactionModel, CommentReactionModel, ReplyReactionModel
from quickstart.utils.response_handler import ResponseHandler
from quickstart.utils.reaction_handler import handle_reaction_logic, extract_action_from_path


class BlogReaction(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        current_user = request.user

        try:
            blog = BlogModel.objects.get(pk=pk)
        except BlogModel.DoesNotExist:
            return ResponseHandler.error(
                message='Blog not found',
                code=1
            )

        action = extract_action_from_path(request.path)

        return handle_reaction_logic(
            current_user=current_user,
            target_object=blog,
            action=action,
            reaction_model=BlogReactionModel,
            reaction_field_name='blog',
            object_name='blog post'
        )

    def http_method_not_allowed(self, request, *args, **kwargs):
        return ResponseHandler.error(
            message='Only POST is allowed on register',
            code=-1
        )


class CommentBlogPostReaction(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        current_user = request.user

        try:
            comment = BlogPostCommentModel.objects.get(pk=pk)
        except BlogPostCommentModel.DoesNotExist:
            return ResponseHandler.error(
                message='Comment not found',
                code=1
            )

        action = extract_action_from_path(request.path)

        return handle_reaction_logic(
            current_user=current_user,
            target_object=comment,
            action=action,
            reaction_model=CommentReactionModel,
            reaction_field_name='comment',
            object_name='comment'
        )

    def http_method_not_allowed(self, request, *args, **kwargs):
        return ResponseHandler.error(
            message='Only POST is allowed for reacting to comments.',
            code=-1
        )


class ReplyReactionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        current_user = request.user

        try:
            reply = ReplyCommentModel.objects.select_related('comment__blog', 'user').get(pk=pk)
        except ReplyCommentModel.DoesNotExist:
            return ResponseHandler.error(
                message='Reply not found.',
                code=1
            )

        action = extract_action_from_path(request.path)

        return handle_reaction_logic(
            current_user=current_user,
            target_object=reply,
            action=action,
            reaction_model=ReplyReactionModel,
            reaction_field_name='reply',
            object_name='reply'
        )


    def http_method_not_allowed(self, request, *args, **kwargs):
        return ResponseHandler.error(
            message='Only POST is allowed for reacting to comments.',
            code=-1
        )