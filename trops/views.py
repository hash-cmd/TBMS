from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
from django.db.models import Sum, Q
from django.contrib.auth.decorators import login_required
from branch.models import CustomerInformation
from branch.forms import EditCustomerForm
from trops.forms import BOGWeeklyForm
from treasury.models import Branchs, Currency, TreasuryBills, Withdrawal, TransactionDetails, BOG_Weekly_Code
from treasury.forms import NewBranchForm, NewCurrencyForm

import csv
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from django.utils.dateparse import parse_date


# Create your views here.
@login_required(login_url='/')  
def dashboard(request):
    total_customers = CustomerInformation.objects.count()

    now = timezone.now()

    start_of_week = now - timezone.timedelta(days=now.weekday())  
    end_of_week = start_of_week + timezone.timedelta(days=4)  

    start_of_week = timezone.make_aware(datetime.combine(start_of_week, datetime.min.time()))
    end_of_week = timezone.make_aware(datetime.combine(end_of_week, datetime.max.time()))

    total_requests = TreasuryBills.objects.filter(
        Q(status='0')
    )
    total_requests_amount = total_requests.aggregate(total=Sum('lcy_amount'))['total'] or 0
    total_requests_amount = round(total_requests_amount, 2)

    total_running_treasury_bills = TreasuryBills.objects.filter(status='1').count()
    total_non_running_treasury_bills = TreasuryBills.objects.filter(status='0').count()

    total_face_value = TreasuryBills.objects.aggregate(total=Sum('face_value'))['total'] or 0
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
    
    return render(request, 'trops/index.html', context)
    

@login_required(login_url='/')  
def treasury_bill(request):
    all_treasury_bills = TreasuryBills.objects.all().order_by('-issue_date')    
    context = {
        'all_treasury_bills': all_treasury_bills,
    }
    return render(request, 'trops/treasury-bills.html', context)

@login_required(login_url='/')  
def all_transactions(request):
    transactions = TransactionDetails.objects.all()
    return render(request, 'trops/all-transactions.html', {'transactions': transactions})


@login_required(login_url='/')  
def export_treasury_bills_to_csv(request):
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if from_date:
        from_date = parse_date(from_date)
    if to_date:
        to_date = parse_date(to_date)

    t_bills_with_null_fields = TreasuryBills.objects.filter(
        interest_rate__isnull=False,
        discount_rate__isnull=False,
        issue_date__isnull=False,
        status=0  
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

    today_date = datetime.today().strftime('%Y-%m-%d')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="UPLOAD_XNETT_{today_date}.csv"'

    writer = csv.writer(response)

    headers = [
        'ACCOUNT','CCY', 'DR_CR', 'TRANSACTION DETAILS', 
        'LCY_AMOUNT', 'ACC_BRANCH', 'FCY_AMOUNT', 'MIS_CODE', 
        'RELATED_ACCOUNT', 'CUST_ID', 'TRANS_CODE', 'SN', 'INSTRUMENT', 'STATUS'
    ]

    bog_code = BOG_Weekly_Code.objects.first()
    if bog_code:
        writer.writerow(headers)
        
        for t_bill in t_bills_with_null_fields:
            writer.writerow([
                f"'{t_bill.account_number.account_number}" if t_bill.account_number.account_number else '',
                t_bill.currency.currency_sign if t_bill.currency else '',
                'Not Debited',
                f'{t_bill.tenor}DAY TBILL @{t_bill.interest_rate}% (GOG-BL-{t_bill.issue_date.strftime("%Y-%m-%d")}-{bog_code}-191GHS{t_bill.face_value})',
                t_bill.lcy_amount,
                t_bill.account_domicile_branch.branch_code if t_bill.account_domicile_branch else '',
                '',
                '',
                f"'{t_bill.account_number.account_number}" if t_bill.account_number.account_number else '',
                '',
                '033',
                t_bill.id,
                '',
                t_bill.status,
            ])
    else:
        print("No BOG code available")

    return response



@login_required(login_url='/')  
def debit_treasury_bill(request):
    if request.method == 'POST' and request.FILES['file']:
        csv_file = request.FILES['file']
        df = pd.read_csv(csv_file)

        headers = [
            'ACCOUNT', 'CCY', 'DR_CR', 'TRANSACTION DETAILS', 
            'LCY_AMOUNT', 'ACC_BRANCH', 'FCY_AMOUNT', 'MIS_CODE', 
            'RELATED_ACCOUNT', 'CUST_ID', 'TRANS_CODE', 'SN', 'INSTRUMENT',
        ]

        if not all(header in df.columns for header in headers):
            return HttpResponse('CSV file is missing some required columns')

        for _, row in df.iterrows():
            data = {
                'account_number': row.get('ACCOUNT'),
                'ccy': row.get('CCY'),
                'dr_cr': row.get('DR_CR'),
                'transaction_details': row.get('Transaction Details'),
                'lcy_amount': row.get('LCY_AMOUNT') if not pd.isna(row.get('LCY_AMOUNT')) else None,
                'acc_branch': row.get('ACC_BRANCH'),
                'fcy_amount': row.get('FCY_AMOUNT') if not pd.isna(row.get('FCY_AMOUNT')) else None,
                'mis_code': row.get('MIS_CODE'),
                'related_account': row.get('RELATED_ACCOUNT'),
                'cust_id': row.get('CUST_ID'),
                'trans_code': row.get('TRANS_CODE'),
                'sn': row.get('SN') if not pd.isna(row.get('SN')) else None,
                'instrument': row.get('INSTRUMENT'),
            }

            try:
                if data['sn'] is not None:
                    data['sn'] = int(data['sn'])
            except ValueError as e:
                return HttpResponse(f'Invalid value for SN: {data["sn"]}')

            transaction_details, created = TransactionDetails.objects.update_or_create(
                trans_code=data['trans_code'],
                defaults=data
            )

            tbill = TreasuryBills.objects.filter(transaction_code=data['trans_code']).first()
            if tbill:
                tbill.status = 1 
                tbill.save()

        return HttpResponse('CSV file processed and data uploaded successfully')
    
    return render(request, 'trops/treasury-bill-approval.html')


@login_required(login_url='/')  
def edit_customer(request, slug):
    customer = get_object_or_404(CustomerInformation, slug=slug)

    if request.method == 'POST':
        form = EditCustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer information has been updated successfully!')
            return redirect('/trops/customers/all/') 
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EditCustomerForm(instance=customer)

    return render(request, 'trops/edit-customer.html', {
        'form': form,
        'customer': customer
    })


@login_required(login_url='/')         
def customers_all(request):
    customers = CustomerInformation.objects.all()
    with_csd = CustomerInformation.objects.filter(csd_number__isnull=False)
    without_csd = CustomerInformation.objects.filter(csd_number__isnull=True)
    context = {
        'all_custumers': customers,
        'all_with_csd': with_csd,
        'all_without_csd': without_csd,
    }
    return render(request, 'trops/customers.html', context)



@login_required(login_url='/')         
def bog_code(request):
    weekly_code_instance = BOG_Weekly_Code.objects.all()

    if request.method == 'POST':
        form = BOGWeeklyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Treasury Bill Weekly Code has been updated successfully!')
            return redirect('/trops/treasury-bill/code/')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BOGWeeklyForm()

    context = {
        'form': form,
        'weekly_code':  weekly_code_instance,  
    }
    return render(request, 'trops/bog_code.html', context)


@login_required(login_url='/')         
def delete_bog_code(request, id):
    instance=get_object_or_404(BOG_Weekly_Code, id=id)
    instance.delete()
    messages.success(request, 'Treasury Bill Weekly Code has been Deleted successfully!')
    return redirect('/trops/treasury-bill/code/')