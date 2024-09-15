from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.utils import  timezone
from django.utils.timezone import make_aware
from datetime import datetime, timedelta
from django.http import HttpResponseRedirect, JsonResponse

from branch.forms import NewCustomerForm, NewTreasuryBillForm
from branch.models import CustomerInformation 
from treasury.models import TreasuryBills, Branchs, Currency, Withdrawal

from dal import autocomplete


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




def dashboard(request):
    today = datetime.today()
    current_weekday = today.weekday()
    start_of_week = today - timedelta(days=current_weekday)  # Monday
    end_of_week = start_of_week + timedelta(days=3)  # Thursday
    
    start_of_week = make_aware(start_of_week)
    end_of_week = make_aware(end_of_week)
    
    # Query for this week's treasury bills
    this_week_t_bills = TreasuryBills.objects.filter(
        maturity_date__range=[start_of_week, end_of_week]
    )
    
    # Get the user's branch (assuming it's stored in the request or user profile)
    user_branch = request.user.branch_code
    
    # Query for all customers in the user's branch
    all_branch_customers = CustomerInformation.objects.filter(account_branch=user_branch)
    
    # Total number of customers in the branch
    total_customers_in_branch = all_branch_customers.count()

    return render(request, 'branch/index.html', {
        'this_week_t_bills': this_week_t_bills,
        'all_branch_customers': all_branch_customers,
        'total_customers_in_branch': total_customers_in_branch,
    })

    



def new_treasury_bill(request):
    all_currency = Currency.objects.all()
    all_branch = Branchs.objects.all()

    if request.method == 'POST':
        form = NewTreasuryBillForm(request.POST, request.FILES)
        if form.is_valid():
            treasury_bill = form.save(commit=False)
            
            # Generate the new transaction code
            last_treasury_bill = TreasuryBills.objects.order_by('-id').first()
            if last_treasury_bill and last_treasury_bill.transaction_code:
                last_transaction_code = last_treasury_bill.transaction_code
                new_transaction_code = str(int(last_transaction_code) + 1).zfill(len(last_transaction_code))
            else:
                new_transaction_code = '1'
            
            treasury_bill.transaction_code = new_transaction_code
            
            # Fetch the CustomerInformation instance based on the selected account number
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


def update_t_bill_rollover_with_interest(request, slug):
    
    update_instance = get_object_or_404(TreasuryBills, slug=slug)
    update_instance.roll_over_instruction = '1'
    update_instance.maturity_instruction = 2
    update_instance.save()
    
    messages.success(request, 'Treasury Bill Updated successfully!')
    return redirect('/branch/notify/')



def update_t_bill_rollover_principal(request, slug):
    
    update_instance = get_object_or_404(TreasuryBills, slug=slug)
    update_instance.roll_over_instruction = '1'
    update_instance.maturity_instruction = 3
    update_instance.save()
    
    messages.success(request, 'Treasury Bill Updated successfully!')
    return redirect('/branch/notify/')


def update_t_bill_do_not_rollover(request, slug):
    
    update_instance = get_object_or_404(TreasuryBills, slug=slug)
    update_instance.roll_over_instruction = '0'
    update_instance.maturity_instruction = 1
    update_instance.save()
    
    messages.success(request, 'Treasury Bill Updated successfully!')
    return redirect('/branch/notify/')
    


def terminate_t_bill(request, slug):
    # Get the TreasuryBills instance using the slug
    termination_instance = get_object_or_404(TreasuryBills, slug=slug)
    
    # Update the TreasuryBills instance
    termination_instance.roll_over_instruction = '3'
    termination_instance.maturity_instruction = 1
    termination_instance.save()
    
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


def withdrawal_list(request):
    withdrawals = Withdrawal.objects.all()
    return render(request, 'branch/treasury/withdrawal-list.html', {'withdrawals': withdrawals})


def delete_treasury_bill(request, slug):
    # Retrieve the TreasuryBill instance based on the slug
    delete_instance = get_object_or_404(TreasuryBills, slug=slug)
    delete_instance.delete()
    messages.success(request, 'Treasury Bill deleted successfully!')
    return redirect('/branch/treasury-bill/')


def get_treasury_bills_due_next_week():
    today = timezone.now().date()
    end_of_week = today + timedelta(weeks=1)
    
    # Query for records where maturity_date is within the next week
    due_next_week = TreasuryBills.objects.filter(
        maturity_date__date__range=[today, end_of_week]
    )
    
    return due_next_week


def notify_treasury_bill(request):
    all_treasury_bills = get_treasury_bills_due_next_week()
    
    context = {
        'all_treasury_bills': all_treasury_bills
    }
    
    return render(request, 'branch/treasury/reinvest-treasury-bill.html', context)



def treasury_bill(request):
    all_treasury_bills = TreasuryBills.objects.all()
    context = {
        'all_treasury_bills': all_treasury_bills,
    }
    return render(request, 'branch/treasury/requested-treasury-bill.html', context)

    
def all_transactions(request):
    pending_t_bills = TreasuryBills.objects.all()
    context = {
        'pending_t_bills': pending_t_bills,
    }
    return render(request, 'branch/treasury/all-transactions.html', context)
 
    


def new_customer(request):
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
    }
    return render(request, 'branch/customers/new-customer.html', context)


       
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

