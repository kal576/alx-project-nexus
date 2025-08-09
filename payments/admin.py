from django.contrib import admin
from .models import Payment


class PaymentAdmin(admin.ModelAdmin):
    list_display = ["id", "order", "amount", "transaction_id", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["order__id", "order__user__username"]


admin.site.register(Payment, PaymentAdmin)
