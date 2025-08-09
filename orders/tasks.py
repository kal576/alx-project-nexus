from celery import shared_task
from django.core.mail import send_mail
from .models import Order

@shared_task
def send_order_confirmation(order_id):
    """Task to send confirmation email on making an order"""
    try:
        order = Order.objects.get(id=order_id)
        send_mail(
                subject=f"Order Confirmed: {order.id}",
                message=f"Hi {order.user.username}, your order for Ksh{order.total_amount} has been confirmed. Please pay within the next 24 hours",
                recipient_list=[order.user.email],
                from_email="noreply@mystore.com"
                )
        return "Email sent for order {order_id}"
    except Order.DoesNotExist:
        return "Order not found"
