from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.profile, name='profile'),
    path('login/', views.profile, name='login'),
    path('logout/', views.profile, name='logout'),
    path('register/', views.profile, name='register'),
]
