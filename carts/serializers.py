from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Cart, CartItem
from products.models import Products


class ProductNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ["id", "name", "price"]


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductNameSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Products.objects.all(),
        source="product",
        write_only=True
    )
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ["id", "product_id", "product", "quantity", "subtotal"]
        extra_kwargs = {"cart": {"read_only": True}}

    @extend_schema_field(serializers.FloatField)
    def get_subtotal(self, obj) -> float:
        return obj.subtotal()


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "user", "items", "total_price"]

    @extend_schema_field(serializers.FloatField)
    def get_total_price(self, cart) -> float:
        return cart.total_price()
