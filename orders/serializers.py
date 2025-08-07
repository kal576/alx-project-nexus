from .models import Order, OrderItem
from products.serializers import ProductsSerializer
from rest_framework import serializers
from products.models import Products
from django.db import transaction
from decimal import Decimal

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductsSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Products.objects.all(),
        source='product',
        write_only=True
    )

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_id', 'quantity', 'unit_price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    total_amount = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'items', 'total_amount', 'created_at']

    def create(self, validated_data):
        """
        checks whether there is enough stock before making an order and calculates the total amount
        """
        items_data = validated_data.pop('items')
        total = Decimal('0.00')

        with transaction.atomic():
            for item in items_data:
                product = item['product']
                quantity = item['quantity']
                unit_price = item['unit_price']

                #check if there is enough stock
                if not product.can_sell(quantity):
                    raise serializers.ValidationError(f"Not enough stock. Available: {product.stock}")

                #calculate the total
                total += quantity * float(unit_price)

            order = Order.objects.create(
                        total_amount=total, 
                        **validated_data
                        )

            #create the order item
            for item in items_data:
                OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        unit_price=unit_price
                        )

                order.save()
                return order

