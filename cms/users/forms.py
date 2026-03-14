from datetime import datetime
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import USER_ROLES, User
from django import forms
from django.urls import reverse_lazy
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout,  Row, Column
from crispy_forms.bootstrap import InlineRadios, Div
from django.contrib.admin import widgets


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = User
        fields = ('username',)


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username',)


class SignUpForm(forms.ModelForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    repeat_password = forms.CharField(label="Repeat Password", required=True, widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = "sign-up-form"
        self.helper.attrs = {
            'hx-post': reverse_lazy('sign-up'),
            'hx-target': '#sign-up-form',
            'hx-swap': 'innerHTML'
        }
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-0'),
                Column('last_name', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('username', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('password', css_class='form-group col-md-6 mb-0'),
                Column('repeat_password', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'SIgn Up')
        )


    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'password', 'repeat_password')

        widgets = {
            'password': forms.PasswordInput()
        }

    def clean(self):
        repeat_password = self.cleaned_data['repeat_password']
        password = self.cleaned_data['password']

        if len(password) < 6:
            self.add_error('password', "Password should contain at least 6 characters.")
        if password != repeat_password:
            self.add_error('repeat_password', "Passwords doesn't match.")
        username = self.cleaned_data['username']
        if len(username) < 6:
            self.add_error('username', "Username should contain at least 6 character.")
        elif User.objects.filter(username=username).exists():
            self.add_error('username', "Username is used")
        return self.cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.role = USER_ROLES[1][0]
        if commit:
            user.save()
        return user


class SignInForm(forms.Form):
    user_name = forms.CharField(required=True, label="Username", widget=forms.TextInput(attrs={'id': "sign_in_username"}))
    s_password = forms.CharField(required=True, label="Password", widget=forms.PasswordInput(attrs={'id': "sign_in_password"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = "sign-in-form"
        self.helper.attrs = {
            'hx-post': reverse_lazy('sign-in'),
            'hx-target': '#sign-in-form',
            'hx-swap': 'innerHTML'
        }
        self.helper.add_input(Submit('submit', 'Sign In'))

    def clean(self):
        password = self.cleaned_data['s_password']
        username = self.cleaned_data['user_name']
        users = User.objects.filter(username=username)
        if users.exists():
            if not users.first().check_password(password):
                raise forms.ValidationError("Username or password is incorrect")
        else:
            raise forms.ValidationError("Username or password is incorrect")


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={"class": "form-control"}))
    new_password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={"class": "form-control"}))
    repeat_password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={"class": "form-control"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = "change-security-form"
        self.helper.attrs = {
            'hx-post': reverse_lazy('security'),
            'hx-target': '#security',
            'hx-swap': 'outerHTML'
        }
        self.helper.layout = Layout(
            Row(
                Column('old_password', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('new_password', css_class='form-group col-md-6 mb-0'),
                Column('repeat_password', css_class='form-group col-md-6 mb-0'),
            ),
            Submit('submit', 'Change Password')
        )

    def clean(self):
        if len(self.cleaned_data['new_password']) < 6:
            self.add_error('new_password', "Password should contain at least 6 characters.")
            return self.cleaned_data

        if self.cleaned_data['new_password'] != self.cleaned_data['repeat_password']:
            self.add_error('repeat_password', "Passwords doesn't match.")
        return self.cleaned_data


class AccountForm(forms.ModelForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    date_of_birth = forms.DateField(label='Date Of Birth', widget=widgets.AdminDateWidget(attrs={"type": "date"}))

    class Meta:
        model = User
        fields = ("first_name", 'last_name', 'date_of_birth')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = "profile-form"
        self.helper.attrs = {
            'hx-post': reverse_lazy('profile'),
            'hx-target': '#account',
            'hx-swap': 'outerHTML'
            }
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-0'),
                Column('last_name', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Div(InlineRadios('gender'), css_class='form-group col-md-6 mb-0'),
                Column('date_of_birth', css_class='form-group col-md-6 mb-0'),
            ),
        )
        self.helper.add_input(Submit('submit', 'Update'))

    def clean_first_name(self):
        if self.cleaned_data['first_name'].strip() == "":
            raise forms.ValidationError("First name cannot be empty.")
        return self.cleaned_data['first_name'].strip()

    def clean_last_name(self):
        if self.cleaned_data['last_name'].strip() == "":
            raise forms.ValidationError("Last name cannot be empty.")
        return self.cleaned_data['last_name'].strip()

    def clean_date_of_birth(self):
        if self.cleaned_data['date_of_birth'] > datetime.today().date():
            raise forms.ValidationError("Date of birth cannot be future.")
        return self.cleaned_data['date_of_birth']


class ChangeUsernameForm(forms.Form):
    new_username = forms.CharField(required=True, label="Username")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = "change-username-form"
        self.helper.attrs = {
            'hx-post': reverse_lazy('change_username'),
            'hx-target': '#change-username',
            'hx-swap': 'outerHTML'
        }
        self.helper.layout = Layout(
            Row(
                Column('new_username', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Change Username')
        )

    def clean_new_username(self):
        username = self.cleaned_data['new_username']
        if len(username) < 6:
            self.add_error('new_username', "Username should contain at least 6 characters.")
            return self.cleaned_data
        if User.objects.filter(username=username).exists():
            self.add_error('new_username', "Username in use.")
            return username
        return username
