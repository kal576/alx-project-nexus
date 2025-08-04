from .models import Order, OrderItem
from products.serializers import ProductSerializer
from rest_framework import serializers

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'unit_price']

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
        order = Order.objects.create(**validated_data)
        total = 0

        for item in items_data:
            product = item['product']
            quantity = item['quantity']
            unit_price = item['unit_price']

            #check if there is enough stock
            if not product.can_sell(quantity):
                raise serializers.ValidationError(f"Not enough stock. Available: {product.stock}")

            #calculate the total
            total += quantity * unit_price

            #create the order item
            OrderItem.objects.create(order=order, product=product, quantity=quantity, unit_price=unit_price)

        order.total_amount = total
        order.save()
        return order

