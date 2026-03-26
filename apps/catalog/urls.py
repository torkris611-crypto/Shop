from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_list, name='product_detail'),
    path('category/<slug:slug>/', views.product_list, name='category_list'),
]
