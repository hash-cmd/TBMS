from django.db import models
from branch.models import CustomerInformation
import os
import uuid
from django.utils import timezone

# Create your models here.
class Branchs(models.Model):
    slug = models.SlugField(unique=True, blank=True)
    branch_code = models.CharField(max_length=5, unique=True)
    branch_name = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = str(uuid.uuid4())
        super().save(*args, **kwargs)

    def __str__(self):
        return self.branch_name

   
class Currency(models.Model):
    slug = models.SlugField(unique=True, blank=True)
    currency_sign = models.CharField(max_length=10)
    currency_name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.currency_name
 
 
 
 
 
class TreasuryBills(models.Model):

    T_BILL_STATUS = (
        ( 0, 'Not Running'),
        ( 1, 'Running'),
    )
    
    INSTRUCTION_UPDATE = (
        ( '0','Do Not Roll-Over'),
        ( '1','Roll-Over'),
        ( '2','Terminate')
    )
    
    TENOR = (
        (91, '91 Days'),
        (182, '182 Days'),
        (364, '1 Year'),
        (732, '2 Years'),
        (1098, '3 Years'),
    )

    MATURITY_INSTRUCTION = (
        (1, 'Pay Principal and Interest on Maturity'),
        (2, 'Roll - Over with Interest on Maturity'),
        (3, 'Roll - Over Principal only on Maturity'),
    )
    
    slug = models.SlugField(unique=True, blank=True)
    transaction_code = models.CharField(max_length=255, blank=True, null=True)
    branch_purchased_at = models.CharField(max_length=100)
    account_domicile_branch = models.ForeignKey(Branchs, on_delete=models.CASCADE)
    account_number = models.ForeignKey(CustomerInformation, on_delete=models.CASCADE)
    tenor = models.PositiveIntegerField(blank=True, null=True, choices=TENOR)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)

    customer_amount = models.DecimalField(max_digits=20, decimal_places=2)
    lcy_amount = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    face_value = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    interest_rate = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    discount_rate = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)

    maturity_instruction = models.PositiveIntegerField(blank=True, null=True, choices=MATURITY_INSTRUCTION)
    issue_date = models.DateTimeField(blank=True, null=True)
    maturity_date = models.DateTimeField(blank=True, null=True)
    file = models.FileField(upload_to='t_bill_files/', blank=True, null=True)
    status = models.CharField(max_length=20, default='0')
    roll_over_instruction = models.CharField(max_length=100, choices=INSTRUCTION_UPDATE, default='None')
    comment = models.TextField(blank=True, null=True)
    created_by = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = str(uuid.uuid4())
        
        if self.file and hasattr(self.file, 'name'):
            file_extension = os.path.splitext(self.file.name)[1]  
            date_str = timezone.now().strftime('%Y-%m-%d')  
            account_number_str = str(self.account_number) if self.account_number else 'unknown'
            self.file.name = f"{account_number_str}_{date_str}{file_extension}"
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"T-Bill {self.transaction_code} - {self.account_number} - {self.maturity_date}"
        

class MaturedTBills(models.Model):
    transaction_code = models.CharField(max_length=255, unique=True)
    branch_purchased_at = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    csd_number = models.CharField(max_length=50, blank=True, null=True)
    customer_name = models.CharField(max_length=255)
    customer_amount = models.DecimalField(max_digits=15, decimal_places=2)
    lcy_amount = models.DecimalField(max_digits=15, decimal_places=2)
    face_value = models.DecimalField(max_digits=15, decimal_places=2)
    issue_date = models.DateTimeField()
    maturity_date = models.DateTimeField()
    requested_by = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Matured T-Bill {self.transaction_code} - {self.customer_name}"


class Withdrawal(models.Model):
    transaction_code = models.CharField(max_length=255)
    branch_purchased_at = models.CharField(max_length=100)
    account_domicile_branch = models.CharField(max_length=255) 
    account_number = models.CharField(max_length=255) 
    tenor = models.CharField(max_length=10)  
    currency = models.CharField(max_length=50)  
    customer_amount = models.CharField(max_length=20) 
    maturity_instruction = models.CharField(max_length=50)
    lcy_amount = models.CharField(max_length=20) 
    interest_rate = models.CharField(max_length=20)  
    discount_rate = models.CharField(max_length=20) 
    face_value = models.CharField(max_length=20) 
    issue_date = models.CharField(max_length=50) 
    maturity_date = models.CharField(max_length=50) 
    roll_over_instruction = models.CharField(max_length=100)
    created_by = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    


class TransactionDetails(models.Model):
    account_number = models.CharField(max_length=100)
    ccy = models.CharField(max_length=10, blank=True, null=True) 
    dr_cr = models.CharField(max_length=2, blank=True, null=True)  
    transaction_details = models.TextField(blank=True, null=True)
    lcy_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True) 
    acc_branch = models.CharField(max_length=100, blank=True, null=True)  
    fcy_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True) 
    mis_code = models.CharField(max_length=50, blank=True, null=True) 
    related_account = models.CharField(max_length=100, blank=True, null=True)
    cust_id = models.CharField(max_length=100, blank=True, null=True)  
    trans_code = models.CharField(max_length=100, blank=True, null=True) 
    sn = models.IntegerField(blank=True, null=True)
    instrument = models.CharField(max_length=100, blank=True, null=True) 

    def __str__(self):
        return f"Transaction {self.trans_code} - {self.account_number}"
    


class BOG_Weekly_Code(models.Model):
    code = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code
    