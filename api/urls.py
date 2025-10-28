# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CreateLoanView, RegisterViewSet, EligibilityView, ViewCustomerLoansView, ViewLoanView

router = DefaultRouter()
register_view = RegisterViewSet.as_view({'post': 'create'})

urlpatterns = [
    path('', include(router.urls)),
    path('register/', register_view, name='register'),
    path('check-eligibility/', EligibilityView.as_view(), name='check-eligibility'),
    path('create-loan/', CreateLoanView.as_view(), name='create-loan'),
    path('view-loan/<int:loan_id>/', ViewLoanView.as_view(), name='view-loan'),
    path('view-loans/<int:customer_id>/', ViewCustomerLoansView.as_view(), name='view-customer-loans'), 

]