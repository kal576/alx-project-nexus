from django.contrib import admin
from .models import Order, OrderItem


class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user__username", "total_amount", "created_at"]
    list_filter = ["user__username", "status", "created_at"]
    search_fields = ["user__username"]


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["id", "get_username", "product", "quantity", "unit_price"]
    list_filter = ["order__user"]
    search_fields = ["order__user_username", "product__name"]

    def get_username(self, obj):
        if obj.order and obj.order.user:
            return obj.order.user.username
        return "Anonymous"


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
