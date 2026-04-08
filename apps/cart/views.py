from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import ensure_csrf_cookie
import json
import logging

logger = logging.getLogger(__name__)
from .models import Cart, CartItem
from apps.catalog.models import Product


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
    """Страница корзины"""
    cart = get_cart(request)
    items = cart.items.select_related('product').all()

    context = {
        'items': items,
        'total_items': cart.get_total_items(),
        'total_price': cart.get_total_price(),
    }
    return render(request, 'cart/cart_detail.html', context)


@login_required
@require_http_methods(["POST"])
def add_to_cart(request):
    """Добавить товар в корзину (AJAX)"""
    try:
        # Пробуем получить JSON из body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            # Если не JSON, пробуем получить из POST
            data = {
                'product_id': request.POST.get('product_id'),
                'quantity': request.POST.get('quantity', 1)
            }

        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 1))

        if not product_id:
            return JsonResponse({'success': False, 'error': 'Не указан товар'})

        product = get_object_or_404(Product, id=product_id, in_stock=True)

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
            'cart_total': str(cart.get_total_price()),
            'message': 'Товар добавлен в корзину'
        })

    except Exception as e:
        logger.error(f"Error in add_to_cart: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["GET"])
def api_update_cart(request):
    """Получить актуальные данные корзины (AJAX)"""
    try:
        cart = get_cart(request)
        return JsonResponse({
            'success': True,
            'total_items': cart.get_total_items(),
            'total_price': float(cart.get_total_price()),
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def api_update_cart_item(request):
    """Обновить количество товара в корзине (AJAX)"""
    try:
        # Пробуем получить JSON из body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = {
                'item_id': request.POST.get('item_id'),
                'quantity': request.POST.get('quantity', 1)
            }

        item_id = data.get('item_id')
        quantity = int(data.get('quantity', 1))

        if not item_id:
            return JsonResponse({'success': False, 'error': 'Не указан товар'})

        cart = get_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

        if quantity <= 0:
            cart_item.delete()
        else:
            if quantity > cart_item.product.stock:
                return JsonResponse({
                    'success': False,
                    'error': f'Доступно только {cart_item.product.stock} шт.'
                })
            cart_item.quantity = quantity
            cart_item.save()

        cart = get_cart(request)
        return JsonResponse({
            'success': True,
            'total_items': cart.get_total_items(),
            'total_price': float(cart.get_total_price()),
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def api_remove_from_cart(request):
    """Удалить товар из корзины (AJAX)"""
    try:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = {'item_id': request.POST.get('item_id')}

        item_id = data.get('item_id')

        if not item_id:
            return JsonResponse({'success': False, 'error': 'Не указан товар'})

        cart = get_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        cart_item.delete()

        cart = get_cart(request)
        return JsonResponse({
            'success': True,
            'total_items': cart.get_total_items(),
            'total_price': float(cart.get_total_price()),
            'cart_empty': cart.get_total_items() == 0
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def api_clear_cart(request):
    """Очистить корзину (AJAX)"""
    try:
        cart = get_cart(request)
        cart.items.all().delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})