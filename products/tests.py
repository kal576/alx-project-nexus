from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from products.models import Products, Category, MvtType

User = get_user_model()

class ProductsTests(APITestCase):
    def setUp(self):
        # Create users: one admin and one regular user
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass"
        )
        self.regular_user = User.objects.create_user(
            username="user", email="user@example.com", password="userpass"
        )
        # Create a category and product
        self.category = Category.objects.create(name="Test Category")
        self.product = Products.objects.create(
            name="Test Product",
            price=100.00,
            stock=10,
            reserved=0,
            category=self.category,
        )
        self.client = APIClient()

    def test_list_products_anonymous(self):
        """Anonymous users can list products"""
        url = reverse("products-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Handle possible pagination in response
        data = response.data.get("results", response.data) if isinstance(response.data, dict) else response.data
        self.assertTrue(any(p["name"] == self.product.name for p in data))

    def test_stock_movement_unauthenticated(self):
        """Unauthenticated users get 401 on stock movement (admin-only)"""
        url = reverse("products-stock-movement", args=[self.product.id])
        data = {"mvt_type": MvtType.IN, "quantity": 5}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_stock_movement_non_admin(self):
        """Non-admin authenticated users get 403 Forbidden on stock movement"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse("products-stock-movement", args=[self.product.id])
        data = {"mvt_type": MvtType.IN, "quantity": 5}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_stock_movement_admin_valid(self):
        """Admin can successfully perform stock movement in (add stock)"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("products-stock-movement", args=[self.product.id])
        data = {"mvt_type": MvtType.IN, "quantity": 5, "note": "Restocking"}
        old_stock = self.product.stock
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, old_stock + 5)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["message"], "Stock updated successfully")

    def test_stock_movement_admin_invalid(self):
        """Admin cannot remove more stock than available"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("products-stock-movement", args=[self.product.id])
        data = {"mvt_type": MvtType.OUT, "quantity": self.product.stock + 1}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("quantity", response.data)

