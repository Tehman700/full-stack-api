from django.db import models
from django.contrib.auth.models import User

class User_Data(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    created = models.DateTimeField(auto_now_add=True)
    mobile_number = models.CharField(max_length=120)
    role = models.CharField(max_length=120)
    email_address = models.EmailField()
    first_name = models.CharField(max_length=150, blank=True, default='')
    last_name = models.CharField(max_length=150, blank=True, default='')
    class Meta:
        ordering = ['created']

    def __str__(self):
        return f"{self.user.username} - {self.role}"




class LoginModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    username = models.CharField(max_length=120)
    password = models.CharField(max_length=255)


    class Meta:
        ordering = ['created']
