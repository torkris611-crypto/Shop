from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    # Главная страница каталога (список всех товаров)
    path('', views.product_list, name='product_list'),

    # Список всех категорий
    path('categories/', views.category_list, name='category_list'),

    # Товары по категории (slug категории)
    path('category/<slug:slug>/', views.product_list, name='product_list_by_category'),

    # Детальная страница товара (slug товара)
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),

    # Добавление отзыва
    path('add-review/<int:product_id>/', views.add_review, name='add_review'),

    # Добавление/удаление из избранного
    path('toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
]