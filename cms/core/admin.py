from django.contrib import admin
from .models import Slider, ShippingMethod, ContactUs, Order, OrderItem, Review


class ContactUsAdmin(admin.ModelAdmin):
    list_display = ('name', 'email_or_phone', 'is_seen')


class SliderAdmin(admin.ModelAdmin):
    list_display = ('title_en', 'description_en', 'ordering')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    list_display = ('product', 'price', 'quantity')
    fields = list_display


class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'status', 'shipping_method')
    inlines = (OrderItemInline,)


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('image_', 'name', 'review', 'is_active', 'link', 'date')


admin.site.register(Slider, SliderAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(ShippingMethod)
admin.site.register(ContactUs, ContactUsAdmin)
admin.site.register(Review, ReviewAdmin)
