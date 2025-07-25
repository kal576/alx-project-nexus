from django.db import models
from orders.models import Order

class Payment(models.Model):
    # Payment Methods
    CARD = 'card'
    MPESA = 'mpesa'
    PAYPAL = 'paypal'
    PAYMENT_METHOD_CHOICES = [
        (CARD, 'Card'),
        (MPESA, 'M-Pesa'),
        (PAYPAL, 'PayPal'),
    ]

    # Payment Status
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
        (FAILED, 'Failed'),
    ]

    transaction_id = models.CharField(max_length=50, unique=True)
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, default="pending", choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_id}, {self.order}, {self.created_at}, {self.amount}"
