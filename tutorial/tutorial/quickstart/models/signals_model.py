from django.db import models
from django.contrib.auth.models import User

class ActivityLog(models.Model):
    action = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Allow null for registration
    model_name = models.CharField(max_length=100)
    instance_id = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    STATUS_CHOICES = (
        (1, 'Submitted'),
        (2, 'Deleted'),
    )
    status = models.IntegerField(default=1, choices=STATUS_CHOICES)


    def __str__(self):
        status_str = dict(self.STATUS_CHOICES).get(self.status, 'Unknown')
        username = self.user.username if self.user else "Anonymous"

        if self.description:
            return f"[{status_str}] {self.description}"

        return f"[{status_str}] {username} {self.action} {self.model_name}(#{self.instance_id})"





# This model is solely for saving the instances of blogs for specific status updates when blog deleted


class BlogActivityMap(models.Model):
    blog = models.OneToOneField('BlogModel', on_delete=models.CASCADE, related_name='activity_map')
    activity_logs = models.ManyToManyField('ActivityLog')

    def __str__(self):
        return f"Activity Map for Blog #{self.blog.id}"
