
from .views import get_cart

def cart(request):
    """Контекстный процессор для корзины"""
    if request.user.is_authenticated or request.session.session_key:
        cart = get_cart(request)
        return {
            'cart_total_items': cart.get_total_items(),
            'cart_total_price': cart.get_total_price(),
        }
    return {
        'cart_total_items': 0,
        'cart_total_price': 0,
    }