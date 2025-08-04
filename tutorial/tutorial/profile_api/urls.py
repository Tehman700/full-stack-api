from django.urls import path
from profile_api.views import ProfileAPIView

urlpatterns = [
    path('profile/', ProfileAPIView.as_view(), name='profile')
]