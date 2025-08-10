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


class CartMixin:
    def get_cart(self):
        """GET /api/Get or create users cart"""
        if self.request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=self.request.user)
            return cart
        else:
            # handles session-based users
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
    lookup_field = "pk"
    lookup_value_regex = r"\d+"

    def get_queryset(self):
        """
        GET /api/cart/cart
        Returns cart for current user/session
        """
        cart = self.get_cart()
        return Cart.objects.filter(id=cart.id) if cart else Cart.objects.none()

    def merge_cart(self, request, user_cart, session_cart):
        """Merges session-cart with user-cart when he authenticates"""
        with transaction.atomic():
            for session_item in session_cart.items.all():
                user_item, created = CartItem.objects.get_or_create(
                    cart=user_cart,
                    product=session_item.product,
                    defaults={"quantity": session_item.quantity},
                )
                if not created:
                    # if item already exists in user cart, just add the quantity
                    user_item.quantity += session_item.quantity
                    user_item.save()

            # delete after merge
            session_cart.delete()

    @action(detail=False, methods=["post"])
    def add_item(self, request):
        """
        POST /api/cart/cart/add-item/
        Gets item from CartItem and adds it to cart
        """
        cart = self.get_cart()
        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity", 1)

        data = {"product_id": product_id, "quantity": quantity}

        serializer = CartItemSerializer(data=data)
        if serializer.is_valid():

            # prevents duplicate database transactions
            with transaction.atomic():
                item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=serializer.validated_data["product"],
                    # if it does not exist, its created with quantity being equal to quantity
                    defaults={"quantity": quantity},
                )

                # if item exists, add quantity
                if not created:
                    item.quantity += quantity
                    item.save()

            return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CartItemViewSet(CartMixin, viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """
        GET /api/cart/cart-items/
        Return cart items for current user/session
        """
        cart = self.get_cart()
        return CartItem.objects.filter(cart=cart) if cart else CartItem.objects.none()

    def perform_create(self, serializer):
        """
        POST api/cart/cart-items/
        Auto assigns current cart
        """
        cart = self.get_cart()
        serializer.save(cart=cart)

    def update(self, request, *args, **kwargs):
        """
        PUT/PATCH /api/cart/cart-items/<id>/
        Updates quantity
        """
        response = super().update(request, *args, **kwargs)
        cart = self.get_cart()
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        DELETE /api/cart/cart-items/<id>/
        Removes an item
        """
        super().destroy(request, *args, **kwargs)
        cart = self.get_cart()
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)
