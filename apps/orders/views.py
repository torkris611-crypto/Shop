from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Order, OrderItem
from apps.cart.views import get_cart


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})


@login_required
def order_create(request):
    cart = get_cart(request)
    items = cart.items.select_related('product').all()

    if not items:
        messages.error(request, 'Корзина пуста')
        return redirect('cart:cart_detail')

    if request.method == 'POST':
        delivery_cost = {'courier': 300, 'pickup': 0, 'post': 350}.get(request.POST.get('delivery_method'), 300)
        total = cart.get_total_price() + delivery_cost

        order = Order.objects.create(
            user=request.user,
            first_name=request.POST.get('first_name', ''),
            last_name=request.POST.get('last_name', ''),
            email=request.POST.get('email', ''),
            phone=request.POST.get('phone', ''),
            city=request.POST.get('city', ''),
            address=request.POST.get('address', ''),
            postal_code=request.POST.get('postal_code', ''),
            comment=request.POST.get('comment', ''),
            delivery_method=request.POST.get('delivery_method', 'courier'),
            payment_method=request.POST.get('payment_method', 'card'),
            delivery_cost=delivery_cost,
            total_price=total,
        )

        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                price=item.product.price,
                quantity=item.quantity
            )

        cart.items.all().delete()
        messages.success(request, f'Заказ #{order.id} оформлен!')
        return redirect('orders:order_detail', order_id=order.id)

    return render(request, 'orders/order_create.html', {
        'items': items,
        'total_price': cart.get_total_price(),
        'total': cart.get_total_price() + 300,
    })


@require_POST
@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status == 'pending':
        order.status = 'cancelled'
        order.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})