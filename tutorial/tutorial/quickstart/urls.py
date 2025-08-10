from django.urls import path
from quickstart.views.reply_comment_view import ReplyCommentBlogPost
from quickstart.views.authentication_views import RegisterAPIView
from quickstart.views.authentication_views import LoginViewSet
from quickstart.views.blog_posts import BlogPostAPIView
from quickstart.views.detail_blog_posts import DetailBlogPost
from quickstart.views.comment_blog_posts import CommentBlogPost
from quickstart.views.reaction_views import BlogReaction, CommentBlogPostReaction, ReplyReactionView
from quickstart.views.subscription_views import SubscribeView, UnsubscribeView

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='registering'),
    path('login/', LoginViewSet.as_view({'post': 'create'}), name='login'),
    path('blog/', BlogPostAPIView.as_view(), name='blogpost'),
    path('blog/<int:pk>/', DetailBlogPost.as_view(), name='detailblogpost'),
    path('blog/like/<int:pk>/', BlogReaction.as_view(), name='likeblog'),
    path('blog/dislike/<int:pk>/', BlogReaction.as_view(), name='dislikeblog'),
    path('comment/', CommentBlogPost.as_view(), name='commentblogpost'),

    path('comment/like/<int:pk>/', CommentBlogPostReaction.as_view(), name='likecomment'),
    path('comment/dislike/<int:pk>/', CommentBlogPostReaction.as_view(), name='dislikecomment'),
    path('reply/', ReplyCommentBlogPost.as_view(), name = 'replycomment'),
    path('reply/dislike/<int:pk>/', ReplyReactionView.as_view(), name='dislikereply'),
    path('reply/like/<int:pk>/', ReplyReactionView.as_view(), name='likereply'),
    path('subscribe/<str:pk>/', SubscribeView.as_view(), name='subscribe'),
    path('unsubscribe/<str:pk>/', UnsubscribeView.as_view(), name='unsubscribe'),
]
