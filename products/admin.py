from django.contrib import admin
from .models import Item, CartItem

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'created_at')
    search_fields = ('title', 'description', 'owner__email')
    list_filter = ('created_at',)
    ordering = ('-created_at',)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'item', 'quantity', 'added_at')
    search_fields = ('user__email', 'item__title')
    list_filter = ('added_at',)
    ordering = ('-added_at',)
