from django.shortcuts import render
from django.http import HttpResponse

def profile(request):
    return HttpResponse("Профиль пользователя - в разработке")
