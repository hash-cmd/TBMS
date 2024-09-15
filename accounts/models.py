from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
import uuid

class CustomUser(AbstractUser):
    DEPARTMENT = (
        ('admin', 'IT Department'),
        ('branch', 'Branch'),
        ('treasury', 'Treasury Department'),
        ('troops', 'Troops Department'),
    )

    BRANCH = (
        ('None', 'None'),
        ('101', 'Airport Branch'),
    )

    department = models.CharField(max_length=50, choices=DEPARTMENT)
    branch_code = models.CharField(max_length=50, choices=BRANCH)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            slug_uuid = uuid.uuid4()
            self.slug = slugify(str(slug_uuid))
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.username} {self.branch_code}'
