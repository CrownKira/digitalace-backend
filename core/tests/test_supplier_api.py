from core.models import Supplier, Company

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from supplier.serializers import SupplierSerializer

SUPPLIER_URL = reverse("supplier:supplier-list")


# TODO: why the descriptions all have invoice in it
# and some testcases are named invoice?
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
        self.company = Company.objects.create(name="testcompany")
        self.user = get_user_model().objects.create_user(
            "test@crownkiraappdev.com",
            "password123",
            is_staff=True,
            company=self.company,
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retreive_supplier(self):
        """Test retreiving supplier"""
        Supplier.objects.create(
            company=self.company,
            name="testsupplier",
            address="testaddress",
            contact="testcontact",
            term="testterm",
            phone_no="testphone_no",
        )
        Supplier.objects.create(
            company=self.company,
            name="testsupplier2",
            address="testaddress",
            contact="testcontact",
            term="testterm",
            phone_no="testphone_no",
        )
        res = self.client.get(SUPPLIER_URL)

        suppliers = Supplier.objects.all().order_by("-id")
        serializer = SupplierSerializer(suppliers, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get("results", None), serializer.data)

    # Deprecated
    # def test_supplier_not_limited_to_user(self):
    #     """Test that suppliers returned are visible by every user"""
    #     testuser = get_user_model().objects.create_user(
    #         "testsales@crownkiraappdev.com" "password1234"
    #     )
    #     testcompany = Company.objects.create(name="testcompany")
    #     Supplier.objects.create(
    #         company=testcompany,
    #         name="testsupplier",
    #         address="testaddress",
    #         contact="testcontact",
    #         term="testterm",
    #         phone_no="testphone_no",
    #     )
    #     Supplier.objects.create(
    #         company=testcompany,
    #         name="testsupplier2",
    #         address="testaddress",
    #         contact="testcontact",
    #         term="testterm",
    #         phone_no="testphone_no",
    #     )
    #     res = self.client.get(SUPPLIER_URL)

    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.assertEqual(len(res.data), 2)

    #     self.user = testuser
    #     self.client.force_authenticate(self.user)

    #     res = self.client.get(SUPPLIER_URL)

    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.assertEqual(len(res.data), 2)

    def test_create_supplier_successful(self):
        """Test creating a new Supplier"""
        payload = {
            "company": self.company,
            "attention": self.user,
            "name": "testsupplier2",
            "address": "testaddress",
            "contact": "testcontact",
            "term": "testterm",
            "phone_no": "testphone_no",
        }
        self.client.post(SUPPLIER_URL, payload)
        exists = Supplier.objects.filter(company=payload["company"])
        self.assertTrue(exists)

    # TODO: rewrite
    # def test_create_invoice_invalid(self):
    #     """Test creating a new supplier with invalid payload"""
    #     payload = {
    #         "company": "",
    #         "attention": self.user,
    #         "name": "testsupplier2",
    #         "address": "testaddress",
    #         "contact": "testcontact",
    #         "term": "testterm",
    #         "phone_no": "testphone_no",
    #     }
    #     res = self.client.post(SUPPLIER_URL, payload)

    #     self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
