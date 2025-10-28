import math
from datetime import date
from dateutil.relativedelta import relativedelta
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Customer, Loan
from .serializers import RegisterSerializer, LoanApplicationSerializer, ViewLoanSerializer, ViewCustomerLoansSerializer
from .utils import check_loan_eligibility

class RegisterViewSet(viewsets.ViewSet):
    def create(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        monthly_salary = serializer.validated_data['monthly_salary']
        approved_limit = math.ceil((36 * monthly_salary) / 100000) * 100000
        customer = serializer.save(approved_limit=approved_limit)
        return Response({
            "customer_id": customer.customer_id, "name": f"{customer.first_name} {customer.last_name}",
            "age": customer.age, "monthly_income": customer.monthly_salary,
            "approved_limit": customer.approved_limit, "phone_number": customer.phone_number
        }, status=status.HTTP_201_CREATED)

class EligibilityView(APIView):
    def post(self, request):
        serializer = LoanApplicationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        customer = Customer.objects.get(pk=data.pop('customer_id')) 
        
        eligibility_result = check_loan_eligibility(customer, **data)

        return Response({
            "customer_id": customer.customer_id, "approval": eligibility_result['approved'],
            "interest_rate": data['interest_rate'],
            "corrected_interest_rate": eligibility_result['corrected_interest_rate'] if eligibility_result['corrected_interest_rate'] != data['interest_rate'] else None,
            "tenure": data['tenure'], "monthly_installment": eligibility_result['monthly_installment']
        })

class CreateLoanView(APIView):
    def post(self, request):
        serializer = LoanApplicationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        customer = Customer.objects.get(pk=data.pop('customer_id'))

        eligibility_result = check_loan_eligibility(customer, **data)

        if not eligibility_result['approved']:
            return Response({
                "loan_id": None, "customer_id": customer.customer_id, "loan_approved": False,
                "message": eligibility_result.get('message', 'Loan not approved based on credit score'),
                "monthly_installment": 0
            })

        new_loan = Loan.objects.create(
            customer=customer, loan_amount=data['loan_amount'], tenure=data['tenure'],
            interest_rate=eligibility_result['corrected_interest_rate'],
            monthly_repayment=eligibility_result['monthly_installment'],
            emis_paid_on_time=0, start_date=date.today(),
            end_date=date.today() + relativedelta(months=data['tenure'])
        )
        return Response({
            "loan_id": new_loan.loan_id, "customer_id": customer.customer_id,
            "loan_approved": True, "message": "Loan approved successfully",
            "monthly_installment": eligibility_result['monthly_installment']
        })

class ViewLoanView(APIView):
    def get(self, request, loan_id):
        loan = Loan.objects.get(loan_id=loan_id)
        return Response(ViewLoanSerializer(loan).data)

class ViewCustomerLoansView(APIView):
    def get(self, request, customer_id):
        loans = Loan.objects.filter(customer__customer_id=customer_id)
        return Response(ViewCustomerLoansSerializer(loans, many=True).data)