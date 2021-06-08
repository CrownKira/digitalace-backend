from core.models import PurchaseOrder, Supplier, Company

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from supplier.serializers import PurchaseOrderSerializer

PURCHASEORDER_URL = reverse("supplier:purchaseorder-list")


class PublicPuchaseOrderApiTest(TestCase):
    """Test the publicly available purchase_order API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retreiving purchase order"""
        res = self.client.get(PURCHASEORDER_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivatePurchseOrderApiTest(TestCase):
    """Test authorized user purchase order API"""

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

    def test_retreive_purchase_order(self):
        """Test retreiving purchase order"""
        testsupplier = Supplier.objects.create(
            company=self.company, name="testsupplier"
        )
        testsupplier2 = Supplier.objects.create(
            company=self.company, name="testsupplier2"
        )
        PurchaseOrder.objects.create(
            date="2001-01-10",
            payment_date="2001-01-10",
            gst_rate="0.07",
            discount_rate="0",
            gst_amount="0",
            discount_amount="0",
            net="0",
            total_amount="0",
            grand_total="0",
            supplier=testsupplier,
            company=self.company,
            status="completed",
        )
        PurchaseOrder.objects.create(
            date="2001-01-10",
            payment_date="2001-01-10",
            gst_rate="0.07",
            discount_rate="0",
            gst_amount="0",
            discount_amount="0",
            net="0",
            total_amount="0",
            grand_total="0",
            supplier=testsupplier2,
            company=self.company,
            status="completed",
        )
        res = self.client.get(PURCHASEORDER_URL)

        purchase_orders = PurchaseOrder.objects.all().order_by("-id")
        serializer = PurchaseOrderSerializer(purchase_orders, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get("results", None), serializer.data)

    # Deprecated
    # def test_purchse_order_not_limited_to_user(self):
    #     """Test that purchase order returned are visible by every user"""
    #     testuser = get_user_model().objects.create_user(
    #         "testsales@crownkiraappdev.com", "password1234"
    #     )
    #     testcompany = Company.objects.create(name="testcompany")
    #     testcompany2 = Company.objects.create(name="testcompany2")
    #     testsupplier = Supplier.objects.create(
    #         company=testcompany, name="testsupplier"
    #     )
    #     testsupplier2 = Supplier.objects.create(
    #         company=testcompany, name="testsupplier2"
    #     )
    #     PurchaseOrder.objects.create(
    #         date="2001-01-10",
    #         payment_date="2001-01-10",
    #         gst_rate="0.07",
    #         discount_rate="0",
    #         gst_amount="0",
    #         discount_amount="0",
    #         net="0",
    #         total_amount="0",
    #         grand_total="0",
    #         supplier=testsupplier,
    #         company=testcompany,
    #     )
    #     PurchaseOrder.objects.create(
    #         date="2001-01-10",
    #         payment_date="2001-01-10",
    #         gst_rate="0.07",
    #         discount_rate="0",
    #         gst_amount="0",
    #         discount_amount="0",
    #         net="0",
    #         total_amount="0",
    #         grand_total="0",
    #         supplier=testsupplier2,
    #         company=testcompany2,
    #     )
    #     res = self.client.get(PURCHASEORDER_URL)

    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.assertEqual(len(res.data), 2)

    #     self.user = testuser
    #     self.client.force_authenticate(self.user)

    #     res = self.client.get(PURCHASEORDER_URL)

    def test_create_purchase_order_successful(self):
        """Test creating a new purchase order"""
        self.company = Company.objects.create(name="testcompany")
        self.supplier = Supplier.objects.create(
            company=self.company, name="testsupplier"
        )
        payload = {
            "supplier": self.supplier.id,
            "company": self.company.id,
            "date": "2001-01-10",
            "payment_date": "2001-01-10",
            "gst_rate": "0.07",
            "discount_rate": "0",
            "gst_amount": "0",
            "discount_amount": "0",
            "net": "0",
            "total_amount": "0",
            "grand_total": "0",
            "status": "completed",
        }
        self.client.post(PURCHASEORDER_URL, payload)
        exists = PurchaseOrder.objects.filter(company=payload["company"])
        self.assertTrue(exists)

    def test_create_purchase_order_invalid(self):
        """Test creating a new invoice"""
        self.company = Company.objects.create(name="testcompany")
        self.supplier = Supplier.objects.create(
            company=self.company, name="testsupplier"
        )
        payload = {
            "supplier": self.supplier.id,
            "company": "",
            "date": "2001-01-10",
            "payment_date": "2001-01-10",
            "gst_rate": "0.07",
            "discount_rate": "0",
            "gst_amount": "0",
            "discount_amount": "0",
            "net": "0",
            "total_amount": "0",
            "grand_total": "0",
            "status": "completed",
        }
        res = self.client.post(PURCHASEORDER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
