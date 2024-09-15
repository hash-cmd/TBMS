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
        (181, '181 Days'),
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
    transaction_code = models.CharField(max_length=255, unique=True, blank=True, null=True)
    branch_purchased_at = models.CharField(max_length=100)
    account_domicile_branch = models.ForeignKey(Branchs, on_delete=models.CASCADE)
    account_number = models.ForeignKey(CustomerInformation, on_delete=models.CASCADE)
    tenor = models.PositiveIntegerField(blank=True, null=True, choices=TENOR)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    customer_amount = models.DecimalField(max_digits=8, decimal_places=2)
    maturity_instruction = models.PositiveIntegerField(blank=True, null=True, choices=MATURITY_INSTRUCTION)
    lcy_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    interest_rate = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    discount_rate = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    face_value = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True) 
    issue_date = models.DateTimeField(blank=True, null=True)
    maturity_date = models.DateTimeField(blank=True, null=True)
    file = models.FileField(upload_to='t_bill_files/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=T_BILL_STATUS, default='0')
    roll_over_instruction = models.CharField(max_length=100, choices=INSTRUCTION_UPDATE, default='None')
    comment = models.TextField(blank=True, null=True)
    created_by = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = str(uuid.uuid4())
        
        # Set file name based on account_number and current date
        if self.file and hasattr(self.file, 'name'):
            file_extension = os.path.splitext(self.file.name)[1]  # Get file extension
            date_str = timezone.now().strftime('%Y-%m-%d')  # Format current date
            account_number_str = str(self.account_number) if self.account_number else 'unknown'
            self.file.name = f"{account_number_str}_{date_str}{file_extension}"
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"T-Bill {self.transaction_code} - {self.account_number} - {self.maturity_date}"
        



class Withdrawal(models.Model):
    transaction_code = models.CharField(max_length=255)
    branch_purchased_at = models.CharField(max_length=100)
    account_domicile_branch = models.CharField(max_length=255)  # Changed to CharField
    account_number = models.CharField(max_length=255)  # Changed to CharField
    tenor = models.CharField(max_length=10)  # Changed to CharField
    currency = models.CharField(max_length=50)  # Changed to CharField
    customer_amount = models.CharField(max_length=20)  # Changed to CharField
    maturity_instruction = models.CharField(max_length=50)
    lcy_amount = models.CharField(max_length=20)  # Changed to CharField
    interest_rate = models.CharField(max_length=20)  # Changed to CharField
    discount_rate = models.CharField(max_length=20)  # Changed to CharField
    face_value = models.CharField(max_length=20)  # Changed to CharField
    issue_date = models.CharField(max_length=50)  # Changed to CharField
    maturity_date = models.CharField(max_length=50)  # Changed to CharField
    roll_over_instruction = models.CharField(max_length=100)
    created_by = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    