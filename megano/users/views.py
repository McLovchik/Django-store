from typing import Callable

from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.http import HttpRequest
from .forms import RegisterForm, AccountEditForm
from .services import reset_phone_format, get_auth_user
from django.contrib.auth import login, get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect, HttpRequest
from django.views.generic import DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from store.services.store_service import StoreServiceMixin


User = get_user_model()


class RegisterView(View):
    """
    Регистрация нового пользователя
    ::Страница: Регистрация пользователей
    """
    def get(self, request: HttpRequest) -> Callable:
        form = RegisterForm()
        return render(request, 'users/register.html', context={'form': form})

    def post(self, request: HttpRequest) -> Callable:
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            reset_phone_format(instance=user)
            login(request, get_auth_user(data=form.cleaned_data))
            return redirect('about')
        return render(request, 'users/register.html', context={'form': form})


class UserLoginView(SuccessMessageMixin, LoginView):
    """
    Аутентификация пользователя
    ::Страница: Логин пользователя
    """
    template_name = 'users/login.html'
    next_page = 'about'
    success_message = 'Вы успешно вошли на сайт'


class UserLogoutView(LogoutView):
    """
    Выход с сайта
    """
    next_page = 'about'


class AccountView(LoginRequiredMixin, StoreServiceMixin, DetailView):
    model = User
    context_object_name = 'user'
    template_name = 'users/account/personal_cabinet.html'

    def get_context_data(self, **kwargs):
        context = super(AccountView, self).get_context_data(**kwargs)
        context['last_order'] = self.get_last_order(user=self.request.user)
        return context


class AccountEditView(LoginRequiredMixin, View):
    # to change
    def get(self, request: HttpRequest) -> Callable:
        form = AccountEditForm()
        return render(request, 'users/account/profile_edit.html', context={'form': form})

    def post(self, request: HttpRequest) -> Callable:
        form = AccountEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save()
            reset_phone_format(instance=user)
            return render(request, 'users/account/profile_edit.html', context={'form': form})
        return render(request, 'users/account/profile_edit.html', context={'form': form})
