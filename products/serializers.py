from rest_framework import serializers
from .models import Products, Category, Inventory, MvtType


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ProductsSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    available_stock = serializers.ReadOnlyField()

    class Meta:
        model = Products
        fields = [f.name for f in Products._meta.fields if f.name != "reserved"] + [
            "category_name",
            "available_stock",
        ]
        


class AdminProductSerializer(ProductsSerializer):
    class Meta:
        read_only_fields = ["reserved", "available_stock"]


class InventorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = Inventory
        fields = [
            "id",
            "product",
            "product_name",
            "mvt_type",
            "quantity",
            "note",
            "created_at",
        ]
        read_only_fields = ["created_at", "product_name"]


class StockMovementSerializer(serializers.Serializer):
    """
    Serializer to validate stock movement input.
    Use with context={'product': product_instance} in view.
    """
    mvt_type = serializers.ChoiceField(choices=MvtType.choices)
    quantity = serializers.IntegerField(min_value=1)
    note = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate(self, data):
        product = self.context.get("product")
        if not product:
            raise serializers.ValidationError("Product context is required.")

        mvt_type = data["mvt_type"]
        quantity = data["quantity"]

        # Prevent removing more than available stock
        if mvt_type == MvtType.OUT and not product.can_sell(quantity):
            raise serializers.ValidationError({
                "quantity": f"Cannot remove {quantity} units. Only {product.stock} available for sale."
            })

        return data

    def create(self, validated_data):
        product = self.context["product"]
        user = self.context["request"].user if self.context.get("request") else None

        inventory = Inventory.objects.create(
            product=product,
            mvt_type=validated_data["mvt_type"],
            quantity=validated_data["quantity"],
            note=validated_data.get("note", ""),
        )

        # Update product stock
        if validated_data["mvt_type"] == MvtType.IN:
            product.stock += validated_data["quantity"]
        elif validated_data["mvt_type"] == MvtType.OUT:
            product.stock -= validated_data["quantity"]
        product.save()

        return validated_data