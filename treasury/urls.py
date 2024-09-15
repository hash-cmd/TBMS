from django.urls import path
from treasury.views import (
    dashboard, branch, currency,
    treasury_bill, export_treasury_bills_to_csv, approve_treasury_bill, delete_treasury_bill, withdrawal_list,    
)

urlpatterns = [
    path('', dashboard, name=""),
    path('treasury-bill/', treasury_bill, name=""),
    path('export-treasury-bills/', export_treasury_bills_to_csv, name='export_treasury_bills_to_csv'),
    path('treasury-bill/bulk-approval/', approve_treasury_bill, name=""),
    path('treasury-bill/delete/<slug:slug>', delete_treasury_bill, name=""),
    path('treasury-bill/withdrawals/', withdrawal_list, name=""),    
    
    path('branch/', branch, name=""),
    path('currency/', currency, name=""),
] 