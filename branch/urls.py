from django.urls import path
from branch.views import (
    dashboard, CustomerAutocomplete,
    new_treasury_bill, edit_treasury_bill, re, treasury_bill, 
    update_t_bill_do_not_rollover, update_t_bill_rollover_principal, update_t_bill_rollover_with_interest, delete_treasury_bill, 
    terminate_t_bill, withdrawal_list, notify_treasury_bill,
    all_transactions,
    new_customer, edit_customer, customers_all,
)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', dashboard, name=""),
    path('customer-autocomplete/', CustomerAutocomplete.as_view(), name='customer-autocomplete'),
    
    path('treasury-bill/new/', new_treasury_bill , name=""),
    path('treasury-bill/edit/<slug:slug>', edit_treasury_bill , name=""),
    path('treasury-bill/roll-over-principal/<slug:slug>', update_t_bill_rollover_principal, name=""),
    path('treasury-bill/roll-over-with-interest/<slug:slug>', update_t_bill_rollover_with_interest, name=""),
    path('treasury-bill/do-not-roll-over/<slug:slug>', update_t_bill_do_not_rollover, name=""),
    path('treasury-bill/terminate/<slug:slug>', terminate_t_bill, name=""),
    path('treasury-bill/delete/<slug:slug>', delete_treasury_bill, name=""),
    path('treasury-bill/withdrawal-list/', withdrawal_list, name=""),
    path('treasury-bill/', treasury_bill, name=""),
    
    path('notify/', notify_treasury_bill, name=""),  
    path('all-transactions/', all_transactions , name=""),
    
    path('customer/new/', new_customer, name=""),
    path('customer/edit/<slug:slug>/', edit_customer, name='edit_customer'),
    path('customers/all/', customers_all , name=""),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)