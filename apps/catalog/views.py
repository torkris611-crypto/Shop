from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .models import Category, Product, Review, Favorite


def home(request):
    """Главная страница"""
    # Получаем новинки (последние 8 товаров)
    new_products = Product.objects.filter(in_stock=True).order_by('-created')[:8]

    # Получаем популярные товары (по количеству отзывов)
    popular_products = Product.objects.filter(in_stock=True).annotate(
        review_count=Count('reviews')
    ).order_by('-review_count')[:8]

    context = {
        'new_products': new_products,
        'popular_products': popular_products,
    }
    return render(request, 'index.html', context)


def product_list(request):
    """Список товаров"""
    products = Product.objects.filter(in_stock=True)
    category = None
    category_slug = request.GET.get('category')

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
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

    # Категории для фильтра
    categories = Category.objects.all()

    context = {
        'products': products,
        'category': category,
        'categories': categories,
        'search_query': search_query,
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

    # Похожие товары
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
    """Список категорий"""
    categories = Category.objects.all()
    return render(request, 'catalog/category_list.html', {'categories': categories})


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

    return product_detail(request, product.slug)


def toggle_favorite(request):
    """Добавить/удалить из избранного"""
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
    return JsonResponse({'success': False})