# api/viewsets/register_viewset.py

from rest_framework import viewsets, status
from rest_framework.response import Response
from ..models import Customer
from ..serializers.register_serializer import RegisterSerializer
import math

class RegisterViewSet(viewsets.ViewSet):
    """
    A viewset for registering new customers.
    """
    queryset = Customer.objects.none() 
    serializer_class = RegisterSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validated_data
        monthly_salary = validated_data['monthly_salary']
        
        approved_limit = math.ceil((36 * monthly_salary) / 100000) * 100000
        
        customer = serializer.save(approved_limit=approved_limit)
        
        response_data = {
            "customer_id": customer.customer_id,
            "name": f"{customer.first_name} {customer.last_name}",
            "age": customer.age,
            "monthly_income": customer.monthly_salary,
            "approved_limit": customer.approved_limit,
            "phone_number": customer.phone_number
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)