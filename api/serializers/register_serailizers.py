# api/serializers/register_serializer.py

from rest_framework import serializers
from ..models import Customer

class RegisterSerializer(serializers.ModelSerializer):
    monthly_income = serializers.IntegerField(source='monthly_salary', write_only=True)

    class Meta:
        model = Customer
        fields = [
            'first_name', 
            'last_name', 
            'age', 
            'monthly_income', 
            'phone_number'
        ]