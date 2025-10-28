import math
from datetime import date
from django.db.models import Sum
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Customer, Loan
from .serializers import RegisterSerializer, EligibilitySerializer
from .utils import calculate_credit_score

class RegisterViewSet(viewsets.ViewSet):
    def create(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        monthly_salary = serializer.validated_data['monthly_salary']
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


class EligibilityView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = EligibilitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        customer = Customer.objects.get(pk=data['customer_id'])
        credit_score = calculate_credit_score(customer)

        current_emis = Loan.objects.filter(customer=customer, end_date__gte=date.today()).aggregate(Sum('monthly_repayment'))['total'] or 0
        if current_emis > customer.monthly_salary * 0.5:
            return Response({"approval": False, "message": "High debt burden"})

        approval = False
        corrected_interest_rate = data['interest_rate']
        if credit_score > 50: approval = True
        elif 30 < credit_score <= 50:
            if data['interest_rate'] > 12: approval = True
            else: corrected_interest_rate = 12.0
        elif 10 < credit_score <= 30:
            if data['interest_rate'] > 16: approval = True
            else: corrected_interest_rate = 16.0
        
        monthly_installment = 0
        if approval:
            r = (corrected_interest_rate / 100) / 12
            p = data['loan_amount']
            n = data['tenure']
            monthly_installment = (p * r * (1 + r)**n) / ((1 + r)**n - 1) if r > 0 else p / n

        response_data = {
            "customer_id": customer.customer_id, "approval": approval,
            "interest_rate": data['interest_rate'],
            "corrected_interest_rate": corrected_interest_rate if corrected_interest_rate != data['interest_rate'] else None,
            "tenure": data['tenure'], "monthly_installment": round(monthly_installment, 2)
        }
        return Response(response_data)