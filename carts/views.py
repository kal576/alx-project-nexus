from django.shortcuts import render
from .serializers import CartSerializer, CartItemSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from .models import Cart, CartItem
from products.models import Products
from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter


class CartMixin:
    def get_cart(self):
        """GET /api/cart/ - Get or create user's cart"""
        # Prevent errors during schema generation
        if getattr(self, "swagger_fake_view", False):
            return None

        if self.request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=self.request.user)
            return cart

        # Handle session-based cart
        if not hasattr(self.request, "session"):
            return None  # No session available (e.g., during schema gen)

        if not self.request.session.session_key:
            self.request.session.create()

        session_key = self.request.session.session_key
        cart, _ = Cart.objects.get_or_create(session_key=session_key)
        return cart


class CartViewSet(CartMixin, viewsets.ReadOnlyModelViewSet):
    """
    Allows only viewing of the cart
    """
    serializer_class = CartSerializer
    permission_classes = [AllowAny]
    queryset = Cart.objects.none()
    lookup_field = "pk"
    lookup_value_regex = r"\d+"

    def get_queryset(self):
        """
        GET /api/cart/cart/
        Returns cart for current user/session
        """
        if getattr(self, "swagger_fake_view", False):
            return Cart.objects.none()
        cart = self.get_cart()
        return Cart.objects.filter(id=cart.id) if cart else Cart.objects.none()

    @extend_schema(
        request=CartItemSerializer,
        responses={200: CartSerializer},
        description="Add an item to the cart. Creates item if not exists, otherwise increments quantity."
    )
    @action(detail=False, methods=["post"])
    def add_item(self, request):
        """
        POST /api/cart/cart/add-item/
        Adds an item to the cart.
        """
        cart = self.get_cart()
        if not cart:
            return Response({"error": "Cart could not be created."}, status=status.HTTP_400_BAD_REQUEST)

        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity", 1)

        if not product_id:
            return Response({"product_id": "This field is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Products.objects.get(id=product_id)
        except Products.DoesNotExist:
            return Response({"product_id": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        data = {"product": product.id, "quantity": quantity}

        serializer = CartItemSerializer(data=data)
        if serializer.is_valid():
            with transaction.atomic():
                item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=product,
                    defaults={"quantity": quantity}
                )
                if not created:
                    item.quantity += quantity
                    item.save()

            return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CartItemViewSet(CartMixin, viewsets.ModelViewSet):
    """
    CRUD operations for CartItem
    """
    serializer_class = CartItemSerializer
    permission_classes = [AllowAny]
    queryset = CartItem.objects.none()
    lookup_field = "pk"
    lookup_value_regex = r"\d+"

    def get_queryset(self):
        """
        GET /api/cart/cart-items/
        Returns cart items for current user/session
        """
        if getattr(self, "swagger_fake_view", False):
            return CartItem.objects.none()
        cart = self.get_cart()
        return CartItem.objects.filter(cart=cart) if cart else CartItem.objects.none()

    @extend_schema(
        description="Automatically assigns the current cart to the new item."
    )
    def perform_create(self, serializer):
        cart = self.get_cart()
        if not cart:
            raise serializers.ValidationError("Cart could not be created.")
        serializer.save(cart=cart)

    @extend_schema(
        responses={200: CartSerializer},
        description="Updates the quantity of a cart item and returns the updated cart."
    )
    def update(self, request, *args, **kwargs):
        """
        PUT/PATCH /api/cart/cart-items/<int:pk>/
        Updates quantity of a cart item.
        """
        response = super().update(request, *args, **kwargs)
        cart = self.get_cart()
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

    @extend_schema(
        responses={200: CartSerializer},
        description="Removes an item from the cart and returns the updated cart."
    )
    def destroy(self, request, *args, **kwargs):
        """
        DELETE /api/cart/cart-items/<int:pk>/
        Removes an item from the cart.
        """
        super().destroy(request, *args, **kwargs)
        cart = self.get_cart()
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)