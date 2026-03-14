from django import forms
from core.models import ContactUs, Order, ShippingMethod, Address
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from users.models import State
from django.utils.translation import get_language


class ContactUsForm(forms.ModelForm):
    class Meta:
        model = ContactUs
        fields = ('name', 'email_or_phone', 'text')

class OrderForm(forms.ModelForm):
    old_address = forms.ModelChoiceField(
        label=_("Address"),
        queryset=Address.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control',"hx-trigger": "change",
                        "hx-target": "#addressFormSection",
                        "hx-swap": "innerHTML",
                        "hx-get": reverse_lazy("change_address_form")}),
        required=False,
    )
    read_checkbox = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={"style": "width:15px; height: unset; margin-top: 0; margin: 10px"}),
        required=True
    )
    class Meta:
        model = Order
        fields = ('old_address', 'shipping_method', 'phone_number', 'comment', 'read_checkbox')
        widgets = {
            "shipping_method": forms.RadioSelect(choices=ShippingMethod.objects.all())
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['old_address'].queryset = Address.objects.filter(user_id=user)

class AddressForm(forms.ModelForm):
    state = forms.ModelChoiceField(
        label=_("State"),
        queryset=State.objects.all().order_by(f"name_{get_language()}"),
        widget=forms.Select(attrs={'class': 'form-control',
                                   "hx-trigger": "change",
                                    "hx-target": "#shippingMethodSection",
                                    "hx-swap": "innerHTML",
                                    "hx-get": reverse_lazy("change_shipping_method")})
    )
    class Meta:
        model = Address
        fields = ('state', 'city', 'address', 'postal_code')
        widgets = {
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'})
        }
