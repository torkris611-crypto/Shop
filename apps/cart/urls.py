from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('add/', views.add_to_cart, name='add_to_cart'),

    # API методы для AJAX
    path('api/update/', views.api_update_cart, name='api_update_cart'),
    path('api/update-item/', views.api_update_cart_item, name='api_update_cart_item'),
    path('api/remove/', views.api_remove_from_cart, name='api_remove_from_cart'),
    path('api/clear/', views.api_clear_cart, name='api_clear_cart'),
]