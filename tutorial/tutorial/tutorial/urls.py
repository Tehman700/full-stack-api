from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('quickstart.urls')),
    path('profile_api/', include('profile_api.urls')),
]
