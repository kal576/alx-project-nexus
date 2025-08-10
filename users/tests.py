from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class UserAuthTests(APITestCase):
    def setUp(self):
        # Create a test user for login/logout tests
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpass123",
            phone_number="1234567890"
        )
        # URLs used in tests
        self.register_url = reverse("user-registration")
        self.logout_url = reverse("logout")

    def test_register_user_success(self):
        """Test successful user registration"""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpass123",
            "phone_number": "0987654321",
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["user"]["email"], data["email"])

    def test_logout_success(self):
        """Test logout blacklists the refresh token"""
        # Generate refresh token for the user
        refresh = RefreshToken.for_user(self.user)
        data = {"refresh": str(refresh)}

        # Authenticate user before logout
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.logout_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)

    def test_logout_invalid_token(self):
        """Test logout fails with invalid refresh token"""
        invalid_data = {"refresh": "invalidtoken"}

        # Authenticate user before logout
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.logout_url, invalid_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
