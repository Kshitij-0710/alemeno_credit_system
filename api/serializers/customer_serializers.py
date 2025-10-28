from rest_framework import serializers
from ..models import Customer

class CustomerSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    monthly_income = serializers.IntegerField(source='monthly_salary', write_only=True)

    class Meta:
        model = Customer
        fields = [
            'customer_id', 'name', 'first_name', 'last_name', 'age', 
            'monthly_income', 'monthly_salary', 'approved_limit', 'phone_number'
        ]
        read_only_fields = ['customer_id', 'approved_limit', 'monthly_salary', 'name']
        extra_kwargs = {
            'first_name': {'write_only': True},
            'last_name': {'write_only': True},
        }
    
    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
