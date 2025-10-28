from datetime import date
from django.db.models import Sum
from .models import Customer, Loan

def calculate_credit_score(customer: Customer):
    """
    Calculates a credit score for a customer based on their loan history.
    """
    current_loans_sum = Loan.objects.filter(
        customer=customer, 
        end_date__gte=date.today()
    ).aggregate(total=Sum('loan_amount'))['total'] or 0

    if current_loans_sum > customer.approved_limit:
        return 0

    score = 100

    total_emis_paid = Loan.objects.filter(customer=customer).aggregate(total=Sum('emis_paid_on_time'))['total'] or 0
    score += min(total_emis_paid, 20)

    loan_count = Loan.objects.filter(customer=customer).count()
    if loan_count > 5:
        score -= 10
    
    current_year_loans = Loan.objects.filter(customer=customer, start_date__year=date.today().year).count()
    if current_year_loans == 0:
        score -= 15
    else:
        score += 5

    if current_loans_sum > customer.monthly_salary * 10:
        score -= 25

    return max(0, min(100, score))


def check_loan_eligibility(customer: Customer, loan_amount: float, interest_rate: float, tenure: int):
    """
    Checks if a customer is eligible for a loan and returns the approval status and terms.
    """
    credit_score = calculate_credit_score(customer)

    # high debt check
    current_emis = Loan.objects.filter(customer=customer, end_date__gte=date.today()).aggregate(total=Sum('monthly_repayment'))['total'] or 0
    if current_emis > customer.monthly_salary * 0.5:
        return {"approved": False, "message": "High debt burden"}

    # credit score approval logic
    approved = False
    corrected_interest_rate = interest_rate
    if credit_score > 50:
        approved = True
    elif 30 < credit_score <= 50:
        if interest_rate > 12:
            approved = True
        else:
            corrected_interest_rate = 12.0
    elif 10 < credit_score <= 30:
        if interest_rate > 16:
            approved = True
        else:
            corrected_interest_rate = 16.0
    
    # calculate EMI if approved
    monthly_installment = 0
    if approved:
        r = (corrected_interest_rate / 100) / 12  
        p = loan_amount                           
        n = tenure                                
        
        if r > 0:
            monthly_installment = (p * r * (1 + r)**n) / ((1 + r)**n - 1)
        else:
            monthly_installment = p / n

    return {
        "approved": approved,
        "corrected_interest_rate": corrected_interest_rate,
        "monthly_installment": round(monthly_installment, 2)
    }