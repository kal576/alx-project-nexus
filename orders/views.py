from rest_framework import viewsets, permissions, status
from .serializers import OrderSerializer
from .models import Order, OrderItem
from carts.models import Cart
from payments.models import Payment
from products.models import Products
from decimal import Decimal
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.decorators import action, throttle_classes
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound
from rest_framework.throttling import UserRateThrottle
from .tasks import send_order_confirmation
from django.db import transaction


class OrderNowThrottle(UserRateThrottle):
    scope = "order_now"


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]

    # returns all orders if user is admin else returns only the users orders
    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.is_admin:
            return Order.objects.all()
        elif self.request.user.is_authenticated:
            return Order.objects.filter(user=self.request.user)

        # empty queryset for anonymous users
        return Order.objects.none()

    @action(detail=False, methods=["post"], url_path="order-now")
    @throttle_classes([OrderNowThrottle])
    def order_now(self, request):
        """
        POST /api/orders/now/
        Buy a product directly
        """
        user = request.user
        items = request.data.get("items", [])

        # Validate items
        if not items or not isinstance(items, list):
            return Response({"error": "No items provided"})

        item = items[0]
        product_id = item.get("product_id")
        quantity = int(item.get("quantity", 1))

        try:
            product = Products.objects.get(id=product_id)
        except Products.DoesNotExist:
            return Response({"error": "Product Does Not Exist"}, status=400)

        # Check if there is enough stock
        if not product.can_sell(quantity):
            return Response(
                {"error": f"Not enough stock for {product.name}"}, status=400
            )

        unit_price = product.price
        total_amount = quantity * unit_price

        with transaction.atomic():
            if user.is_authenticated:
                order = Order.objects.create(
                    user=user, total_amount=total_amount, status="pending"
                )
            else:
                order = Order.objects.create(
                    total_amount=total_amount, status="pending"
                )

            # update payment status
            Payment.objects.create(status="pending")

            # reserve stock awaiting payment
            product.reserved += quantity
            product.save(update_fields=["reserved"])

            OrderItem.objects.create(
                order=order, product=product, quantity=quantity, unit_price=unit_price
            )

            # send order confirmation email
            send_order_confirmation.delay(order.id)

        return Response(
            {"message": "Order created successfully. Please proceed to payment"},
            status=200,
        )

    def get_cart(self, request):
        """Gets an existing cart for checkout, else raises an error"""
        user = request.user
        session_key = request.session.session_key

        if user.is_authenticated:
            cart = Cart.objects.filter(user=user).first()
        else:
            cart = Cart.objects.filter(session_key=session_key).first()

        if not cart:
            raise NotFound("Please add items to cart before checkout")

        return cart

    @action(detail=False, methods=["post"], url_path="checkout")
    def checkout(self, request):
        """
        POST /api/orders/checkout/
        Create an order from cart
        """
        user = request.user
        cart = self.get_cart(request)
        total_amount = Decimal(0.00)

        if not cart.items.exists():
            return Response({"error": "Cart is empty"}, status=400)

        with transaction.atomic():
            # calculate total amount
            for item in cart.items.all():
                product = item.product
                if not product.can_sell(item.quantity):
                    return Response(
                        {"error": f"Not enough stock for {product.name}"}, status=400
                    )

                total_amount += item.quantity * float(item.product.price)

                # reserve the product
                item.product.reserved += item.quantity
                item.product.save(update_fields=["reserved"])

            # create an order
            order = Order.objects.create(
                user=user if user.is_authenticated else None,
                total_amount=total_amount,
                status="pending",
            )

            # create order items
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    unit_price=item.product.price,
                )

            # send order confirmation email
            send_order_confirmation.delay(order.id)

        return Response(
            {
                "message": "Order created from cart successfully. Please proceed to payment"
            },
            status=200,
        )

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        """
        POST /api/orders/cancel-order/
        Cancels order
        """

        order = self.get_object()

        if order.status == "cancelled":
            return Response(
                {"error": "Order already cancelled"}, status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            # Release reserved stock
            for item in order.items.all():
                product = item.product
                product.reserved -= item.quantity
                product.save(update_fields=["reserved"])

            # Update order status
            order.status = "cancelled"
            order.save()

            # Update payment status
            if hasattr(order, "payment"):
                order.payment.status = "cancelled"
                order.payment.save()

        return Response({"message": "Order cancelled. Stock released."})
