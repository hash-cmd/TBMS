from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.utils import  timezone
from django.utils.timezone import make_aware
from datetime import datetime, timedelta
from django.http import HttpResponseRedirect, JsonResponse
import re
from django.contrib.auth.decorators import login_required

from branch.forms import NewCustomerForm, EditCustomerForm, NewTreasuryBillForm, EditTreasuryBillForm
from django.db.models import Sum, Q
from branch.models import CustomerInformation 
from treasury.models import MaturedTBills, TreasuryBills, Branchs, Currency, Withdrawal, TransactionDetails

from dal import autocomplete
from django.core.mail import send_mail
from django.conf import settings



# Create your views here.
class CustomerAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Check for user permissions if needed
        #if not self.request.user.is_authenticated:
        #    return CustomerInformation.objects.none()

        qs = CustomerInformation.objects.all()

        if self.q:
            qs = qs.filter(account_number__icontains=self.q)
        return qs



@login_required(login_url='/')
def dashboard(request):
    today = datetime.today()
    current_weekday = today.weekday()
    start_of_week = today - timedelta(days=current_weekday)  # Monday
    end_of_week = start_of_week + timedelta(days=3)  # Thursday
    
    start_of_week = make_aware(start_of_week)
    end_of_week = make_aware(end_of_week)
    
    # Query for this week's treasury bills
    this_week_t_bills = TreasuryBills.objects.filter(
        created_at__range=[start_of_week, end_of_week]
    )
    
    user_branch = request.user.branch_code
    all_branch_customers = CustomerInformation.objects.all()
    total_customers_in_branch = all_branch_customers.count()
    
    running_branch_t_bills = TreasuryBills.objects.filter(account_domicile_branch__branch_code=user_branch).aggregate(total=Sum('lcy_amount'))['total'] or 0
    running_branch_t_bills_count = TreasuryBills.objects.filter(
        Q(account_domicile_branch__branch_code=user_branch) &
        Q(status=1)
        ).count() 
    running_branch_t_bills = round(running_branch_t_bills, 2)
    matured_count = MaturedTBills.objects.filter(branch_purchased_at=user_branch).count()
    
    return render(request, 'branch/index.html', {
        'this_week_t_bills': this_week_t_bills,
        'total_customers_in_branch': total_customers_in_branch,
        'running_branch_t_bills': running_branch_t_bills,
        'running_branch_t_bills_count': running_branch_t_bills_count,
        'matured_count': matured_count,
    })

    


@login_required(login_url='/')
def new_treasury_bill(request):
    all_currency = Currency.objects.all()
    all_branch = Branchs.objects.all()

    if request.method == 'POST':
        form = NewTreasuryBillForm(request.POST, request.FILES)
        if form.is_valid():
            treasury_bill = form.save(commit=False)
        
            treasury_bill.transaction_code = '033'
            
            account_number = form.cleaned_data.get('account_number')
            if account_number:
                try:
                    customer_info = CustomerInformation.objects.get(account_number=account_number)
                    treasury_bill.account_number = customer_info
                except CustomerInformation.DoesNotExist:
                    pass
            
            treasury_bill.save()
            messages.success(request, 'Treasury Bill created successfully!')
            return redirect('/branch/treasury-bill/new/')
        else:
            print(form.errors)  
    else:
        form = NewTreasuryBillForm()

    context = {
        'form': form,
        'all_currency': all_currency,
        'all_branch': all_branch,
    }
    return render(request, 'branch/treasury/new-treasury-bill.html', context)
    
    
    
@login_required(login_url='/')    
def edit_treasury_bill(request, slug):
    instance = get_object_or_404(TreasuryBills, slug=slug)
    all_branch = Branchs.objects.all()
    if request.method == 'POST':
        form = EditTreasuryBillForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Treasury Bill updated successfully.')
            return redirect('/branch/treasury-bill/')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EditTreasuryBillForm(instance=instance)
    
    return render(request, 'branch/treasury/edit-treasury-bill.html', {'form': form,  'all_branch': all_branch,})    
    
    
    
  
@login_required(login_url='/')
def update_t_bill_rollover_with_interest(request, slug):
    update_instance = get_object_or_404(TreasuryBills, slug=slug)
    
    # Update the instance
    update_instance.roll_over_instruction = '1'
    update_instance.maturity_instruction = 2
    update_instance.save()
    
    # Sending email
    subject = 'Treasury Bill Roll-Over Update'
    message = f'The Treasury Bill with transaction code {update_instance.transaction_code} has been successfully updated with a roll-over instruction to rollover principal and interest'
    recipient_list = ['Treasury@omnibsic.com.gh']  # Replace with the actual recipient's email
    from_email = settings.DEFAULT_FROM_EMAIL  # Ensure your settings.py has the correct email setup
    
    send_mail(subject, message, from_email, recipient_list, fail_silently=False)

    messages.success(request, 'Treasury Bill Updated successfully!')
    
    return redirect('/branch/notify/')


@login_required(login_url='/')
def update_t_bill_rollover_principal(request, slug):
    
    update_instance = get_object_or_404(TreasuryBills, slug=slug)
    update_instance.roll_over_instruction = '1'
    update_instance.maturity_instruction = 3
    update_instance.save()
    
    # Sending email
    subject = 'Treasury Bill Roll-Over Update'
    message = f'The Treasury Bill with transaction code {update_instance.transaction_code} has been successfully updated with a roll-over instruction to only roll over the principal'
    recipient_list = ['Treasury@omnibsic.com.gh']  # Replace with the actual recipient's email
    from_email = settings.DEFAULT_FROM_EMAIL  # Ensure your settings.py has the correct email setup
    
    send_mail(subject, message, from_email, recipient_list, fail_silently=False)
    
    messages.success(request, 'Treasury Bill Updated successfully!')
    return redirect('/branch/notify/')

@login_required(login_url='/')
def update_t_bill_do_not_rollover(request, slug):
    
    update_instance = get_object_or_404(TreasuryBills, slug=slug)
    update_instance.roll_over_instruction = '0'
    update_instance.maturity_instruction = 1
    update_instance.save()
    
    # Sending email
    subject = 'Treasury Bill Roll-Over Update'
    message = f'The Treasury Bill with transaction code {update_instance.transaction_code} has been successfully updated not to to rollover at maturity'
    recipient_list = ['Treasury@omnibsic.com.gh']  # Replace with the actual recipient's email
    from_email = settings.DEFAULT_FROM_EMAIL  # Ensure your settings.py has the correct email setup
    
    send_mail(subject, message, from_email, recipient_list, fail_silently=False)
    
    messages.success(request, 'Treasury Bill Updated successfully!')
    return redirect('/branch/notify/')
    

login_required(login_url='/')
def terminate_t_bill(request, slug):
    # Get the TreasuryBills instance using the slug
    termination_instance = get_object_or_404(TreasuryBills, slug=slug)
    
    # Update the TreasuryBills instance
    termination_instance.roll_over_instruction = '3'
    termination_instance.maturity_instruction = 1
    termination_instance.save()

    subject = 'Treasury Bill Termination'
    message = f'The Treasury Bill with transaction code ({termination_instance.transaction_code}) and Account Number {termination_instance.account_number.account_number} has instructed {request.user.username} to terminate.'
    recipient_list = ['Treasury@omnibsic.com.gh']  # Replace with the actual recipient's email
    from_email = settings.DEFAULT_FROM_EMAIL 
    
    send_mail(subject, message, from_email, recipient_list, fail_silently=False)
    
    # Create a Withdrawal instance
    withdrawal = Withdrawal(
        transaction_code=termination_instance.transaction_code,
        branch_purchased_at=termination_instance.branch_purchased_at,
        account_domicile_branch=termination_instance.account_domicile_branch,
        account_number=termination_instance.account_number.account_number,
        tenor=termination_instance.tenor,
        currency=termination_instance.currency,
        customer_amount=termination_instance.customer_amount,
        maturity_instruction=termination_instance.maturity_instruction,
        lcy_amount=termination_instance.lcy_amount,
        interest_rate=termination_instance.interest_rate,
        discount_rate=termination_instance.discount_rate,
        face_value=termination_instance.face_value,
        issue_date=termination_instance.issue_date,
        maturity_date=termination_instance.maturity_date,
        roll_over_instruction='Do not roll over',  # Assuming '2' for Terminate
        created_by=request.user.username,  # Set the created_by field with the current user's username
    )
    
    # Save the Withdrawal instance
    withdrawal.save()
    
    # Success message and redirect
    messages.success(request, 'Treasury Bill Terminated successfully!')
    return redirect('/branch/treasury-bill/')

@login_required(login_url='/')
def withdrawal_list(request):
    withdrawals = Withdrawal.objects.all()
    return render(request, 'branch/treasury/withdrawal-list.html', {'withdrawals': withdrawals})

@login_required(login_url='/')
def delete_treasury_bill(request, slug):
    # Retrieve the TreasuryBill instance based on the slug
    delete_instance = get_object_or_404(TreasuryBills, slug=slug)
    delete_instance.delete()
    messages.success(request, 'Treasury Bill deleted successfully!')
    return redirect('/branch/treasury-bill/')

login_required(login_url='/')
def get_treasury_bills_due_next_week():
    today = timezone.now().date()
    end_of_week = today + timedelta(weeks=1)
    
    # Query for records where maturity_date is within the next week
    due_next_week = TreasuryBills.objects.filter(
        maturity_date__date__range=[today, end_of_week]
    )
    
    return due_next_week

@login_required(login_url='/')
def notify_treasury_bill(request):
    all_treasury_bills = get_treasury_bills_due_next_week()
    
    context = {
        'all_treasury_bills': all_treasury_bills
    }
    
    return render(request, 'branch/treasury/reinvest-treasury-bill.html', context)


login_required(login_url='/')
def treasury_bill(request):
    all_treasury_bills = TreasuryBills.objects.all()
    context = {
        'all_treasury_bills': all_treasury_bills,
    }
    return render(request, 'branch/treasury/requested-treasury-bill.html', context)

@login_required(login_url='/')    
def all_transactions(request):
    transactions = TransactionDetails.objects.all()
    return render(request, 'branch/treasury/all-transactions.html', {'transactions': transactions})
 
    

@login_required(login_url='/')
def new_customer(request):
    all_branch = Branchs.objects.all()
    if request.method == 'POST':
        form = NewCustomerForm(request.POST, request.FILES)
        if form.is_valid():
            account_number = form.cleaned_data.get('account_number')
            
            if CustomerInformation.objects.filter(account_number=account_number).exists():
                messages.error(request, "An account with this number already exists.")
                return redirect('/branch/customer/new/')
            else:
                form.save()
                messages.success(request, "New Customer Information Added Successfully.")
                return redirect('/branch/customer/new/')
        else:
            messages.error(request, "There were errors in your form submission.")
    else:
        form = NewCustomerForm()

    context = {
        'form': form,
        'all_branch': all_branch,
    }
    return render(request, 'branch/customers/new-customer.html', context)


@login_required(login_url='/')
def edit_customer(request, slug):
    customer = get_object_or_404(CustomerInformation, slug=slug)

    if request.method == 'POST':
        form = EditCustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer information has been updated successfully!')
            return redirect('/branch/customers/all/')  # Redirect to a list view or details page after editing
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EditCustomerForm(instance=customer)

    return render(request, 'branch/customers/edit-customer.html', {
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
    return render(request, 'branch/customers/customers.html', context)

