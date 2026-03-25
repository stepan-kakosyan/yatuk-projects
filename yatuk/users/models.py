from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils import timezone
from .managers import CustomUserManager
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import get_language
from django.db.models import Count, Sum, F
from django.utils.translation import gettext_lazy as _

USER_ROLES = [
        ('admin', 'Admin'),
        ('client', 'Client')
    ]


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    profile_image = models.ImageField(null=True, blank=True, max_length=1000, upload_to='profile_images/%Y/%m/%d')
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
                "total": shopping_cart_.aggregate(sum=Sum(F('count') * F('product__price')))['sum']
            }
        else:
            return {
                "count": 0,
                "total": 0
            }


class State(models.Model):
    name_en = models.CharField(max_length=255)
    name_ru = models.CharField(max_length=255)
    name_hy = models.CharField(max_length=255)
    code = models.CharField(max_length=10)

    def __str__(self):
        return getattr(self, f"name_{get_language()}")

    @classmethod
    def import_armenian_states(cls):
        armenian_states = [
            {'name_en': 'Aragatsotn', 'name_ru': 'Арагацотн', 'name_hy': 'Արագածոտն', 'code': 'AG'},
            {'name_en': 'Ararat', 'name_ru': 'Арарат', 'name_hy': 'Արարատ', 'code': 'AR'},
            {'name_en': 'Armavir', 'name_ru': 'Армавир', 'name_hy': 'Արմավիր', 'code': 'AV'},
            {'name_en': 'Gegharkunik', 'name_ru': 'Гегаркуник', 'name_hy': 'Գեղարքունիք', 'code': 'GR'},
            {'name_en': 'Kotayk', 'name_ru': 'Котайк', 'name_hy': 'Կոտայք', 'code': 'KT'},
            {'name_en': 'Lori', 'name_ru': 'Лори', 'name_hy': 'Լոռի', 'code': 'LO'},
            {'name_en': 'Shirak', 'name_ru': 'Ширак', 'name_hy': 'Շիրակ', 'code': 'SH'},
            {'name_en': 'Syunik', 'name_ru': 'Сюник', 'name_hy': 'Սյունիք', 'code': 'SU'},
            {'name_en': 'Tavush', 'name_ru': 'Тавуш', 'name_hy': 'Տավուշ', 'code': 'TV'},
            {'name_en': 'Vayots Dzor', 'name_ru': 'Вайоц Дзор', 'name_hy': 'Վայոց Ձոր', 'code': 'VD'},
            {'name_en': 'Yerevan', 'name_ru': 'Ереван', 'name_hy': 'Երևան', 'code': 'ER'},
        ]

        for state in armenian_states:
            state_obj, created = cls.objects.get_or_create(
                name_en=state['name_en'],
                name_ru=state['name_ru'],
                name_hy=state['name_hy'],
                code=state['code']
            )
            if created:
                print(f"State '{state['name_en']}' created successfully")
            else:
                print(f"State '{state['name_en']}' already exists.")


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses", verbose_name=_("User"))
    address = models.CharField(max_length=255, verbose_name=_("Address"))
    city = models.CharField(max_length=255, verbose_name=_("City or Village"))
    state = models.ForeignKey(State, on_delete=models.PROTECT, related_name="addresses", null=False, blank=False,
                              verbose_name=_("State"))
    postal_code = models.CharField(max_length=10, verbose_name=_("Postal Code"))
    is_default = models.BooleanField(default=False, verbose_name=_("Is Default"))

    def __str__(self):
        return f"{self.state}, {self.city}, {self.address}, {self.postal_code}"
