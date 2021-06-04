from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Customer, Company
from customer.serializers import CustomerSerializer


CUSTOMER_URL = reverse('customer:customer-list')


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
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            "test@crownkiraappdev.com",
            "password123",
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retreive_customer(self):
        """Test retreiving customer"""
        testcompany2 = Company.objects.create(name="testcompany2")
        testcompany = Company.objects.create(name="testcompany")
        Customer.objects.create(name='testcustomer', company=testcompany)
        Customer.objects.create(name='testcustomer2', company=testcompany2)

        res = self.client.get(CUSTOMER_URL)

        customers = Customer.objects.all().order_by('id')
        serializer = CustomerSerializer(customers, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_customer_not_limited_to_user(self):
        """Test that customers returned are visible by every user"""
        testcompany2 = Company.objects.create(name="testcompany2")
        testcompany = Company.objects.create(name="testcompany")
        Customer.objects.create(name='testcustomer', company=testcompany)
        Customer.objects.create(name='testcustomer2', company=testcompany2)
        testuser = get_user_model().objects.create_user(
            "testsales@crownkiraappdev.com" "password1234"
        )
        res = self.client.get(CUSTOMER_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

        self.user = testuser
        self.client.force_authenticate(self.user)

        res = self.client.get(CUSTOMER_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_create_customer_successful(self):
        """Test creating a new customer"""
        self.Company = Company.objects.create(name="testcompany")
        payload = {
            'company': self.Company.id,
            'name': 'testname',
        }
        self.client.post(CUSTOMER_URL, payload)
        exists = Customer.objects.filter(company=payload['company'])
        self.assertTrue(exists)

    def test_create_customer_invalid(self):
        """Test creating a new customer"""
        self.Company = Company.objects.create(name="testcompany")
        payload = {
            'company': self.Company.id,
            'name': '',
        }
        res = self.client.post(CUSTOMER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
