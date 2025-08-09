from rest_framework.viewsets import ReadOnlyModelViewSet
from .models import Payment
from products.models import Inventory
from orders.models import Order
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import PaymentSerializer
from rest_framework import status
from rest_framework.response import Response
from django.db import transaction
from .tasks import send_payment_confirmation


class PaymentViewSet(ReadOnlyModelViewSet):
    """
    Handles payment-related operations such as confirming payments and listing all payments.
    """

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return self.queryset.select_related("order", "user").all()
        elif self.request.user.is_authenticated:
            return (
                self.queryset.filter(user=self.request.user)
                .select_related("order")
                .all()
            )

        return self.queryset.none()

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def confirm_payment(self, request):
        """
        Confirms payment(called by the payment gateway webhook) and deducts the reserved stock
        Updates the order status
        """
        transaction_id = request.data.get("transaction_id")
        order_id = request.data.get("order_id")
        payment_method = request.data.get("payment_method")

        if not transaction_id or not order_id:
            return Response(
                {"error": "Transaction ID and Order ID are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if Payment.objects.filter(transaction_id=transaction_id).exists():
            return Response(
                {"error": "The payment has already been processed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            payment = Payment.objects.create(
                order=order,
                user=self.request.user if self.request.user.is_authenticated else None,
                amount=order.total_amount,
                payment_method=payment_method,
                status="confirmed",
                transaction_id=transaction_id,
            )

            # update order status
            order.status = "completed"
            order.save()

            # deduct reserved stock for each order item
            for item in order.items.all():
                product = item.product
                product.reserved -= item.quantity
                product.save(update_fields=["reserved"])

                # Log inventory movement
                Inventory.objects.create(
                    product=product,
                    mvt_type="OUT",
                    quantity=item.quantity,
                )

            # Send confirmation email async
            send_payment_confirmation.delay(payment.id)

            return Response(
                {
                    "message": "Payment confirmed.",
                    "payment_id": payment.id,
                    "order_id": order.id,
                },
                status=status.HTTP_200_OK,
            )
