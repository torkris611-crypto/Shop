from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    fields = ('product', 'quantity')
    raw_id_fields = ('product',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_key', 'get_items_count', 'get_total_price', 'created')
    list_display_links = ('id', 'user')
    search_fields = ('user__username', 'session_key')
    list_filter = ('created', 'updated')
    inlines = [CartItemInline]

    def get_items_count(self, obj):
        return obj.items.count()

    get_items_count.short_description = 'Товаров в корзине'

    def get_total_price(self, obj):
        return f"{obj.get_total_price()} ₽"

    get_total_price.short_description = 'Общая сумма'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'quantity', 'get_total_price')
    list_display_links = ('id', 'cart')
    search_fields = ('cart__user__username', 'product__name')
    list_filter = ('cart__created',)

    def get_total_price(self, obj):
        return f"{obj.get_total_price()} ₽"

    get_total_price.short_description = 'Сумма'