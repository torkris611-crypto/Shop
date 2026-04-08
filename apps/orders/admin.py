from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """Товары в заказе (отображаются внутри заказа)"""
    model = OrderItem
    extra = 0
    fields = ('product', 'product_name', 'price', 'quantity', 'get_total_price')
    readonly_fields = ('product_name', 'price', 'get_total_price')
    can_delete = False

    def get_total_price(self, obj):
        return f"{obj.price * obj.quantity} ₽"

    get_total_price.short_description = 'Сумма'

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Настройка отображения заказов в админке"""

    list_display = (
        'id',
        'user_link',
        'full_name',
        'phone',
        'total_price_display',
        'status_colored',
        'created_at',
    )

    list_display_links = ('id', 'user_link')

    search_fields = (
        'id',
        'user__username',
        'user__email',
        'first_name',
        'last_name',
        'phone',
        'email',
        'address'
    )

    list_filter = ('status', 'delivery_method', 'payment_method', 'created')
    list_per_page = 25
    readonly_fields = ('created', 'updated', 'total_price')

    fieldsets = (
        (' Информация о покупателе', {
            'fields': ('user', 'first_name', 'last_name', 'email', 'phone')
        }),
        (' Адрес доставки', {
            'fields': ('city', 'address', 'postal_code')
        }),
        (' Доставка и оплата', {
            'fields': ('delivery_method', 'payment_method', 'delivery_cost', 'discount')
        }),
        (' Финансовая информация', {
            'fields': ('total_price',)
        }),
        (' Статус заказа', {
            'fields': ('status', 'tracking_number')
        }),
        (' Дополнительно', {
            'fields': ('comment', 'created', 'updated'),
            'classes': ('collapse',)
        }),
    )

    inlines = [OrderItemInline]

    actions = [
        'mark_as_pending',
        'mark_as_paid',
        'mark_as_shipped',
        'mark_as_delivered',
        'mark_as_cancelled'
    ]

    def user_link(self, obj):
        if obj.user:
            return format_html(
                '<a href="/admin/auth/user/{}/change/" style="color: #9c27b0;">{}</a>',
                obj.user.id, obj.user.username
            )
        return '-'

    user_link.short_description = 'Пользователь'

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    full_name.short_description = 'ФИО'

    def total_price_display(self, obj):
        return f"{obj.total_price} ₽"

    total_price_display.short_description = 'Сумма'

    def created_at(self, obj):
        return obj.created.strftime('%d.%m.%Y %H:%M')

    created_at.short_description = 'Дата'

    def status_colored(self, obj):
        colors = {
            'pending': ('#ff9800', ' В обработке'),
            'paid': ('#2196f3', ' Оплачен'),
            'shipped': ('#9c27b0', ' Отправлен'),
            'delivered': ('#4caf50', ' Доставлен'),
            'cancelled': ('#f44336', ' Отменен'),
        }
        color, text = colors.get(obj.status, ('gray', obj.status))
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; border-radius: 20px; font-size: 12px;">{}</span>',
            color, text
        )

    status_colored.short_description = 'Статус'

    def mark_as_pending(self, request, queryset):
        count = queryset.update(status='pending')
        self.message_user(request, f' {count} заказ(ов) переведены в статус "В обработке"')

    mark_as_pending.short_description = 'Перевести в статус "В обработке"'

    def mark_as_paid(self, request, queryset):
        count = queryset.update(status='paid')
        self.message_user(request, f' {count} заказ(ов) отмечены как оплаченные')

    mark_as_paid.short_description = 'Отметить как оплаченные'

    def mark_as_shipped(self, request, queryset):
        count = queryset.update(status='shipped')
        self.message_user(request, f' {count} заказ(ов) отмечены как отправленные')

    mark_as_shipped.short_description = 'Отметить как отправленные'

    def mark_as_delivered(self, request, queryset):
        count = queryset.update(status='delivered')
        self.message_user(request, f' {count} заказ(ов) отмечены как доставленные')
    mark_as_delivered.short_description = 'Отметить как доставленные'

    def mark_as_cancelled(self, request, queryset):
        count = queryset.update(status='cancelled')
        self.message_user(request, f'️ {count} заказ(ов) отменены')

    mark_as_cancelled.short_description = 'Отменить заказы'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_link', 'product_name', 'price_display', 'quantity', 'total_price_display')
    list_display_links = ('id', 'order_link')
    search_fields = ('order__id', 'product_name', 'order__user__username')
    list_filter = ('order__status',)
    readonly_fields = ('order', 'product', 'product_name', 'price', 'quantity')

    def order_link(self, obj):
        return format_html(
            '<a href="/admin/orders/order/{}/change/">Заказ #{}</a>',
            obj.order.id, obj.order.id
        )

    order_link.short_description = 'Заказ'

    def price_display(self, obj):
        return f"{obj.price} ₽"

    price_display.short_description = 'Цена'

    def total_price_display(self, obj):
        return f"{obj.price * obj.quantity} ₽"

    total_price_display.short_description = 'Сумма'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False