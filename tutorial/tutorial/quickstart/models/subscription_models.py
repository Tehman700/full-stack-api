from django.db import models
from django.contrib.auth.models import User

class SubscribeTable(models.Model):
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscribe_records')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author_records')
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['subscribed_at']

    def __str__(self):
        return f"{self.subscriber.username} subscribed to '{self.author.username}' BlogPosts"


class UnsubscribeTable(models.Model):
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE, related_name='unsubscribe_records')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='unsubscription_records')
    unsubscribed_at = models.DateTimeField(auto_now_add=True)
    original_subscription = models.ForeignKey(SubscribeTable, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ['unsubscribed_at']

    def __str__(self):
        return f"{self.subscriber.username} unsubscribed from {self.author.username} BlogPosts"



