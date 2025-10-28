# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterViewSet, EligibilityView

router = DefaultRouter()
router.register(r'register', RegisterViewSet, basename='register')

urlpatterns = [
    path('', include(router.urls)),
    path('check-eligibility/', EligibilityView.as_view(), name='check-eligibility'),
]