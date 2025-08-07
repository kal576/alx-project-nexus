from rest_framework import viewsets, permissions, status
from .serializers import OrderSerializer
from .models import Order, OrderItem
from carts.models import Cart
from products.models import Products
from decimal import Decimal
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.decorators import action
from django_ratelimit.decorators import ratelimit
from django.shortcuts import get_object_or_404
from django.db import transaction

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]
    
    #returns all orders if user is admin else returns only the users orders
    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.is_admin:
            return Order.objects.all()
        elif self.request.user.is_authenticated:
            return Order.objects.filter(user=self.request.user)

        #empty queryset for anonymous users
        return Order.objects.none()
    
    #@ratelimit(key='ip', rate='5/m', method='POST', block=True)
    @action(detail=False, methods=['post'], url_path='order-now')
    def order_now(self, request):
        """
        POST /api/orders/now/
        Buy a product directly
        """
        user = request.user
        items = request.data.get('items', [])

        if not items or not isinstance(items, list):
            return Response({"error": "No items provided"})

        item = items[0]
        product_id = item.get('product_id')
        quantity = int(item.get('quantity',1))

        try:
            product = Products.objects.get(id=product_id)
        except Products.DoesNotExist:
            return Response({"error": "Product Does Not Exist"}, status=400)

        unit_price = product.price
        total_amount = quantity * unit_price

        with transaction.atomic():
            if user.is_authenticated:
                order = Order.objects.create(user=user, total_amount=total_amount)
            else:
                order = Order.objects.create(total_amount=total_amount)

            OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price
                )

        return Response ({"message":"Order created successfully. Please proceed to checkout"}, status=200)

    @action(detail=False, methods=['post'], url_path='checkout')
    def checkout(self, request):
        """
        POST /api/orders/checkout/
        Create an order from cart
        """
        if request.user.is_authenticated:
            cart = get_object_or_404(Cart, user=request.user)
        else:
            session_key = request.session.session_key
            if not session_key:
                return Response({"error": "No active session key"}, status=status.HTTP_400_BAD_REQUEST)
            cart = get_object_or_404(Cart, session_key=session_key)

        if not cart.items.exists():
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        items_data = []

        for item in cart.items.all():
            items_data.append({
                'product_id': item.product_id,
                'quantity': item.quantity,
                'unit_price': item.product.price
                })

        serializer = self.get_serializer(data={
            'user': request.user.id if request.user.is_authenticated else None,
            'status': 'pending',
            'items': items_data
            })

        if serializer.is_valid():
            with transaction.atomic():
                order = serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
