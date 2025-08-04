from rest_framework import viewsets, permissions, status
from .serializers import OrderSerializer
from .models import Order, OrderItem
from products.models import Products
from decimal import Decimal
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from ratelimit.decorators import ratelimit

class OrderViewSet(viewsets.ModelViewset):
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]
    
    #returns all orders if user is admin else returns only the users orders
    def get_queryset(self):
        if self.request.user.is_admin:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)


    #fbv to order an item. has rate limitting to prevent attacks since users dont have to log in
    @ratelimit(key='ip', rate='5/m', method='POST', block=True)
    @api_view(['POST'])
    @permission_classes([AllowAny])
    def order_now(request):
        user = request.user
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity',1))

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product Does Not Exist"},status 400)

        if user.is_authenticated:
            order = Order.objects.create(user=user)
        order = Order.objects.create()
        
        OrderItem.objects.create(
                order=order,
                product=product,
                quantity-quantity,
                unit_price=unit_price
                )

        return Response ({"message":"Order created successfully. Please proceed to checkout"}, status=200)
