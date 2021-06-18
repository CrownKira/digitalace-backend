from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Customer, Company

# from customer.serializers import CustomerSerializer


CUSTOMER_URL = reverse("customer:customer-list")


class PublicCustomerApiTest(TestCase):
    """Test the publicly available Customer API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retreiving customers"""
        res = self.client.get(CUSTOMER_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCustomerApiTest(TestCase):
    """Test authorized user customer API"""

    # TODO: currently test for owners only.
    # Extend the test cases to test for employees too
    # (once employee is implemented)
    def setUp(self):
        self.company = Company.objects.create(name="testcompany")
        self.user = get_user_model().objects.create_user(
            "test@crownkiraappdev.com",
            "password123",
            is_staff=True,
            company=self.company,
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    # TODO: exclude image/thumbnail from res.data
    # def test_retreive_customer(self):
    #     """Test retreiving customer"""
    #     Customer.objects.create(name="testcustomer", company=self.company)
    #     Customer.objects.create(name="testcustomer2", company=self.company)

    #     res = self.client.get(CUSTOMER_URL)
    #     customers = Customer.objects.all().order_by("-id")
    #     serializer = CustomerSerializer(customers, many=True)
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.assertEqual(res.data.get("results", None), serializer.data)

    def test_create_customer_successful(self):
        """Test creating a new customer"""
        payload = {
            "company": self.company,
            "name": "testcustomer",
        }
        self.client.post(CUSTOMER_URL, payload)
        exists = Customer.objects.filter(company=payload["company"])
        self.assertTrue(exists)

    def test_create_customer_invalid(self):
        """Test creating a new customer"""
        payload = {
            "company": self.company,
            "name": "",
        }
        res = self.client.post(CUSTOMER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
