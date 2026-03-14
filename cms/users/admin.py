from django.contrib import admin
from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'date_joined', 'domain', 'is_active')


# Register your models here.
admin.site.register(User, UserAdmin)
