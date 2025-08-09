# from django.db.models import Count, Q
# from django.http import JsonResponse
# from rest_framework import status
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from quickstart.models.blog_models import BlogModel, BlogPostCommentModel, CommentReactionModel, ReplyCommentModel, \
#     ReplyReactionModel
# from quickstart.serializers.blog_post_serializer import BlogPostSerializer, CommentSerializer, ReplySerializer
# from quickstart.utils.response_handler import ResponseHandler
#
#
# class BlogPostAPIView(APIView):
#     permission_classes = [IsAuthenticated]
#
#
#     # POST --->   Writer
#     # GET  ---> Writer, Viewer
#     # PUT ----> writer
#     # Patch ----> writer
#     # Delete -----> Writer
#
#     def post(self, request):
#
#         current_user = request.user
#         if current_user.profile.role.lower() != 'writer':
#             return ResponseHandler.error(
#                 message='Only Writers are allowed to post',
#                 code=0,
#                 errors=None
#             )
#
#
#         post_data = request.data
#         allowed_fields = {'title', 'content'}
#         extra_fields = set(post_data.keys()) - allowed_fields
#         if extra_fields:
#             return ResponseHandler.error(
#                 message='Only title and content are allowed.',
#                 errors="NONE",
#                 code=1
#             )
#
#         serializer = BlogPostSerializer(data=post_data)
#
#         if serializer.is_valid():
#             serializer.save(user  = request.user) # THis is the autoamtica fethcer
#
#             # Create response data with author information
#             response_data = serializer.data.copy()
#             response_data['author'] = current_user.username
#             response_data['author_id'] = current_user.id
#             return ResponseHandler.success(
#                 message='Blog Post Successfully Created',
#                 data=response_data
#             )
#         else:
#             return ResponseHandler.rest_error(
#                 message='Please Enter Correct fields',
#                 errors=serializer.errors,
#                 code=1
#             )
#

#     def get(self, request):
#         current_user = request.user
#
#         if current_user.profile.role.lower() == 'viewer' or current_user.profile.role.lower() == 'writer':
#             # Viewer sees all blog posts with author information
#             blogs = BlogModel.objects.select_related('user').all().order_by('id')
#             serializer = BlogPostSerializer(blogs, many=True)
#
#             data_with_authors = []
#             for i, blog in enumerate(blogs):
#                 blog_data = serializer.data[i].copy()
#                 blog_data['author'] = blog.user.username
#                 blog_data['author_id'] = blog.user.id
#
#                 blog_data['comments'] = self.get_comments_with_replies(blog, current_user)
#                 data_with_authors.append(blog_data)
#             return ResponseHandler.success(
#                 code = 0,
#                 message = "Blog Post Successfully Fetched",
#                 data = data_with_authors
#             )

        # This is for the reason that how can a writer cannot see other blogs and how will he react or comment othre blospots,etc
        # elif current_user.profile.role.lower() == 'writer':
        #     # Writer sees only their own posts
        #     blogs = BlogModel.objects.filter(user=request.user).order_by('id')
        #     serializer = BlogPostSerializer(blogs, many=True)
        #     data_with_authors = []
        #     for i, blog in enumerate(blogs):
        #         blog_data = serializer.data[i].copy()
        #         blog_data['author'] = current_user.username
        #         blog_data['author_id'] = current_user.id
        #
        #         blog_data['comments'] = self.get_comments_with_replies(blog, current_user)
        #
        #
        #         data_with_authors.append(blog_data)
        #
        #     return ResponseHandler.success(
        #         code=0,
        #         message="For this Writer Blog Posts Fetched",
        #         data=data_with_authors
        #     )

    #     else:
    #         return ResponseHandler.error(
    #             message='No other Roles are Allowed',
    #             code=-1
    #         )
    #
    # def get_comments_with_replies(self, blog, current_user):
    #     """Helper method to get comments with their replies and reaction counts"""
    #     comments = BlogPostCommentModel.objects.filter(blog=blog).order_by('created')
    #     comments_data = []
    #
    #     for comment in comments:
    #         # Get comment data
    #         comment_serializer = CommentSerializer(comment)
    #         comment_data = comment_serializer.data.copy()
    #
    #         # Remove unwanted fields
    #         comment_data.pop('comment_likes', None)
    #         comment_data.pop('comment_dislikes', None)
    #
    #         # Calculate comment likes and dislikes
    #         comment_reactions = CommentReactionModel.objects.filter(comment=comment).aggregate(
    #             likes=Count('id', filter=Q(reaction='like')),
    #             dislikes=Count('id', filter=Q(reaction='dislike'))
    #         )
    #
    #         comment_data['likes'] = comment_reactions['likes'] or 0
    #         comment_data['dislikes'] = comment_reactions['dislikes'] or 0
    #
    #         # Get replies for this comment
    #         replies = ReplyCommentModel.objects.filter(comment=comment).order_by('created')
    #         replies_data = []
    #
    #         for reply in replies:
    #             reply_serializer = ReplySerializer(reply)
    #             reply_data = reply_serializer.data.copy()
    #
    #             # Calculate reply likes and dislikes
    #             reply_reactions = ReplyReactionModel.objects.filter(reply=reply).aggregate(
    #                 likes=Count('id', filter=Q(reaction='like')),
    #                 dislikes=Count('id', filter=Q(reaction='dislike'))
    #             )
    #
    #             reply_data['likes'] = reply_reactions['likes'] or 0
    #             reply_data['dislikes'] = reply_reactions['dislikes'] or 0
    #
    #             # Add current user's reaction to this reply
    #             user_reply_reaction = ReplyReactionModel.objects.filter(
    #                 reply=reply, user=current_user
    #             ).first()
    #             reply_data['user_reaction'] = user_reply_reaction.reaction if user_reply_reaction else None
    #
    #             replies_data.append(reply_data)
    #
    #         comment_data['replies'] = replies_data
    #         comment_data['replies_count'] = len(replies_data)
    #
    #         comments_data.append(comment_data)
    #
    #     return comments_data
    #
    #
    # def http_method_not_allowed(self, request, *args, **kwargs):
    #     return ResponseHandler.error(
    #         message='No other Methods Allowed',
    #         code=-1,
    #         errors="NONE"
    #     )
    #




























# Fake code for DetailBlogPost in which we can see the writer mechanism:

        # if current_user.profile.role.lower() == 'writer':
        #     try:
        #         specific_blog = BlogModel.objects.get(pk=pk, user=current_user)
        #     except BlogModel.DoesNotExist:
        #         return ResponseHandler.error(message='Blog not found', code=-1)
        #
        #     serializer = BlogPostSerializer(specific_blog)
        #     response_data = serializer.data.copy()
        #     response_data['author'] = specific_blog.user.username
        #     response_data['author_id'] = specific_blog.user.id
        #
        #     # Add comments with reaction counts
        #     comments = BlogPostCommentModel.objects.filter(blog=specific_blog).order_by('created')
        #     comments_data = []
        #
        #     for comment in comments:
        #         comment_serializer = CommentSerializer(comment)
        #         comment_data = comment_serializer.data.copy()
        #
        #         # Remove unwanted fields if they exist in serializer
        #         comment_data.pop('comment_likes', None)
        #         comment_data.pop('comment_dislikes', None)
        #
        #         # Calculate like and dislike counts for each comment
        #         reactions = CommentReactionModel.objects.filter(comment=comment).aggregate(
        #             likes=Count('id', filter=Q(reaction='like')),
        #             dislikes=Count('id', filter=Q(reaction='dislike'))
        #         )
        #
        #         comment_data['likes'] = reactions['likes'] or 0
        #         comment_data['dislikes'] = reactions['dislikes'] or 0
        #
        #         comments_data.append(comment_data)
        #
        #     response_data['comments'] = comments_data
        #
        #     return ResponseHandler.success(
        #         message='Blog Post Successfully Fetched',
        #         data=response_data
        #     )



# In the Normal BlogPostAPIView


        # This is for the reason that how can a writer cannot see other blogs and how will he react or comment othre blospots,etc
        # elif current_user.profile.role.lower() == 'writer':
        #     # Writer sees only their own posts
        #     blogs = BlogModel.objects.filter(user=request.user).order_by('id')
        #     serializer = BlogPostSerializer(blogs, many=True)
        #     data_with_authors = []
        #     for i, blog in enumerate(blogs):
        #         blog_data = serializer.data[i].copy()
        #         blog_data['author'] = current_user.username
        #         blog_data['author_id'] = current_user.id
        #
        #         blog_data['comments'] = self.get_comments_with_replies(blog, current_user)
        #
        #
        #         data_with_authors.append(blog_data)
        #
        #     return ResponseHandler.success(
        #         code=0,
        #         message="For this Writer Blog Posts Fetched",
        #         data=data_with_authors
        #     )
