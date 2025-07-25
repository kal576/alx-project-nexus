from rest_framework import serializers
from .models import Products, Category, Inventory, MvtType

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductsSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Products
        fields = '__all__'

class InventorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='products.name', read_only=True)

    class Meta:
        model = Inventory
        fields = [
            'id', 'product', 'product_name', 'mvt_type',
            'quantity', 'note', 'created_at'
        ]

class StockMovementSerializer(serializers.ModelSerializer):
    """
    Serializer to validate movement of stocks input
    """
    mvt_type = serializers.ChoiceField(choices=MvtType.choices)
    quantity = serializers.IntegerField(min_value=1)
    note = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        product = self.context['product']
        mvt_type = data['mvt_type']
        quantity = data['quantity']

        #prevents removing quantity above current stock
        if mvt_ype == MvtType.OUT and not product.can_sell(quantity):
            raise serializers.ValidationError(f"Cannot remove {quantity} units. Available: {product.stock}")
        return data

