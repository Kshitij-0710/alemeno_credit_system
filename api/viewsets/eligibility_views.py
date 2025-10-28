from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import Customer, Loan
from ..serializers import LoanEligibilitySerializer
from ..utils import calculate_credit_score
from django.db.models import Sum
from datetime import date

class CheckEligibilityView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoanEligibilitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            customer = Customer.objects.get(pk=data['customer_id'])
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=404)

        # Rule: If sum of all current EMIs > 50% of monthly salary, don't approve
        current_emis = Loan.objects.filter(
            customer=customer, end_date__gte=date.today()
        ).aggregate(total=Sum('monthly_repayment'))['total'] or 0
        
        if current_emis > customer.monthly_salary * 0.5:
            return Response({
                "customer_id": customer.customer_id,
                "approval": False,
                "interest_rate": data['interest_rate'],
                "corrected_interest_rate": None,
                "tenure": data['tenure'],
                "monthly_installment": 0
            })

        credit_score = calculate_credit_score(customer)
        
        approval = False
        corrected_interest_rate = data['interest_rate']

        if credit_score > 50:
            approval = True
        elif 30 < credit_score <= 50:
            if data['interest_rate'] > 12:
                approval = True
            else:
                corrected_interest_rate = 12.0
        elif 10 < credit_score <= 30:
            if data['interest_rate'] > 16:
                approval = True
            else:
                corrected_interest_rate = 16.0
        # If score < 10, approval remains False

        # Calculate Monthly Installment (EMI)
        # Formula: EMI = P * r * (1+r)^n / ((1+r)^n - 1)
        # P = Loan Amount, r = monthly interest rate, n = tenure in months
        monthly_interest_rate = (corrected_interest_rate / 100) / 12
        loan_amount = data['loan_amount']
        tenure = data['tenure']
        
        monthly_installment = 0
        if approval:
            if monthly_interest_rate > 0:
                monthly_installment = (loan_amount * monthly_interest_rate * (1 + monthly_interest_rate)**tenure) / ((1 + monthly_interest_rate)**tenure - 1)
            else: # For 0% interest
                monthly_installment = loan_amount / tenure

        response_data = {
            "customer_id": customer.customer_id,
            "approval": approval,
            "interest_rate": data['interest_rate'],
            "corrected_interest_rate": corrected_interest_rate if corrected_interest_rate != data['interest_rate'] else None,
            "tenure": tenure,
            "monthly_installment": round(monthly_installment, 2)
        }

        return Response(response_data)