from celery import Celery
from .models import Payment
from django.core.mail import send_mail
from celery import shared_task

@shared_task
def payment_confirmation_email(payment_id):
    """Send payment confirmation to users email after successfull payment"""
    try:
        payment = Payment.object.get(id=payment_id)
        user = payment.order.user
        recipient_email = payment.user.email if payment.user else None

        if recipient_email:
            send_mail(
                    subject = f"Payment Confirmation - Order #{payment.order.id}",
                    message = f"
                    Dear {payment.user.username if payment.user else 'Customer'},
                    
                    Your payment of ${payment.amount} for Order {payment.order.id} has been confirmed.
                    
                    Payment Details:
                    - Payment ID: {payment.id}
                    - Amount: Ksh{payment.amount}
                    - Payment Method: {payment.payment_method}
                    - Status: {payment.status}

                    Thank you for your purchase!

                    Best regards,
                    Your Store Team
                    ",
                    recipient_list=[recipient_email],
                    from_email="noreply@mystore.com")
        else:
            return Response({"error": "Email address not found"})
    except Payment.DoesNotExist:
        logger.error(f"Payment {payment_id} not found")
