from django.db import models

class Category(models.Model):
    name = models.CharField(unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

class Products(models.Model):
    name = models.CharField(max_length=255)
    stock = models.PositiveIntegerField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    #checks the remaining stocks
    def can_sell(self, quantity):
        return self.stock >= int(quantity)

    class Meta:
        verbose_name_plural = "Products"
        
class MvtType(models.TextChoices):
    IN = 'IN', 'Stock In'
    OUT = 'OUT', 'Stock Out'

class Inventory(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    mvt_type = models.CharField(max_length=3, choices=MvtType.choices)
    quantity= models.PositiveIntegerField()
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    note = models.CharField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_mvt_type_display()}: {self.quantity} of {self.product}"

    def clean(self):
        # Validate first
        if self.product and self.mvt_type == MvtType.OUT and self.quantity > self.product.stock:
                raise ValidationError(f"Cannot remove {self.quantity}. Only {self.product.stock} in stock.")

    def save(self, *args, **kwargs):
        self.full_clean()

        #save inventory record
        super().save(*args, **kwargs)

        #update product stock
        if self.mvt_type == MvtType.IN:
            self.product.stock += self.quantity
        elif self.mvt_type == MvtType.OUT:
            self.product.stock -= self.quantity
        else:
            raise ValidationError("Invalid Movement Type")

        self.product.save(update_fields=['stock', 'updated_at'])

        class Meta:
            verbose_name_plural = "Inventories"
