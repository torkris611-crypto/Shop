from django.contrib import admin
from .models import Category, Product, ProductImage, Review, Favorite


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'is_main')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'parent')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'slug')
    list_filter = ('parent',)
    prepopulated_fields = {'slug': ('name',)}

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'parent')
        }),
        ('Дополнительно', {
            'fields': ('image', 'description')
        }),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'stock', 'in_stock', 'is_new', 'created')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'slug', 'description')
    list_filter = ('category', 'in_stock', 'is_new', 'created')
    list_editable = ('price', 'stock', 'in_stock', 'is_new')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'category', 'description')
        }),
        ('Цена и наличие', {
            'fields': ('price', 'old_price', 'stock', 'in_stock')
        }),
        ('Изображение и характеристики', {
            'fields': ('image', 'specifications')
        }),
        ('Статус товара', {
            'fields': ('is_new',),
            'classes': ('wide',)
        }),
        ('Даты', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created', 'updated')


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'image', 'is_main')
    list_display_links = ('id', 'product')
    list_filter = ('is_main',)
    list_editable = ('is_main',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'user', 'rating', 'is_approved', 'created')
    list_display_links = ('id', 'product')
    search_fields = ('product__name', 'user__username', 'text')
    list_filter = ('rating', 'is_approved', 'created')
    list_editable = ('is_approved',)

    actions = ['approve_reviews', 'reject_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)

    approve_reviews.short_description = "Одобрить выбранные отзывы"

    def reject_reviews(self, request, queryset):
        queryset.update(is_approved=False)

    reject_reviews.short_description = "Отклонить выбранные отзывы"


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'created')
    list_display_links = ('id', 'user')
    search_fields = ('user__username', 'product__name')
    list_filter = ('created',)