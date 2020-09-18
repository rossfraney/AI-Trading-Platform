from django.shortcuts import render, redirect
from django.contrib.auth import (
    logout,
)


def login_view(request):
    template_name = 'braikout/login.html'
    return render(request, template_name, {})


def logout_view(request):
    template_name = 'braikout/login.html'
    logout(request)
    redirect("/")
    return render(request, template_name)


def index(request):
    return render(request, 'dashboard/index.html')
