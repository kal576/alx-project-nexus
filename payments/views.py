from .models import Payment
from products.models import Inventory
from order.models import Order
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.respose import Response
from django.db import transaction

@api_view(['POST'])
@permission_classes(AllowAny)
def confirm_payment(request):
    """
    Confirms payment(called by the payment gateway webhook) and deducts the reserved stock
    Updates the order status
    """
    transaction_id = request.data.get('transaction_id')
    order_id = request.data.get('order_id')

    with transaction.atomic():
        payment.status = 'confirmed'
        payment.transaction_id = transaction_id
        payment.save()

        #update order status
        order = payment.order
        order.status = 'confirmed'
        order.save()

        #deduct reserved stock
        product = item.product
        product.reserved -= quantity
        product.save(update_fields=['reserved'])

        # Log inventory movement
        Inventory.objects.create(
                product=product,
                mvt_type='OUT',
                quantity=item.quantity,
                )

        # Send confirmation email async
        send_payment_confirmation.delay(payment.id)

        return Response({
        "message": "Payment confirmed.",
        "payment_id": payment.id,
        "order_id": order.id
    }, status=status.HTTP_200_OK)

