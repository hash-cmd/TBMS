from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
from django.db.models import Sum, Q
from django.contrib.auth.decorators import login_required

from branch.models import CustomerInformation
from treasury.models import Branchs, Currency, TreasuryBills, Withdrawal, TransactionDetails
from treasury.forms import NewBranchForm, NewCurrencyForm

import csv
import pandas as pd
from datetime import datetime, timedelta
from django.utils.dateparse import parse_date, parse_datetime


@login_required(login_url='/')  
def dashboard(request):
    total_customers = CustomerInformation.objects.count()

    now = timezone.now()

    start_of_week = now - timezone.timedelta(days=now.weekday()) 
    end_of_week = start_of_week + timezone.timedelta(days=4) 

    start_of_week = timezone.make_aware(datetime.combine(start_of_week, datetime.min.time()))
    end_of_week = timezone.make_aware(datetime.combine(end_of_week, datetime.max.time()))

    total_requests = TreasuryBills.objects.filter(
        Q(created_at__range=(start_of_week, end_of_week)) &
        Q(status='0')
    )
    total_requests_amount = total_requests.aggregate(total=Sum('customer_amount'))['total'] or 0
    total_requests_amount = round(total_requests_amount, 2)

    total_running_treasury_bills = TreasuryBills.objects.filter(status='1').count()
    total_non_running_treasury_bills = TreasuryBills.objects.filter(status='0').count()

    total_face_value = TreasuryBills.objects.filter(status='1').aggregate(total=Sum('face_value'))['total'] or 0
    total_face_value = round(total_face_value, 2)

    context = {
        'total_customers': total_customers,
        'total_requests': total_requests,
        'total_requests_count': total_requests.count(),
        'total_running_treasury_bills': total_running_treasury_bills,
        'total_non_running_treasury_bills': total_non_running_treasury_bills,
        'total_requests_amount': total_requests_amount,
        'total_face_value': total_face_value,
    }                                                
    
    return render(request, 'treasury/index.html', context)
    
    
@login_required(login_url='/')  
def branch(request):
    all_branches = Branchs.objects.all()
    all_branch_count = Branchs.objects.all().count()
    if request.method == 'POST':
        form = NewBranchForm(request.POST)
        if form.is_valid():
            branch_code = form.cleaned_data.get('branch_code')
            branch_name = form.cleaned_data.get('branch_name')
            
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
    
    
@login_required(login_url='/')    
def currency(request):
    all_currency = Currency.objects.all()
    all_currency_count = Currency.objects.all().count()
    if request.method == 'POST':
        form = NewCurrencyForm(request.POST)
        if form.is_valid():
            currency_sign = form.cleaned_data.get('currency_sign')
            currency_name = form.cleaned_data.get('currency_name')
            
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
    
    


@login_required(login_url='/')  
def approve_single_treasury_bill(request):
    if request.method == 'POST':
        # Retrieve the data from the POST request
        transaction_code = request.POST.get('transaction_code')
        interest_rate = request.POST.get('interest_rate')
        discount_rate = request.POST.get('discount_rate')
        issue_date = request.POST.get('issue_date')

        try:
            treasury_bill_request = TreasuryBills.objects.get(transaction_code=transaction_code)
            customer_amount = float(treasury_bill_request.customer_amount)

            tenor_days = treasury_bill_request.tenor
            face_value = round((customer_amount * (float(interest_rate) / 100) * tenor_days / 364) + customer_amount, 2)

            print(f"Calculated Face Value: {face_value}")

            discount_rate = float(discount_rate)
            lcy_amount = abs(face_value * (1 - (discount_rate / 100) * tenor_days / 364))

            treasury_bill_request.face_value = face_value
            treasury_bill_request.lcy_amount = lcy_amount
            treasury_bill_request.interest_rate = interest_rate
            treasury_bill_request.discount_rate = discount_rate
            
            issue_date_dt = pd.to_datetime(issue_date, format='%m/%d/%Y', errors='coerce')
            if pd.notna(issue_date_dt):
                current_time = timezone.now()
                issue_date_with_time = issue_date_dt.replace(hour=current_time.hour, minute=current_time.minute, second=current_time.second)

                treasury_bill_request.issue_date = issue_date_with_time
                treasury_bill_request.maturity_date = issue_date_with_time + timedelta(days=tenor_days)

            treasury_bill_request.save()

            print("Treasury Bill approved and updated successfully.")

            messages.success(request, 'Treasury Bill approved and updated successfully.')
            return redirect('/treasury/treasury-bill/')

        except TreasuryBills.DoesNotExist:
            messages.error(request, 'Treasury Bill does not exist!')
            return redirect('/treasury/treasury-bill/')

        except Exception as e:
            messages.error(request, 'Treasury Bill Error!')
            return redirect('/treasury/treasury-bill/')

    return redirect('/treasury/treasury-bill/')





@login_required(login_url='/')  
def approve_treasury_bill(request):
    if request.method == 'POST' and request.FILES.get('file_upload'):
        file = request.FILES['file_upload']
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)

            expected_columns = [
                'Transaction Code', 'Branch Purchased At', 'Account Domicile Branch',
                'Account Number', 'Account Name', 'Tenor', 'Currency', 'Customer Amount',
                'Maturity Instruction', 'Interest Rate', 'Discount Rate', 'Issue Date',
                'Status', 'Created At'
            ]
            if not all(column in df.columns for column in expected_columns):
                return HttpResponse('CSV file is missing some required columns')

            current_time = datetime.now().time()

            for _, row in df.iterrows():
                transaction_code = row.get('Transaction Code')

                tbill = TreasuryBills.objects.filter(transaction_code=transaction_code).first()

                if tbill:
                    tbill.interest_rate = row.get('Interest Rate')
                    tbill.discount_rate = row.get('Discount Rate')

                    issue_date_str = row.get('Issue Date')
                    if issue_date_str:
                        try:
                            issue_date = pd.to_datetime(issue_date_str, format='%m/%d/%Y', errors='coerce')
                            if pd.notna(issue_date):
                                issue_date = issue_date.replace(hour=current_time.hour, minute=current_time.minute, second=current_time.second)
                                tbill.issue_date = issue_date
                        except ValueError:
                            return HttpResponse('Invalid date format for Issue Date')

                    tenor_days = row.get('Tenor')
                    if pd.notna(tenor_days):
                        tenor_days = int(tenor_days)
                        if tbill.issue_date:
                            tbill.maturity_date = tbill.issue_date + timedelta(days=tenor_days)

                    customer_amount = row.get('Customer Amount')
                    interest_rate = row.get('Interest Rate')
                    if pd.notna(customer_amount) and pd.notna(interest_rate):
                        customer_amount = float(customer_amount)
                        interest_rate = float(interest_rate)
                        face_value = round((customer_amount * (interest_rate / 100) * tenor_days / 364) + customer_amount)
                        tbill.face_value = face_value

                    discount_rate = row.get('Discount Rate')
                    if pd.notna(discount_rate):
                        discount_rate = float(discount_rate)
                        lcy_amount = abs(face_value * (1 - (discount_rate / 100) * tenor_days / 364))
                        tbill.lcy_amount = lcy_amount
                    tbill.roll_over_instruction = None
                    tbill.save(update_fields=['interest_rate', 'discount_rate', 'issue_date', 'maturity_date', 'face_value', 'lcy_amount'])

            return HttpResponse('CSV file processed successfully')
        else:
            return HttpResponse('Invalid file format')

    return render(request, 'treasury/treasury-bill-approval.html')



@login_required(login_url='/')  
def export_treasury_bills_to_csv(request):
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if from_date:
        from_date = parse_date(from_date)
    if to_date:
        to_date = parse_date(to_date)

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

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="PENDING_TREASURY_BILLS.csv"'

    writer = csv.writer(response)
    headers = [
        'Transaction Code', 'Branch Purchased At', 'Account Domicile Branch', 
        'Account Number', 'Account Name', 'Tenor', 'Currency', 'Customer Amount', 
        'Maturity Instruction', 'Interest Rate', 
        'Discount Rate', 'Issue Date', 'Status', 'Created At'
    ]
    writer.writerow(headers)  
    for t_bill in t_bills_with_null_fields:

        if t_bill.maturity_instruction == 1:
            maturity_instruction_text = 'Pay Principal & Interest on Maturity'
        elif t_bill.maturity_instruction == 2:
            maturity_instruction_text = 'Roll - Over with Interest on Maturity'
        elif t_bill.maturity_instruction == 3:
            maturity_instruction_text = 'Roll - Over Principal only on Maturity'
        else:
            maturity_instruction_text = t_bill.maturity_instruction  
    
        writer.writerow([
            t_bill.transaction_code,
            t_bill.branch_purchased_at,
            t_bill.account_domicile_branch.branch_name,
            t_bill.account_number.account_number,
            t_bill.account_number,
            t_bill.tenor,
            t_bill.currency.currency_sign,
            t_bill.customer_amount,
             maturity_instruction_text,
            t_bill.interest_rate,
            t_bill.discount_rate,
            t_bill.issue_date,
            t_bill.status,
            t_bill.created_at,
        ])

    return response




@login_required(login_url='/')  
def delete_treasury_bill(request, slug):
    delete_instance = get_object_or_404(TreasuryBills, slug=slug)
    delete_instance.delete()
    messages.success(request, 'Treasury Bill deleted successfully!')
    return redirect('/treasury/treasury-bill/')
    


@login_required(login_url='/')    
def treasury_bill(request):
    all_treasury_bills = TreasuryBills.objects.all()
    context = {
        'all_treasury_bills': all_treasury_bills,
    }
    return render(request, 'treasury/treasury-bills.html', context)
    
    
@login_required(login_url='/')   
def withdrawal_list(request):
    withdrawals = Withdrawal.objects.all()
    return render(request, 'treasury/withdrawals.html', {'withdrawals': withdrawals})

@login_required(login_url='/')  
def all_transactions(request):
    transactions = TransactionDetails.objects.all()
    return render(request, 'treasury/all-transactions.html', {'transactions': transactions})
 
