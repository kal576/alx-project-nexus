from django.db import models
from django.contrib.auth import get_user_model
from products.models import Products

User = get_user_model()

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)

    class Meta:
        #ensure either user or session_key is available, and not both
        constraints = [
                models.CheckConstraint(
                    check=(
                        models.Q(user__isnull=False, session_key__isnull=True) |
                        models.Q(user__isnull=True, session_key__isnull=False)
                        ),
                    name='user_or_session'
                    )
                ]

    def total_price(self):
        return sum(item.subtotal() for item in self.items.all())

    def __str__(self):
        if self.user:
            return f"Cart for {self.user.username}"
        return f"Cart for {self.session_key}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def subtotal(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f"Cart items for {self.cart}"
