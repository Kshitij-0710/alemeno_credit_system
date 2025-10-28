# api/utils.py
from .models import Customer, Loan
from django.db.models import Sum
from datetime import date

def calculate_credit_score(customer: Customer):
    current_loans_sum = Loan.objects.filter(
        customer=customer, 
        end_date__gte=date.today()
    ).aggregate(total=Sum('loan_amount'))['total'] or 0

    if current_loans_sum > customer.approved_limit:
        return 0

    score = 100

    total_emis_paid = Loan.objects.filter(customer=customer).aggregate(total=Sum('emis_paid_on_time'))['total'] or 0
    score += min(total_emis_paid, 20) # Add up to 20 points

    loan_count = Loan.objects.filter(customer=customer).count()
    if loan_count > 5:
        score -= 10
    
    current_year_loans = Loan.objects.filter(customer=customer, start_date__year=date.today().year).count()
    if current_year_loans == 0:
        score -= 15 # Penalize for no recent activity
    else:
        score += 5 # Reward for recent activity

    if current_loans_sum > customer.monthly_salary * 10:
        score -= 25

    return max(0, min(100, score)) # Ensure score is between 0 and 100