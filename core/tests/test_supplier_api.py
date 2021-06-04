from core.models import Supplier, Company

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from supplier.serializers import SupplierSerializer

SUPPLIER_URL = reverse("supplier:supplier-list")


class PublicSupplierApiTest(TestCase):
    """Test the publicly available invoice API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retreiving invoices"""
        res = self.client.get(SUPPLIER_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateSupplierApiTest(TestCase):
    """Test authorized user Supplier API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            "test@crownkiraappdev.com",
            "password123",
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retreive_supplier(self):
        """Test retreiving supplier"""
        testcompany = Company.objects.create(name="testcompany")
        Supplier.objects.create(
            company=testcompany,
            name='testsupplier',
            address='testaddress',
            area='testarea',
            contact='testcontact',
            term='testterm',
            phone_no='testphone_no'
        )
        Supplier.objects.create(
            company=testcompany,
            name='testsupplier2',
            address='testaddress',
            area='testarea',
            contact='testcontact',
            term='testterm',
            phone_no='testphone_no'
        )
        res = self.client.get(SUPPLIER_URL)

        suppliers = Supplier.objects.all().order_by("id")
        serializer = SupplierSerializer(suppliers, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_supplier_not_limited_to_user(self):
        """Test that suppliers returned are visible by every user"""
        testuser = get_user_model().objects.create_user(
            "testsales@crownkiraappdev.com" "password1234"
        )
        testcompany = Company.objects.create(name="testcompany")
        Supplier.objects.create(
            company=testcompany,
            name='testsupplier',
            address='testaddress',
            area='testarea',
            contact='testcontact',
            term='testterm',
            phone_no='testphone_no'
        )
        Supplier.objects.create(
            company=testcompany,
            name='testsupplier2',
            address='testaddress',
            area='testarea',
            contact='testcontact',
            term='testterm',
            phone_no='testphone_no'
        )
        res = self.client.get(SUPPLIER_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

        self.user = testuser
        self.client.force_authenticate(self.user)

        res = self.client.get(SUPPLIER_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_create_supplier_successful(self):
        """Test creating a new Supplier"""
        self.Company = Company.objects.create(name="testcompany")
        payload = {
            'company': self.Company.id,
            'attention': self.user.id,
            'name': 'testsupplier2',
            'address': 'testaddress',
            'area': 'testarea',
            'contact': 'testcontact',
            'term': 'testterm',
            'phone_no': 'testphone_no'
        }
        self.client.post(SUPPLIER_URL, payload)
        exists = Supplier.objects.filter(company=payload["company"])
        self.assertTrue(exists)

    def test_create_invoice_invalid(self):
        """Test creating a new supplier with invalid payload"""
        self.Company = Company.objects.create(name="testcompany")
        payload = {
            'company': '',
            'attention': self.user.id,
            'name': 'testsupplier2',
            'address': 'testaddress',
            'area': 'testarea',
            'contact': 'testcontact',
            'term': 'testterm',
            'phone_no': 'testphone_no'
        }
        res = self.client.post(SUPPLIER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
