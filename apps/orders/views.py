from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Order, OrderItem
from apps.cart.views import get_cart
from apps.catalog.models import Product


@login_required
def order_list(request):
    """Список заказов ТОЛЬКО текущего пользователя"""
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    """Детали заказа ТОЛЬКО текущего пользователя"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})


@login_required
def order_create(request):
    """Создание заказа из корзины"""
    cart = get_cart(request)
    items = cart.items.select_related('product').all()

    if not items:
        messages.error(request, 'Корзина пуста')
        return redirect('cart:cart_detail')

    if request.method == 'POST':
        # 1. Сначала ПРОВЕРЯЕМ наличие товаров на складе
        for item in items:
            if item.quantity > item.product.stock:
                messages.error(
                    request,
                    f'Товара "{item.product.name}" осталось только {item.product.stock} шт. '
                    f'Вы заказали {item.quantity} шт. Пожалуйста, уменьшите количество.'
                )
                return redirect('cart:cart_detail')

        # 2. Расчет стоимости доставки
        delivery_method = request.POST.get('delivery_method', 'courier')
        delivery_costs = {'courier': 300, 'pickup': 0, 'post': 350}
        delivery_cost = delivery_costs.get(delivery_method, 300)

        subtotal = cart.get_total_price()
        total = subtotal + delivery_cost

        # 3. Создаем заказ
        order = Order.objects.create(
            user=request.user,
            first_name=request.POST.get('first_name', request.user.first_name),
            last_name=request.POST.get('last_name', request.user.last_name),
            email=request.POST.get('email', request.user.email),
            phone=request.POST.get('phone', request.user.profile.phone if hasattr(request.user, 'profile') else ''),
            city=request.POST.get('city', ''),
            address=request.POST.get('address', ''),
            postal_code=request.POST.get('postal_code', ''),
            comment=request.POST.get('comment', ''),
            delivery_method=delivery_method,
            payment_method=request.POST.get('payment_method', 'card'),
            delivery_cost=delivery_cost,
            total_price=total,
            status='pending',
        )

        # 4. Копируем товары в заказ И СПИСЫВАЕМ СО СКЛАДА
        for item in items:
            # Создаем запись о товаре в заказе
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                price=item.product.price,
                quantity=item.quantity
            )

            # Уменьшаем количество товара на складе
            product = item.product
            product.stock -= item.quantity
            product.save()

            # Если товар закончился, обновляем статус "В наличии"
            if product.stock == 0:
                product.in_stock = False
                product.save()

        # 5. Очищаем корзину
        cart.items.all().delete()

        messages.success(request, f' Заказ #{order.id} успешно оформлен!')
        return redirect('orders:order_detail', order_id=order.id)

    # GET запрос - показываем форму
    context = {
        'items': items,
        'total_price': cart.get_total_price(),
        'delivery_cost': 300,
        'total': cart.get_total_price() + 300,
    }
    return render(request, 'orders/order_create.html', context)


@require_POST
@login_required
def cancel_order(request, order_id):
    """Отмена заказа (возврат товаров на склад)"""
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status == 'pending':
        # Возвращаем товары на склад
        for item in order.items.all():
            product = item.product
            product.stock += item.quantity
            if product.stock > 0:
                product.in_stock = True
            product.save()

        order.status = 'cancelled'
        order.save()

        messages.success(request, f' Заказ #{order.id} отменен. Товары возвращены на склад.')
        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Нельзя отменить этот заказ'})