from django.urls import path
from trops.views import dashboard, edit_customer, customers_all, treasury_bill, export_treasury_bills_to_csv, debit_treasury_bill, all_transactions, bog_code, delete_bog_code
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', dashboard, name=""),
    path('treasury-bill/', treasury_bill, name=""),
    path('treasury-bill/export-csv/', export_treasury_bills_to_csv, name=""),
    path('treasury-bill/bulk-debit/', debit_treasury_bill, name=""),
    path('all-transactions/', all_transactions , name=""),
    
    path('customer/edit/<slug:slug>/', edit_customer, name='edit_customer'),
    path('customers/all/', customers_all , name=""),
    path('treasury-bill/code/', bog_code, name=""),
    path('treasury-bill/code/delete/<int:id>', delete_bog_code, name=""),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)