from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='order.user.username')
    
    class Meta:
        model = Payment
        fields = (
            "id",
            "order",
            "user",
            "payment_method",
            "transaction_id",
            "created_at",
        )
