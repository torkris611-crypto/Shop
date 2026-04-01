from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('categories/', views.category_list, name='category_list'),  # ← список всех категорий
    path('category/<slug:slug>/', views.product_list, name='product_list_by_category'),  # ← товары по категории
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('add-review/<int:product_id>/', views.add_review, name='add_review'),
    path('toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
]