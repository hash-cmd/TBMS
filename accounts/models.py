from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
import uuid

class CustomUser(AbstractUser):
    DEPARTMENT = (
        ('admin', 'Internal Control'),
        ('branch', 'Branch'),
        ('treasury', 'Treasury Department'),
        ('trops', 'Troops Department'),
    )

    department = models.CharField(max_length=50, choices=DEPARTMENT)
    branch_code = models.CharField(max_length=50, blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            slug_uuid = uuid.uuid4()
            self.slug = slugify(str(slug_uuid))
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.username} {self.branch_code}'
