from django.contrib.auth import login
from .forms import LoginForm
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from users.models import User
from django.shortcuts import render, redirect
from .forms import UserRegistrationForm
from .forms import UserEditForm
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

def profile(request):
    active = request.GET.get("active", "personal_info")
    if request.htmx:
        return render(request, 'users/partials/profile-info.html')
    context = {
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
                    next_url = request.GET.get('next', None)
                    if next_url:
                        return redirect(next_url)
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

def user_edit(request):
    user = request.user
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, _('User information updated successfully.'))
            return render(request, 'users/partials/profile-card.html')
        else:
            messages.error(request, _('Form submission failed. Please check your inputs and try again.'))
    else:
        form = UserEditForm(instance=user)
    return render(request, 'users/partials/profile-form.html', {'form': form})

def upload_profile_image(request):
    request.user.profile_image = request.FILES['prof-img']
    request.user.domain = 'canvas.yatuk.am'
    request.user.save()
    return render(request, 'users/partials/profile-image.html')
