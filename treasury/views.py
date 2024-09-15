from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
from django.db.models import Sum

from branch.models import CustomerInformation
from treasury.models import Branchs, Currency, TreasuryBills, Withdrawal
from treasury.forms import NewBranchForm, NewCurrencyForm

import csv
import pandas as pd
from datetime import datetime, timedelta
from django.utils.dateparse import parse_date



# Create your views here.
def dashboard(request):
    total_customers = CustomerInformation.objects.count()
    
    # Get the current date
    now = timezone.now()
    
    # Calculate the start and end of the current week
    start_of_week = now - timezone.timedelta(days=now.weekday())  # Monday
    end_of_week = start_of_week + timezone.timedelta(days=6)  # Sunday
    
    total_running_treasury_bills = TreasuryBills.objects.filter(status='1').count()
    total_non_running_treasury_bills = TreasuryBills.objects.filter(status='0').count()
    
    total_face_value = TreasuryBills.objects.filter(status='1').aggregate(total=Sum('face_value'))['total'] or 0
    total_face_value = round(total_face_value, 2)
    
    total_face_value_not_running = TreasuryBills.objects.filter(
        status='0',
        issue_date__range=[start_of_week, end_of_week]
    ).aggregate(total=Sum('customer_amount'))['total'] or 0
    total_face_value_not_running = round(total_face_value_not_running, 2)
    
    non_running_treasury_bills = TreasuryBills.objects.filter(
        status=0
    )
    
    context = {
        'total_customers': total_customers,
        'total_running_treasury_bills': total_running_treasury_bills,
        'total_non_running_treasury_bills': total_non_running_treasury_bills,
        'total_face_value': total_face_value,
        'total_face_value_not_running': total_face_value_not_running,
        'non_running_treasury_bills': non_running_treasury_bills,
    }
    return render(request, 'treasury/index.html', context)
    
    

def branch(request):
    all_branches = Branchs.objects.all()
    all_branch_count = Branchs.objects.all().count()
    if request.method == 'POST':
        form = NewBranchForm(request.POST)
        if form.is_valid():
            branch_code = form.cleaned_data.get('branch_code')
            branch_name = form.cleaned_data.get('branch_name')
            
            # Check if a branch with the same branch_code or branch_name already exists
            if Branchs.objects.filter(branch_code=branch_code).exists() or Branchs.objects.filter(branch_name=branch_name).exists():
                messages.error(request, "Branch with this code or name already exists.")
            else:
                branch = form.save(commit=False)
                branch.save()
                messages.success(request, "Branch has been successfully added.")
                return redirect('/treasury/branch/')
    else:
        form = NewBranchForm()
    
    context = {
        'form': form,
        'all_branches': all_branches,
        'all_branch_count': all_branch_count,
    }
    return render(request, 'treasury/branch.html', context)
    
    
    
def currency(request):
    all_currency = Currency.objects.all()
    all_currency_count = Currency.objects.all().count()
    if request.method == 'POST':
        form = NewCurrencyForm(request.POST)
        if form.is_valid():
            currency_sign = form.cleaned_data.get('currency_sign')
            currency_name = form.cleaned_data.get('currency_name')
            
            # Check if a branch with the same branch_code or branch_name already exists
            if Currency.objects.filter(currency_sign=currency_sign).exists() or Currency.objects.filter(currency_name=currency_name).exists():
                messages.error(request, "Branch with this code or name already exists.")
            else:
                currency = form.save(commit=False)
                currency.save()
                messages.success(request, "Currency has been successfully added.")
                return redirect('/treasury/currency/')
    else:
        form = NewCurrencyForm()
    
    context = {
        'form': form,
        'all_currency': all_currency,
        'all_currency_count': all_currency_count,
    }    
    return render(request, 'treasury/currency.html', context)   




def approve_treasury_bill(request):
    if request.method == 'POST' and request.FILES.get('file_upload'):
        file = request.FILES['file_upload']
        if file.name.endswith('.csv'):
            # Read the CSV file using pandas
            df = pd.read_csv(file)

            # Optional: Validate CSV columns
            expected_columns = [
                'Transaction Code', 'Branch Purchased At', 'Account Domicile Branch',
                'Account Number', 'Account Name', 'Tenor', 'Currency', 'Customer Amount',
                'Maturity Instruction', 'Interest Rate', 'Discount Rate', 'Issue Date',
                'Status', 'Created At'
            ]
            if not all(column in df.columns for column in expected_columns):
                return HttpResponse('CSV file is missing some required columns')

            # Get the current time
            current_time = datetime.now().time()

            # Process each row of the DataFrame
            for _, row in df.iterrows():
                transaction_code = row.get('Transaction Code')

                # Check if the transaction code already exists
                tbill = TreasuryBills.objects.filter(transaction_code=transaction_code).first()

                if tbill:
                    # Update only specified fields
                    tbill.interest_rate = row.get('Interest Rate')
                    tbill.discount_rate = row.get('Discount Rate')

                    # Parse issue_date and add current time
                    issue_date_str = row.get('Issue Date')
                    if issue_date_str:
                        try:
                            # Parse the date and add the current time
                            issue_date = pd.to_datetime(issue_date_str, format='%m/%d/%Y', errors='coerce')
                            if pd.notna(issue_date):
                                issue_date = issue_date.replace(hour=current_time.hour, minute=current_time.minute, second=current_time.second)
                                tbill.issue_date = issue_date
                        except ValueError:
                            return HttpResponse('Invalid date format for Issue Date')

                    # Calculate maturity_date based on tenor
                    tenor_days = row.get('Tenor')
                    if pd.notna(tenor_days):
                        tenor_days = int(tenor_days)  # Convert tenor to integer if it's not null
                        if tbill.issue_date:
                            tbill.maturity_date = tbill.issue_date + timedelta(days=tenor_days)

                    # Calculate face_value based on the provided formula
                    customer_amount = row.get('Customer Amount')
                    interest_rate = row.get('Interest Rate')
                    if pd.notna(customer_amount) and pd.notna(interest_rate):
                        customer_amount = float(customer_amount)
                        interest_rate = float(interest_rate)
                        face_value = round((customer_amount * (interest_rate / 100) * tenor_days / 364) + customer_amount, 2)
                        tbill.face_value = face_value

                    # Calculate lcy_amount based on the provided formula
                    discount_rate = row.get('Discount Rate')
                    if pd.notna(discount_rate):
                        discount_rate = float(discount_rate)
                        lcy_amount = abs(face_value * (1 - (discount_rate / 100) * tenor_days / 364))
                        tbill.lcy_amount = round(lcy_amount, 2)
                    tbill.roll_over_instruction = None
                    tbill.save(update_fields=['interest_rate', 'discount_rate', 'issue_date', 'maturity_date', 'face_value', 'lcy_amount'])

            return HttpResponse('CSV file processed successfully')
        else:
            return HttpResponse('Invalid file format')

    return render(request, 'treasury/treasury-bill-approval.html')






def export_treasury_bills_to_csv(request):
    # Get the date range from the GET request
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    # Parse the dates
    if from_date:
        from_date = parse_date(from_date)
    if to_date:
        to_date = parse_date(to_date)

    # Filter the records based on the selected date range
    t_bills_with_null_fields = TreasuryBills.objects.filter(
        interest_rate__isnull=True,
        discount_rate__isnull=True,
        issue_date__isnull=True
    )

    if from_date and to_date:
        t_bills_with_null_fields = t_bills_with_null_fields.filter(
            created_at__range=[from_date, to_date]
        )
    elif from_date:
        t_bills_with_null_fields = t_bills_with_null_fields.filter(
            created_at__gte=from_date
        )
    elif to_date:
        t_bills_with_null_fields = t_bills_with_null_fields.filter(
            created_at__lte=to_date
        )

    # Create the HttpResponse object with the appropriate CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="t_bills.csv"'

    # Create a CSV writer
    writer = csv.writer(response)

    # Define the CSV column headers
    headers = [
        'Transaction Code', 'Branch Purchased At', 'Account Domicile Branch', 
        'Account Number', 'Account Name', 'Tenor', 'Currency', 'Customer Amount', 
        'Maturity Instruction', 'Interest Rate', 
        'Discount Rate', 'Issue Date', 'Status', 'Created At'
    ]
    writer.writerow(headers)  # Write the header row

    # Write each record to the CSV
    for t_bill in t_bills_with_null_fields:
        writer.writerow([
            t_bill.transaction_code,
            t_bill.branch_purchased_at,
            t_bill.account_domicile_branch.branch_name,
            t_bill.account_number.account_number,
            t_bill.account_number,
            t_bill.tenor,
            t_bill.currency.currency_sign,
            t_bill.customer_amount,
            t_bill.maturity_instruction,
            t_bill.interest_rate,
            t_bill.discount_rate,
            t_bill.issue_date,
            t_bill.status,
            t_bill.created_at,
        ])

    return response



def delete_treasury_bill(request, slug):
    # Retrieve the TreasuryBill instance based on the slug
    delete_instance = get_object_or_404(TreasuryBills, slug=slug)
    delete_instance.delete()
    messages.success(request, 'Treasury Bill deleted successfully!')
    return redirect('/treasury/treasury-bill/')
    


    
def treasury_bill(request):
    all_treasury_bills = TreasuryBills.objects.all()
    context = {
        'all_treasury_bills': all_treasury_bills,
    }
    return render(request, 'treasury/treasury-bills.html', context)
    
    
    
def withdrawal_list(request):
    withdrawals = Withdrawal.objects.all()
    return render(request, 'treasury/withdrawals.html', {'withdrawals': withdrawals})
