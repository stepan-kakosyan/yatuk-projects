# authentication/forms.py
from django import forms
from users.models import User, Address, State
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.utils.translation import get_language


class LoginForm(forms.Form):
    username = forms.CharField(max_length=63, label=_("Username"))
    password = forms.CharField(max_length=63, widget=forms.PasswordInput, label=_("Password"))

class UserRegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=30, label=_("First Name"))
    last_name = forms.CharField(max_length=30, label=_("Last Name"))
    username = forms.CharField(min_length=6, label=_("Username"))
    password = forms.CharField(widget=forms.PasswordInput, min_length=6, label=_("Password"))
    repeat_password = forms.CharField(widget=forms.PasswordInput, min_length=6, label=_("Repeat Password"))

    def clean_username(self):
        username = self.cleaned_data['username']
        if len(username) < 6:
            raise forms.ValidationError(_('Username must be at least 6 characters long.'))
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(_('Username already in use.'))
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        repeat_password = cleaned_data.get('repeat_password')
        if password and repeat_password and password != repeat_password:
            raise forms.ValidationError(_('Passwords do not match.'))
        return cleaned_data

    def save(self, commit=True):
        user = User()
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.username = self.cleaned_data['username']
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class UserEditForm(forms.ModelForm):
    first_name = forms.CharField(
        label=_('First Name'),
        max_length=255,
        required=False
    )
    last_name = forms.CharField(
        label=_('Last Name'),
        max_length=255,
        required=False
    )
    username = forms.CharField(
        label=_('Username'),
        min_length=6,
        validators=[RegexValidator(
            r'^[\w.@+-]+$',
            message=_('Please enter a valid username.'),
            code='invalid_username'
        )],
        widget=forms.TextInput(attrs={'autocomplete': 'off'})
    )
    phone_number = forms.CharField(
        max_length=20,
        label=_('Phone Number'),
        widget=forms.TextInput(),
        required=False,
    )
    email = forms.EmailField(
        label=_('Email'),
        required=False
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'username']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(username=self.instance.username).exists():
            raise forms.ValidationError(_('This username is already taken.'))
        return username

class AddressForm(forms.ModelForm):
    state = forms.ModelChoiceField(
        label=_("State"),
        queryset=State.objects.all().order_by(f"name_{get_language()}"),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    class Meta:
        model = Address
        fields = ('state', 'city', 'address', 'postal_code')
        widgets = {
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'})
        }
