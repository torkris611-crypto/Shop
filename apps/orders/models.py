from django.db import models
from django.conf import settings
from django.db.models.signals import pre_save
from django.dispatch import receiver
from apps.catalog.models import Product


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'В обработке'),
        ('paid', 'Оплачен'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
    )

    DELIVERY_CHOICES = (
        ('courier', 'Курьерская доставка'),
        ('pickup', 'Самовывоз'),
        ('post', 'Почта России'),
    )

    PAYMENT_CHOICES = (
        ('card', 'Банковская карта'),
        ('cash', 'Наличные при получении'),
        ('online', 'Онлайн-оплата'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    first_name = models.CharField('Имя', max_length=50)
    last_name = models.CharField('Фамилия', max_length=50)
    email = models.EmailField('Email')
    phone = models.CharField('Телефон', max_length=20)
    city = models.CharField('Город', max_length=100, blank=True, default='')
    address = models.TextField('Адрес доставки')
    postal_code = models.CharField('Индекс', max_length=20, blank=True, default='')
    comment = models.TextField('Комментарий', blank=True, default='')
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='pending')
    delivery_method = models.CharField('Способ доставки', max_length=20, choices=DELIVERY_CHOICES, default='courier')
    payment_method = models.CharField('Способ оплаты', max_length=20, choices=PAYMENT_CHOICES, default='card')
    delivery_cost = models.DecimalField('Стоимость доставки', max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField('Скидка', max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField('Общая сумма', max_digits=10, decimal_places=2, default=0)
    tracking_number = models.CharField('Трек-номер', max_length=100, blank=True, default='')
    created = models.DateTimeField('Создан', auto_now_add=True)
    updated = models.DateTimeField('Обновлен', auto_now=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created']

    def __str__(self):
        return f'Заказ #{self.id} - {self.user.username}'

    def get_total_quantity(self):
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Заказ')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    product_name = models.CharField('Название товара', max_length=200, default='')
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField('Количество', default=1)

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'

    def __str__(self):
        return f'{self.product_name} x {self.quantity}'

    def get_total_price(self):
        return self.price * self.quantity