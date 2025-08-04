from django.db import models
from django.contrib.auth.models import User

"""
    Below all Models are totally for the Mechanism Related to Blogs-Posting, reply and comments mechanism
"""

class BlogModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blogs')
    title = models.CharField(max_length=120)
    content = models.TextField()
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)


    class Meta:
        ordering = ['created']


class BlogPostCommentModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    blog = models.ForeignKey(BlogModel, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)

    class Meta:
        ordering = ['created']

    def __str__(self):
        return f"{self.user.username} commented on '{self.blog.title}'"



class ReplyCommentModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(BlogPostCommentModel, on_delete=models.CASCADE)
    reply = models.TextField()
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ['created']

    def __str__(self):
        return f"{self.user.username} replied on '{self.comment.blog.title}'"









