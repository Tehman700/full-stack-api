from rest_framework import serializers
from quickstart.models.blog_models import BlogModel, BlogPostCommentModel, ReplyCommentModel


class BlogPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogModel
        fields = ['id', 'title', 'content', 'likes', 'dislikes']


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    blog = serializers.PrimaryKeyRelatedField(queryset=BlogModel.objects.all())

    class Meta:
        model = BlogPostCommentModel
        fields = ['id', 'user', 'blog', 'comment', 'likes', 'dislikes','created']


class ReplySerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    comment = serializers.PrimaryKeyRelatedField(queryset=BlogPostCommentModel.objects.all())

    class Meta:
        model = ReplyCommentModel
        fields = ['id', 'user', 'comment', 'reply', 'likes', 'dislikes' ,'created']

