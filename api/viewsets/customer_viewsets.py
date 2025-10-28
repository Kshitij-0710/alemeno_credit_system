from rest_framework import viewsets, status
from rest_framework.response import Response
from ..models import Customer
from ..serializers.customer_serializers import CustomerSerializer
import math

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Calculate approved limit
        monthly_salary = serializer.validated_data['monthly_salary']
        approved_limit = math.ceil((36 * monthly_salary) / 100000) * 100000
        
        # Save the instance
        customer = serializer.save(approved_limit=approved_limit)
        
        # Prepare the custom response body
        response_data = {
            "customer_id": customer.customer_id,
            "name": f"{customer.first_name} {customer.last_name}",
            "age": customer.age,
            "monthly_income": customer.monthly_salary,
            "approved_limit": customer.approved_limit,
            "phone_number": customer.phone_number
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)
