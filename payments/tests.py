from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from orders.models import Order, OrderItem
from products.models import Products
from payments.models import Payment
from decimal import Decimal

User = get_user_model()


class PaymentTests(APITestCase):
    def setUp(self):
        # Create test users with unique emails and product/order setup
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="payuser",
            password="testpass123",
            email="payuser@example.com"
        )
        self.admin_user = User.objects.create_superuser(
            username="adminuser",
            password="adminpass",
            email="adminuser@example.com"
        )
        self.product = Products.objects.create(name="Pay Product", price=30.0, stock=50, reserved=0)
        self.order = Order.objects.create(user=self.user, total_amount=Decimal("60.00"), status="pending")
        OrderItem.objects.create(order=self.order, product=self.product, quantity=2, unit_price=self.product.price)

    def test_payment_list_admin(self):
        # Admin user can see all payments
        self.client.force_authenticate(user=self.admin_user)
        Payment.objects.create(
            transaction_id="tx123",
            order=self.order,
            amount=self.order.total_amount,
            payment_method="card",
            status="completed",
        )
        url = reverse("payment-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Handle possible pagination structure
        data = response.data.get("results", response.data) if isinstance(response.data, dict) else response.data
        self.assertTrue(len(data) >= 1)

    def test_payment_list_non_admin(self):
        # Regular user should see no payments
        self.client.force_authenticate(user=self.user)
        url = reverse("payment-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Handle possible pagination structure
        data = response.data.get("results", response.data) if isinstance(response.data, dict) else response.data
        self.assertEqual(len(data), 0)

    def test_confirm_payment_success(self):
        # Confirm payment succeeds and updates order status and stock
        url = reverse("payment-confirm-payment")
        data = {
            "transaction_id": "tx999",
            "order_id": self.order.id,
            "payment_method": "mpesa",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        payment = Payment.objects.filter(transaction_id="tx999").first()
        self.assertIsNotNone(payment)
        self.assertEqual(payment.status, "confirmed")

        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "completed")

        self.product.refresh_from_db()
        self.assertEqual(self.product.reserved, 0)

    def test_confirm_payment_missing_transaction_id(self):
        # Confirm payment fails if transaction_id missing
        url = reverse("payment-confirm-payment")
        data = {"order_id": self.order.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_confirm_payment_invalid_order(self):
        # Confirm payment fails if order_id invalid
        url = reverse("payment-confirm-payment")
        data = {"transaction_id": "tx1000", "order_id": 999999}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_confirm_payment_already_processed(self):
        # Payment with same transaction_id cannot be processed twice
        Payment.objects.create(
            transaction_id="tx2000",
            order=self.order,
            amount=self.order.total_amount,
            payment_method="card",
            status="confirmed",
        )
        url = reverse("payment-confirm-payment")
        data = {
            "transaction_id": "tx2000",
            "order_id": self.order.id,
            "payment_method": "card",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
