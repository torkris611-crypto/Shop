from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Profile
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm


def user_login(request):
    """Вход пользователя"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {username}!')
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, 'Неверное имя пользователя или пароль')
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def user_logout(request):
    """Выход пользователя"""
    logout(request)
    messages.success(request, 'Вы вышли из аккаунта')
    return redirect('home')


def register(request):
    """Регистрация пользователя"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Регистрация успешна! Теперь вы можете войти.')
            return redirect('accounts:login')
        else:
            # Выводим ошибки формы
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    """Личный кабинет"""
    return render(request, 'accounts/profile.html')


@login_required
def update_profile(request):
    """Обновление профиля"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
        else:
            messages.error(request, 'Ошибка при обновлении профиля')
    return redirect('accounts:profile')