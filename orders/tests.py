from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from products.models import Products
from carts.models import Cart, CartItem
from .models import Order, OrderItem
from decimal import Decimal

User = get_user_model()


class OrderTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="orderuser", password="testpass123")
        self.product = Products.objects.create(name="Order Product", price=20.0, stock=100, reserved=0)
        self.client = APIClient()

    def test_order_now_authenticated(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("order-order-now")
        data = {"items": [{"product_id": self.product.id, "quantity": 2}]}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order = Order.objects.filter(user=self.user).last()
        self.assertIsNotNone(order)
        self.assertEqual(order.total_amount, Decimal("40.0"))
        self.assertEqual(order.items.count(), 1)
        item = order.items.first()
        self.assertEqual(item.product, self.product)
        self.assertEqual(item.quantity, 2)

    def test_order_now_anonymous(self):
        url = reverse("order-order-now")
        data = {"items": [{"product_id": self.product.id, "quantity": 1}]}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order = Order.objects.filter(user=None).last()
        self.assertIsNotNone(order)

    def test_order_now_invalid_product(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("order-order-now")
        data = {"items": [{"product_id": 9999, "quantity": 1}]}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_now_insufficient_stock(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("order-order-now")
        data = {"items": [{"product_id": self.product.id, "quantity": 1000}]}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_checkout_authenticated(self):
        self.client.force_authenticate(user=self.user)
        # Setup a cart with items
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=3)

        url = reverse("order-checkout")
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order = Order.objects.filter(user=self.user).last()
        self.assertIsNotNone(order)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.total_amount, Decimal("60.0"))

    def test_checkout_empty_cart(self):
        self.client.force_authenticate(user=self.user)
        cart = Cart.objects.create(user=self.user)
        url = reverse("order-checkout")
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_checkout_anonymous(self):
        session = self.client.session
        session.save()
        cart = Cart.objects.create(session_key=session.session_key)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)

        url = reverse("order-checkout")
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order = Order.objects.filter(user=None).last()
        self.assertIsNotNone(order)
        self.assertEqual(order.items.count(), 1)

    def test_cancel_order(self):
        self.client.force_authenticate(user=self.user)
        order = Order.objects.create(user=self.user, total_amount=50, status="pending")
        OrderItem.objects.create(order=order, product=self.product, quantity=2, unit_price=self.product.price)

        url = reverse("order-cancel", args=[order.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, "cancelled")

    def test_cancel_already_cancelled_order(self):
        self.client.force_authenticate(user=self.user)
        order = Order.objects.create(user=self.user, total_amount=50, status="cancelled")
        url = reverse("order-cancel", args=[order.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_orders_authenticated_user(self):
        self.client.force_authenticate(user=self.user)
        Order.objects.create(user=self.user, total_amount=10, status="pending")
        Order.objects.create(user=None, total_amount=20, status="pending")

        url = reverse("order-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # User should only see their own orders
        for order in response.data:
            self.assertEqual(order["user"], self.user.id)

    def test_get_orders_admin(self):
        admin_user = User.objects.create_superuser(username="admin", password="adminpass")
        self.client.force_authenticate(user=admin_user)
        Order.objects.create(user=self.user, total_amount=10, status="pending")
        Order.objects.create(user=None, total_amount=20, status="pending")

        url = reverse("order-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Admin sees all orders
        self.assertGreaterEqual(len(response.data), 2)
