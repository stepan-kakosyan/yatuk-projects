from django.contrib.auth import login
from .forms import LoginForm
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from users.models import User, Address
from .forms import UserRegistrationForm
from .forms import UserEditForm, AddressForm
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from core.views import my_login_required
from core.models import Order


@my_login_required
def profile(request):
    active = request.GET.get("active", "personal_info")
    if request.htmx:
        return render(request, 'users/partials/profile-info.html')
    context = {
        "addresses": Address.objects.filter(user=request.user),
        "orders": Order.objects.filter(user=request.user).exclude(status="not_paid").order_by("-id"),
        "active": active
        }
    return render(request, 'users/profile.html', context=context)


def login_page(request):
    if request.user.is_authenticated:
        return redirect(reverse_lazy("index"))
    form = LoginForm()
    message = ''
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = User.objects.filter(username=cd['username'])
            if user.exists():
                if user.first().check_password(cd['password']):
                    login(request, user.first())
                    return redirect(reverse_lazy("profile"))
                else:
                    message = _('Invalid username or password!')
            else:
                message = _('Invalid username or password!')
    if request.htmx:
        return render(request, 'users/partials/login-card.html', context={'form': form, 'message': message})
    return render(request, 'users/login.html', context={'form': form, 'message': message})


def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(reverse_lazy('profile'))
    else:
        form = UserRegistrationForm()
    if request.htmx:
        return render(request, 'users/partials/registration-card.html', {'form': form})
    return render(request, 'users/registration.html', {'form': form})


@my_login_required
def user_edit(request):
    user = request.user
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, _('User information updated successfully.'))
            return render(request, 'users/partials/profile-info.html')
        else:
            messages.error(request, _('Form submission failed. Please check your inputs and try again.'))
    else:
        form = UserEditForm(instance=user)
    return render(request, 'users/partials/profile-form.html', {'form': form})


@my_login_required
def remove_address(request, id):
    Address.objects.get(id=id).delete()
    return render(request, 'users/partials/address-list.html',
                  context={"addresses": Address.objects.filter(user=request.user)})


@my_login_required
def edit_address(request, id=None):
    user = request.user
    if id:
        address = Address.objects.get(id=id)
        if address.user != user:
            return render(request, 'users/partials/address-list.html',
                          context={"addresses": Address.objects.filter(user=request.user)})
        form = AddressForm(request.POST or None, instance=address)
    else:
        form = AddressForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            address = form.save(commit=False)
            address.user = user
            if not Address.objects.filter(user=user).exists():
                address.is_default = True
            address.save()
            return render(request, 'users/partials/address-list.html',
                          context={"addresses": Address.objects.filter(user=request.user)})

    context = {'form': form, 'address_id': id}
    return render(request, 'users/partials/address-form.html', context)


@my_login_required
def address_list(request):
    return render(request, 'users/partials/address-list.html',
                  context={"addresses": Address.objects.filter(user=request.user)})


@my_login_required
def upload_profile_image(request):
    request.user.profile_image = request.FILES['prof-img']
    request.user.domain = "yatuk.am"
    request.user.save()
    return render(request, 'users/partials/profile-image.html')
