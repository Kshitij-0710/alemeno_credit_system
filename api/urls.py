# api/urls.py

from rest_framework.routers import DefaultRouter
from .viewsets.register_viewset import RegisterViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'register', RegisterViewSet, basename='register')

urlpatterns = [
    path('', include(router.urls)),
    # Add other paths here later
]