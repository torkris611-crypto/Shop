from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('product', 'product_name', 'price', 'quantity')
    readonly_fields = ('product_name', 'price')

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'first_name', 'last_name', 'total_price', 'status', 'created')
    list_display_links = ('id', 'user')
    search_fields = ('user__username', 'first_name', 'last_name', 'email', 'phone')
    list_filter = ('status', 'delivery_method', 'payment_method', 'created')
    list_editable = ('status',)
    inlines = [OrderItemInline]
    readonly_fields = ('created', 'updated')

    fieldsets = (
        ('Пользователь', {
            'fields': ('user',)
        }),
        ('Контактные данные', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Адрес доставки', {
            'fields': ('city', 'address', 'postal_code')
        }),
        ('Информация о заказе', {
            'fields': ('status', 'delivery_method', 'payment_method', 'delivery_cost', 'discount', 'total_price',
                       'tracking_number')
        }),
        ('Дополнительно', {
            'fields': ('comment', 'created', 'updated'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_paid', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled']

    def mark_as_paid(self, request, queryset):
        queryset.update(status='paid')

    mark_as_paid.short_description = "Отметить как оплаченные"

    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped')

    mark_as_shipped.short_description = "Отметить как отправленные"

    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')

    mark_as_delivered.short_description = "Отметить как доставленные"

    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='cancelled')

    mark_as_cancelled.short_description = "Отметить как отмененные"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'product_name', 'price', 'quantity')
    list_display_links = ('id', 'order')
    search_fields = ('order__user__username', 'product_name')
    list_filter = ('order__status',)