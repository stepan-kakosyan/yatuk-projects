from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils import timezone
from .managers import CustomUserManager
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import Count, Sum, F
from django.utils.translation import gettext_lazy as _

USER_ROLES = [
        ('admin', 'Admin'),
        ('client', 'Client')
    ]

class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    profile_image = models.ImageField(null=True, blank=True, max_length=1000, upload_to='profile_images/')
    username = models.CharField(unique=True, max_length=255, null=False, blank=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    role = models.CharField(choices=USER_ROLES, max_length=20, null=False, blank=False)
    phone_number = PhoneNumberField(region='AM', null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    background = models.CharField(max_length=255, null=True, blank=True)
    domain = models.CharField(max_length=255, null=True, blank=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def display_name(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}"
        else:
            return self.username

    @property
    def cart_items(self):
        return self.cart_products.filter(user=self)

    @property
    def shopping_cart(self):
        shopping_cart_ = self.cart_products.filter(user=self)
        if shopping_cart_.exists():
            return {
                "count": shopping_cart_.aggregate(count_=Count("count"))['count_'],
                "total": shopping_cart_.aggregate(sum = Sum(F('count') *  F('product__price')))['sum']
            }
        else:
            return {
                "count": 0,
                "total": 0
            }
