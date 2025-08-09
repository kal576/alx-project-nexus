from celery import shared_task
from django.core.mail import send_mail
from .models import Products


@shared_task
def low_stock_alert(product_id):
    try:
        product = Products.objects.get(id=product_id)
        if product.stock < 5:
            send_mail(
                subject=f"Low Stock Alert: {product.name}",
                message=f"Low stock for {product.name}. Available units: {product.stock}",
                recipient_list=["admin@example.com"],
                from_email="noreply@myshop.com",
            )
            return f"Alert sent for {product.name}"
        return f"Stock okay for {product.name}"
    except Product.DoesNotExist:
        return "Product not found"
