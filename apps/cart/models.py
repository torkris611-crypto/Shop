from django.db import models
from django.conf import settings
from apps.catalog.models import Product

class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        null=True,
        blank=True
    )
    session_key = models.CharField('Ключ сессии', max_length=40, null=True, blank=True)
    created = models.DateTimeField('Создана', auto_now_add=True)
    updated = models.DateTimeField('Обновлена', auto_now=True)

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def __str__(self):
        if self.user:
            return f'Корзина {self.user.username}'
        return f'Корзина (сессия: {self.session_key})'

    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())

    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name='Корзина')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    quantity = models.PositiveIntegerField('Количество', default=1)

    class Meta:
        verbose_name = 'Элемент корзины'
        verbose_name_plural = 'Элементы корзины'
        unique_together = ['cart', 'product']

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'

    def get_total_price(self):
        return self.product.price * self.quantity