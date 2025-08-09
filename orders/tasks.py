from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from django.core.mail import send_mail
from .models import Order

def list_items(order):
    return ", ".join(f"{item.product.name} (Qty: {item.quantity})" for item in order.items.all()
                     )

@shared_task
def send_order_confirmation(order_id):
    """Task to send confirmation email on making an order"""
    try:
        order = Order.objects.get(id=order_id)
        recipient_email = order.user.email if order.user and order.user.email else None

        if recipient_email:
            send_mail(
                    subject=f"Order Confirmed: {order.id}",
                    message=f"""Dear {order.user.username if order.user else 'Customer'},

Your order {order.id} has been completed and is being prepared for shipping.

Order Details:
- Order ID: {order.id}
- Total Amount: Ksh{order.total_amount}
- Status: Pending Payment
- Items: {list_items(order)}

You will receive a shipping notification once your order is dispatched.

Please ensure your payment is completed within the next 6 hours to avoid order cancellation.

Thank you for your business!

Best regards,
Your Store Team
""",
                    recipient_list=[recipient_email],
                    from_email="noreply@mystore.com"
                )
        return f"Email sent for order {order_id}"
    except Order.DoesNotExist:
        return "Order not found"

@shared_task
def release_unpaid_orders():
    """Releases unpaid orders after six hours"""
    cutoff = timezone.now() - timedelta(hours=6)
    expired_orders = Order.objects.filter(
        status='pending',
        created_at__lt=cutoff
    )

    for order in expired_orders:
        with transaction.atomic():
            #release reserved stock
            for item in order.items.all():
                product = item.product
                product.reserved = max(0, product.reserved - item.quantity)                
                product.save(update_fields=['reserved'])
                
            order.status = 'expired'
            order.save()

            #notify user order has expired
            send_order_expiration_email.delay(order.id)

@shared_task
def send_order_expiration_email(order_id):
    """Task to send confirmation email on making an order"""
    try:
        order = Order.objects.get(id=order_id)
        recipient_email = order.user.email if order.user and order.user.email else None

        if recipient_email:
            send_mail(
                    subject=f"Order Expired: {order.id}",
                    message=f"Dear {order.user.username if order.user else 'Customer'}, your order {order.id} has expired. Please make a new order.",
                    recipient_list=[recipient_email],
                    from_email="noreply@mystore.com"
                )
        return f"Email sent for order {order_id}"
    except Order.DoesNotExist:
        return "Order not found"
