from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import ListView
from django.views import View
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

import copy

from . import models
from . import forms


class BaseProfile(View):
    template_name = 'profile_user/create.html'

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)

        self.car = copy.deepcopy(self.request.session.get('car', {}))

        self.profile = None

        if self.request.user.is_authenticated:
            self.profile = models.ProfileUser.objects.filter(
                user=self.request.user
            ).first()

            self.contexto = {
                'userform': forms.UserForm(
                    data=self.request.POST or None,
                    user=self.request.user,
                    instance=self.request.user,
                ),

                'profileform': forms.ProfileForm(
                    data=self.request.POST or None,
                    instance=self.profile
                )
            }
        else:
            self.contexto = {
                'userform': forms.UserForm(
                    data=self.request.POST or None
                ),
                'profileform': forms.ProfileForm(
                    data=self.request.POST or None
                )
            }
        self.userform = self.contexto['userform']
        self.profileform = self.contexto['profileform']

        if self.request.user.is_authenticated:
            self.template_name = 'profile_user/update_profile.html'

        self.renderizar = render(
            self.request, self.template_name, self.contexto)

    def get(self, *args, **kwargs):
        return self.renderizar


class Create(BaseProfile):
    def post(self, *args, **kwargs):
        if not self.userform.is_valid() or not self.profileform.is_valid():
            messages.error(
                self.request,
                'Existem erros no formulário de cadastro. Verifique se todos '
                'os campos foram preenchidos corretamente.'
            )

            return self.renderizar

        username = self.userform.cleaned_data.get('username')
        password = self.userform.cleaned_data.get('password')
        email = self.userform.cleaned_data.get('email')
        first_name = self.userform.cleaned_data.get('first_name')
        last_name = self.userform.cleaned_data.get('last_name')
        # username = self.userform.cleaned_data.get('username')

        if self.request.user.is_authenticated:
            user = self.request.user
            user.username = username

            if password:
                user.set_password(password)

            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            if not self.profile:
                self.profileform.cleaned_data['user'] = user
                print(self.profileform.cleaned_data)
                profile = models.ProfileUser(**self.profileform.cleaned_data)
                profile.save()
        else:
            user = self.userform.save(commit=False)
            user.set_password(password)
            user.save()

            profile = self.profileform.save(commit=False)
            profile.user = user
            profile.save()

        if password:
            auth = authenticate(
                self.request,
                username=user,
                password=password
            )
            if auth:
                login(self.request, user=user)

        self.request.session['car'] = self.car
        self.request.session.save()

        messages.success(
            self.request,
            'Seu cadastro foi criado com sucesso!'
        )

        messages.success(
            self.request,
            'Você efetuou seu login e já pode concluir a compra!'
        )
        # return redirect('product:car')
        return self.renderizar


class UpdateProfile(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Atualizar')


class Login(View):
    def post(self, *args, **kwargs):
        username = self.request.POST.get('username')
        password = self.request.POST.get('password')

        if not username or not password:
            messages.error(
                self.request,
                'Usuário ou senha inválidos.'
            )
            return redirect('profile_user:criar')

        user = authenticate(
            self.request, username=username, password=password)

        if not user:
            messages.error(
                self.request,
                'Usuário ou senha inválidos.'
            )
            return redirect('profile_user:criar')

        login(self.request, user=user)

        messages.success(
            self.request,
            'Você fez login no sistema e pode concluir sua compra.'
        )
        return redirect('product:carrinho')


class Logout(View):
    def get(self, *args, **kwargs):
        car = copy.deepcopy(self.request.session.get('carrinho'))

        logout(self.request)

        self.request.session['carrinho'] = car
        self.request.session.save()
        return HttpResponse('product:list')

# Create your views here.
