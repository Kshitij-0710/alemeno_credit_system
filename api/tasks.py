from celery import shared_task
import pandas as pd
from .models import Customer, Loan
from django.db import transaction

@shared_task
def ingest_data_task():
    try:
        #ingest customer stuff
        customer_df = pd.read_excel('customer_data.xlsx')
        with transaction.atomic():
            for _, row in customer_df.iterrows():
                Customer.objects.update_or_create(
                    customer_id=row['customer_id'],
                    defaults={
                        'first_name': row['first_name'],
                        'last_name': row['last_name'],
                        'phone_number': row['phone_number'],
                        'monthly_salary': row['monthly_salary'],
                        'approved_limit': row['approved_limit'],
                        'current_debt': row['current_debt'],
                    }
                )

        #ingest loan stuff
        loan_df = pd.read_excel('loan_data.xlsx')
        with transaction.atomic():
            for _, row in loan_df.iterrows():
                customer = Customer.objects.get(customer_id=row['customer_id'])
                Loan.objects.update_or_create(
                    loan_id=row['loan_id'],
                    defaults={
                        'customer': customer,
                        'loan_amount': row['loan_amount'],
                        'tenure': row['tenure'],
                        'interest_rate': row['interest_rate'],
                        'monthly_repayment': row['monthly_payment'],
                        'emis_paid_on_time': row['emis_paid_on_time'],
                        'start_date': row['start_date'],
                        'end_date': row['end_date'],
                    }
                )
        return "Data ingestion successful."
    except Exception as e:
        return f"An error occurred: {str(e)}"