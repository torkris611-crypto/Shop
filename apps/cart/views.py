from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from apps.catalog.models import Product
from .models import Cart, CartItem


def get_cart(request):
    """Получить корзину пользователя"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart


def cart_detail(request):
    """Детали корзины"""
    cart = get_cart(request)
    items = cart.items.select_related('product').all()

    context = {
        'cart': cart,
        'items': items,
        'total_price': cart.get_total_price(),
        'total_items': cart.get_total_items(),
    }
    return render(request, 'cart/cart_detail.html', context)


@require_POST
def add_to_cart(request):
    """Добавить товар в корзину"""
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))

    try:
        product = get_object_or_404(Product, id=product_id, in_stock=True)

        # Проверяем наличие на складе
        if quantity > product.stock:
            return JsonResponse({
                'success': False,
                'error': f'Доступно только {product.stock} шт.'
            })

        cart = get_cart(request)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            new_quantity = cart_item.quantity + quantity
            if new_quantity > product.stock:
                return JsonResponse({
                    'success': False,
                    'error': f'Нельзя добавить больше {product.stock} шт.'
                })
            cart_item.quantity = new_quantity
            cart_item.save()

        return JsonResponse({
            'success': True,
            'cart_count': cart.get_total_items(),
            'cart_total': str(cart.get_total_price())
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_POST
def update_cart_item(request):
    """Обновить количество товара"""
    item_id = request.POST.get('item_id')
    quantity = int(request.POST.get('quantity', 1))

    try:
        cart = get_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

        if quantity <= 0:
            cart_item.delete()
        else:
            # Проверяем наличие
            if quantity > cart_item.product.stock:
                return JsonResponse({
                    'success': False,
                    'error': f'Доступно только {cart_item.product.stock} шт.'
                })
            cart_item.quantity = quantity
            cart_item.save()

        return JsonResponse({
            'success': True,
            'cart_count': cart.get_total_items(),
            'cart_total': str(cart.get_total_price())
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_POST
def remove_from_cart(request):
    """Удалить товар из корзины"""
    item_id = request.POST.get('item_id')

    try:
        cart = get_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        cart_item.delete()

        return JsonResponse({
            'success': True,
            'cart_count': cart.get_total_items(),
            'cart_total': str(cart.get_total_price())
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_POST
def clear_cart(request):
    """Очистить корзину"""
    cart = get_cart(request)
    cart.items.all().delete()

    return JsonResponse({'success': True})