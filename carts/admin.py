from django.contrib import admin
from .models import Cart, CartItem

class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username']

class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_username', 'product', 'quantity', 'subtotal']
    list_filter = ['cart__user', 'cart']
    search_fields = ['cart__user__username', 'product__name']

    def get_username(self, obj):
        if obj.cart and obj.cart.user:
            return obj.cart.user.username
        return 'Anonymous'

    get_username.admin_order_field = 'cart__user'

admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)



