from django.db import models
from django.utils.text import slugify
import uuid

# Create your models here.
class CustomerInformation(models.Model):
    
    TITLE = (
        ('Mr', 'Mr'),
        ('Mrs', 'Mrs'),
        ('Miss', 'Miss'),
        ('Master', 'Master'),
        ('Dr', 'Dr'),
    )
    
    RESIDENTIAL_STATUS = (
        ('Resident Ghanaian', 'Resident Ghanaian'),
        ('Resident Foreigner', 'Resident Foreigner'),
        ('Non Resident Ghanaian', 'Non Resident Ghanaian'),
        ('Non Resident Foreigner', 'Non Resident Foreigner')
    )
    
    ID_TYPES = (
        ('National ID', 'National ID'),
        ('Passport', 'Passport'),
        ('Birth Certificate', 'Birth Certificate'),
        ('Voters Card', 'Voters Card'),
        ('Certificate of Incorporation', 'Certificate of Incorporation'),
        ('Drivers License', 'Drivers License'),
    )

    BRANCHES = (
        ('101', 'Airport'),
    )
    
    slug = models.SlugField(unique=True)
    
    #applicants information
    title = models.CharField(max_length=20, blank=True, null=True, choices=TITLE)
    surname_or_company_name = models.CharField(max_length=255, blank=True, null=True)
    other_names = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    residential_address = models.CharField(max_length=255, blank=True, null=True)
    residential_status = models.CharField(max_length=255, blank=True, null=True, choices=RESIDENTIAL_STATUS, default='')
    phone_number =  models.CharField(max_length=12, blank=True, null=True)
    fax_number =  models.CharField(max_length=12, blank=True, null=True)
    email =  models.EmailField(blank=True, null=True)
    date_of_birth_or_incorporation_of_business =  models.DateField(blank=True, null=True)
    occupation = models.CharField(max_length=255, blank=True, null=True)
    nationality = models.CharField(max_length=255, blank=True, null=True)
    id_type = models.CharField(max_length=255, blank=True, null=True, choices=ID_TYPES, default='')
    id_number = models.CharField(max_length=255, blank=True, null=True)
    place_of_issue = models.CharField(max_length=255, blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    
    account_number = models.CharField(max_length=13, unique=True)
    account_branch = models.CharField(max_length=255, blank=True, null=True, choices=BRANCHES, default='')
    csd_number = models.CharField(max_length=255, blank=True, null=True)
    
    image = models.FileField(upload_to='ID/')
    csd_file = models.FileField(upload_to='CSD/')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = str(uuid.uuid4())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.surname_or_company_name} {self.other_names}"
