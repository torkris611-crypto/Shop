from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'phone', 'city')
    list_display_links = ('id', 'user')
    search_fields = ('user__username', 'user__email', 'phone')
    list_filter = ('city',)

    fieldsets = (
        ('Пользователь', {
            'fields': ('user',)
        }),
        ('Контактная информация', {
            'fields': ('phone', 'avatar', 'address', 'city', 'postal_code')
        }),
    )