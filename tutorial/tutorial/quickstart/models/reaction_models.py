from django.db import models
from django.contrib.auth.models import User
from quickstart.models.blog_models import BlogModel, BlogPostCommentModel, ReplyCommentModel

"""
    Below all Models are totally for the Mechanism Related to Reactions for Blogs,Comments or Replies
"""

class BlogReactionModel(models.Model):
    REACTION_CHOICES = (
        ('like', 'Like'),
        ('dislike', 'Dislike'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    blog = models.ForeignKey(BlogModel, on_delete=models.CASCADE)
    reaction = models.CharField(max_length=10, choices=REACTION_CHOICES)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'blog')  # One reaction per user per blog

    def __str__(self):
        return f"{self.user.username} reacted {self.reaction} to '{self.blog.title}'"


class CommentReactionModel(models.Model):
    REACTION_CHOICES = (
        ('like', 'Like'),
        ('dislike', 'Dislike'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment_reactors")
    comment = models.ForeignKey(BlogPostCommentModel, on_delete=models.CASCADE, related_name="comment_reactions")
    reaction = models.CharField(max_length=10, choices=REACTION_CHOICES)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'comment')  # One reaction per user per comment

    def __str__(self):
        return f"{self.user.username} reacted {self.reaction} to comment on '{self.comment.blog.title}'"


class ReplyReactionModel(models.Model):
    REACTION_CHOICES = (
        ('like', 'Like'),
        ('dislike', 'Dislike'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reply = models.ForeignKey(ReplyCommentModel, on_delete=models.CASCADE, related_name='reply_reactions')
    reaction = models.CharField(max_length=10, choices=REACTION_CHOICES)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'reply')  # One reaction per user per reply

    def __str__(self):
        return f"{self.user.username} reacted {self.reaction} to reply"



