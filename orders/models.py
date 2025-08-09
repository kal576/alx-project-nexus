from django.db import models
from products.models import Products
from decimal import Decimal
from django.conf import settings

class Order(models.Model):
    ORDER_STATUS_CHOICES = [
            ('pending', 'Pending'),
            ('paid', 'Paid'),
            ('expired', 'Expired'),
            ('shipped', 'Shipped'),
            ('complete', 'Complete'),
            ('cancelled', 'Cancelled'),]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=50, decimal_places=2)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.user:
            return f"Order by {self.user.username}"
        return "Guest Order"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Product: {self.product}, Quantity: {self.quantity}"
