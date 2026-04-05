from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .models import Category, Product, Review, Favorite


def home(request):
    """Главная страница - показывает только новинки"""
    # Только новинки (отмеченные флажком is_new)
    new_products = Product.objects.filter(in_stock=True, is_new=True).order_by('-created')[:8]

    # Если новинок нет, показываем последние 8 товаров
    if not new_products:
        new_products = Product.objects.filter(in_stock=True).order_by('-created')[:8]

    context = {
        'new_products': new_products,
    }
    return render(request, 'index.html', context)


def product_list(request, slug=None):
    """Список товаров с фильтрацией"""
    products = Product.objects.filter(in_stock=True)
    category = None

    # Получаем slug категории из параметра URL
    if slug:
        category = get_object_or_404(Category, slug=slug)
        products = products.filter(category=category)

    # Фильтрация по цене
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # Поиск
    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Сортировка
    sort = request.GET.get('sort', '-created')
    products = products.order_by(sort)

    # Пагинация
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    products = paginator.get_page(page)

    # Все категории для фильтра (только верхний уровень)
    categories = Category.objects.filter(parent__isnull=True)

    # Словарь для отображения названий сортировки
    sort_choices = {
        '-created': 'Новинки',
        'price': 'Цена по возрастанию',
        '-price': 'Цена по убыванию',
        'name': 'По названию (А-Я)',
        '-name': 'По названию (Я-А)',
    }

    context = {
        'products': products,
        'category': category,
        'categories': categories,
        'search_query': search_query,
        'current_sort': sort,
        'sort_choices': sort_choices,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'catalog/product_list.html', context)


def product_detail(request, slug):
    """Детальная страница товара"""
    product = get_object_or_404(Product, slug=slug, in_stock=True)
    reviews = product.reviews.filter(is_approved=True)

    # Проверка в избранном
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, product=product).exists()

    # Похожие товары (из той же категории)
    related_products = Product.objects.filter(
        category=product.category,
        in_stock=True
    ).exclude(id=product.id)[:4]

    context = {
        'product': product,
        'reviews': reviews,
        'is_favorite': is_favorite,
        'related_products': related_products,
    }
    return render(request, 'catalog/product_detail.html', context)


def category_list(request):
    """Список всех категорий"""
    # Получаем только родительские категории
    main_categories = Category.objects.filter(parent__isnull=True)

    # Для каждой категории получаем подкатегории
    categories_with_subs = []
    for cat in main_categories:
        categories_with_subs.append({
            'category': cat,
            'subcategories': Category.objects.filter(parent=cat)
        })

    context = {
        'categories_with_subs': categories_with_subs,
    }
    return render(request, 'catalog/category_list.html', context)


def add_review(request, product_id):
    """Добавление отзыва"""
    if request.method == 'POST' and request.user.is_authenticated:
        product = get_object_or_404(Product, id=product_id)
        rating = request.POST.get('rating')
        text = request.POST.get('review_text')

        if rating and text:
            Review.objects.create(
                product=product,
                user=request.user,
                rating=rating,
                text=text
            )
            messages.success(request, 'Спасибо за отзыв!')
        else:
            messages.error(request, 'Пожалуйста, заполните все поля')

        return redirect('catalog:product_detail', slug=product.slug)

    return redirect('catalog:product_list')


def toggle_favorite(request):
    """Добавить/удалить из избранного (AJAX)"""
    if request.method == 'POST' and request.user.is_authenticated:
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)

        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            product=product
        )

        if not created:
            favorite.delete()
            is_favorite = False
        else:
            is_favorite = True

        return JsonResponse({'success': True, 'is_favorite': is_favorite})
    return JsonResponse({'success': False, 'error': 'Требуется авторизация'})