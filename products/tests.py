# products/tests.py
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from decimal import Decimal

from .models import Products, Category, Inventory, MvtType

User = get_user_model()


class ECommerceAPITests(APITestCase):
    def setUp(self):
        # Create users
        self.admin = User.objects.create_user(
            email='admin@example.com',
            username='adminuser',
            password='adminpass123',
            is_admin=True
        )
        self.customer = User.objects.create_user(
            email='customer@example.com',
            username='customeruser',
            password='customerpass123',
            is_admin=False
        )

        # Create category
        self.category = Category.objects.create(name='Electronics')

        # Create product
        self.product = Products.objects.create(
            name='Laptop',
            stock=10,
            category=self.category,
            price=Decimal('999.99'),
            description='High-performance laptop'
        )

        # URLs
        self.login_url = reverse('token_obtain_pair')
        self.products_url = reverse('products-list')
        self.product_detail = lambda pk: reverse('products-detail', kwargs={'pk': pk})
        self.inventory_url = reverse('inventory-list')
        self.filter_options_url = reverse('products-filter_options')

        # Client
        self.client = APIClient()

    # 1. User Login Tests
    def test_user_login_correct_credentials(self):
        """Test login with correct credentials"""
        data = {
            'email': 'admin@example.com',
            'password': 'adminpass123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_user_login_wrong_credentials(self):
        """Test login with wrong password"""
        data = {
            'email': 'admin@example.com',
            'password': 'wrongpass'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('access', response.data)

    # 2. Adding Products
    def test_admin_can_add_product(self):
        """Test admin can create a product"""
        self.client.force_authenticate(user=self.admin)
        data = {
            'name': 'Phone',
            'stock': 5,
            'category': self.category.id,
            'price': '699.99',
            'description': 'Latest smartphone'
        }
        response = self.client.post(self.products_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)  # 1 from setUp + 1 new

    def test_customer_cannot_add_product(self):
        """Test customer cannot create a product"""
        self.client.force_authenticate(user=self.customer)
        data = {
            'name': 'Forbidden Product',
            'stock': 5,
            'category': self.category.id,
            'price': '100.00'
        }
        response = self.client.post(self.products_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # 3. Deleting Products
    def test_admin_can_delete_product(self):
        """Test admin can delete a product"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(self.product_detail(self.product.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())

    def test_customer_cannot_delete_product(self):
        """Test customer cannot delete a product"""
        self.client.force_authenticate(user=self.customer)
        response = self.client.delete(self.product_detail(self.product.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # 4. Trying to Edit Stock as Customer
    def test_customer_cannot_edit_stock(self):
        """Test customer cannot update stock via product update"""
        self.client.force_authenticate(user=self.customer)
        data = {'stock': 9999}
        response = self.client.patch(self.product_detail(self.product.id), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # 5. Editing Products: Admin vs Customer
    def test_admin_can_edit_product(self):
        """Test admin can update product details"""
        self.client.force_authenticate(user=self.admin)
        data = {'name': 'Updated Laptop', 'price': '1099.99'}
        response = self.client.patch(self.product_detail(self.product.id), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Updated Laptop')
        self.assertEqual(str(self.product.price), '1099.99')

    def test_customer_cannot_edit_product(self):
        """Test customer cannot update product"""
        self.client.force_authenticate(user=self.customer)
        data = {'name': 'Hacked Name'}
        response = self.client.patch(self.product_detail(self.product.id), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ✅ NEW: Inventory Tests

    def test_admin_can_add_stock_in(self):
        """Test admin can add stock via IN movement"""
        self.client.force_authenticate(user=self.admin)
        data = {
            'product': self.product.id,
            'mvt_type': MvtType.IN,
            'quantity': 5,
            'note': 'New shipment'
        }
        response = self.client.post(self.inventory_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 15)  # 10 + 5

    def test_admin_can_add_stock_out(self):
        """Test admin can remove stock via OUT movement"""
        self.client.force_authenticate(user=self.admin)
        data = {
            'product': self.product.id,
            'mvt_type': MvtType.OUT,
            'quantity': 3,
            'note': 'Sold online'
        }
        response = self.client.post(self.inventory_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 7)  # 10 - 3

    def test_admin_cannot_oversell_stock(self):
        """Test admin cannot remove more than available stock"""
        self.client.force_authenticate(user=self.admin)
        data = {
            'product': self.product.id,
            'mvt_type': MvtType.OUT,
            'quantity': 15,  # More than 10 in stock
            'note': 'Attempt to oversell'
        }
        response = self.client.post(self.inventory_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Cannot remove', str(response.data))

    def test_customer_cannot_add_inventory(self):
        """Test customer cannot add inventory movement"""
        self.client.force_authenticate(user=self.customer)
        data = {
            'product': self.product.id,
            'mvt_type': MvtType.IN,
            'quantity': 10
        }
        response = self.client.post(self.inventory_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_inventory_list_accessible_to_admin(self):
        """Test admin can list inventory"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.inventory_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_inventory_list_not_accessible_to_customer(self):
        """Test customer cannot list inventory"""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(self.inventory_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ✅ NEW: Missing Test Cases

    def test_filter_options_returns_movement_types(self):
        """Test filter_options includes movement types"""
        response = self.client.get(self.filter_options_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('movement_types', response.data)
        self.assertGreater(len(response.data['movement_types']), 0)

    def test_product_stock_updates_on_inventory_save(self):
        """Test stock is auto-updated when inventory is saved"""
        inventory = Inventory.objects.create(
            product=self.product,
            mvt_type=MvtType.IN,
            quantity=10,
            note='Initial stock'
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 20)  # 10 + 10

    def test_inventory_str_method(self):
        """Test Inventory __str__ method"""
        inventory = Inventory.objects.create(
            product=self.product,
            mvt_type=MvtType.IN,
            quantity=5,
            note='Test'
        )
        self.assertIn('Laptop', str(inventory))
        self.assertIn('IN', str(inventory))

    def test_product_str_method(self):
        """Test Product __str__ method"""
        self.assertEqual(str(self.product), 'Laptop')

    def test_category_str_method(self):
        """Test Category __str__ method"""
        self.assertEqual(str(self.category), 'Electronics')
