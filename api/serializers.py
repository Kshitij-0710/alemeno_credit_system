from datetime import date
from rest_framework import serializers
from .models import Customer, Loan

class RegisterSerializer(serializers.ModelSerializer):
    monthly_income = serializers.IntegerField(source='monthly_salary')
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'age', 'monthly_income', 'phone_number']

class LoanApplicationSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.FloatField()
    interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField()

class ViewLoanSerializer(serializers.ModelSerializer):
    customer = serializers.ReadOnlyField(source='customer.__str__') # Simpler representation
    monthly_installment = serializers.DecimalField(source='monthly_repayment', max_digits=10, decimal_places=2)
    class Meta:
        model = Loan
        fields = ['loan_id', 'customer', 'loan_amount', 'interest_rate', 'monthly_installment', 'tenure']

class ViewCustomerLoansSerializer(serializers.ModelSerializer):
    repayments_left = serializers.SerializerMethodField()
    monthly_installment = serializers.DecimalField(source='monthly_repayment', max_digits=10, decimal_places=2)
    class Meta:
        model = Loan
        fields = ['loan_id', 'loan_amount', 'interest_rate', 'monthly_installment', 'repayments_left']

    def get_repayments_left(self, obj):
        months_passed = (date.today().year - obj.start_date.year) * 12 + (date.today().month - obj.start_date.month)
        return max(0, obj.tenure - months_passed)