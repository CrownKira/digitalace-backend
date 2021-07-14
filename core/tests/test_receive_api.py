from core.models.transaction import PurchaseOrder, Receive
from core.models.user import Company
from core.models.maintenance import Supplier
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from supplier.serializers import ReceiveSerializer

RECEIVE_URL = reverse("supplier:receive-list")


class PublicReceiveApiTest(TestCase):
    """Test the publicly available receive API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retreiving receive"""
        res = self.client.get(RECEIVE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateReceiveApiTest(TestCase):
    """Test authorized user receive API"""

    def setUp(self):
        self.company = Company.objects.create(name="testcompany")
        self.supplier = Supplier.objects.create(
            company=self.company, name="testsupplier"
        )
        self.user = get_user_model().objects.create_user(
            "test@crownkiraappdev.com",
            "password123",
            is_staff=True,
            company=self.company,
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retreive_receive(self):
        """Test retreiving receive"""
        supplier = Supplier.objects.create(
            company=self.company, name="testsupplier"
        )
        purchase_order = PurchaseOrder.objects.create(
            supplier=supplier,
            company=self.company,
            date="2001-01-10",
            # payment_date="2001-01-10",
            gst_rate="0.07",
            discount_rate="0",
            gst_amount="0",
            discount_amount="0",
            net="0",
            total_amount="0",
            grand_total="0",
            status="PD",
        )
        purchase_order2 = PurchaseOrder.objects.create(
            supplier=supplier,
            company=self.company,
            date="2001-01-10",
            # payment_date="2001-01-10",
            gst_rate="0.07",
            discount_rate="0",
            gst_amount="0",
            discount_amount="0",
            net="0",
            total_amount="0",
            grand_total="0",
            status="PD",
        )
        Receive.objects.create(
            supplier=supplier,
            purchase_order=purchase_order,
            company=self.company,
            date="2001-01-10",
            payment_date="2001-01-10",
            gst_rate="0.07",
            discount_rate="0",
            gst_amount="0",
            discount_amount="0",
            net="0",
            total_amount="0",
            grand_total="0",
            status="PD",
        )
        Receive.objects.create(
            supplier=supplier,
            purchase_order=purchase_order2,
            company=self.company,
            date="2001-01-10",
            payment_date="2001-01-10",
            gst_rate="0.07",
            discount_rate="0",
            gst_amount="0",
            discount_amount="0",
            net="0",
            total_amount="0",
            grand_total="0",
            status="PD",
        )

        res = self.client.get(RECEIVE_URL)

        receives = Receive.objects.all().order_by("-id")
        serializer = ReceiveSerializer(receives, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get("results", None), serializer.data)

    # TODO: rewrite
    # def test_create_receive_successful(self):
    #     """Test creating a new receive"""
    #     purchase_order = PurchaseOrder.objects.create(
    #         supplier=self.supplier,
    #         company=self.company,
    #         date="2001-01-10",
    #         payment_date="2001-01-10",
    #         gst_rate="0.07",
    #         discount_rate="0",
    #         gst_amount="0",
    #         discount_amount="0",
    #         net="0",
    #         total_amount="0",
    #         grand_total="0",
    #         status="CP",
    #     )
    #     payload = {
    #         "supplier": self.supplier,
    #         "company": self.company,
    #         "purchase_order": purchase_order,
    #         "date": "2001-01-10",
    #         "payment_date": "2001-01-10",
    #         "gst_rate": "0.07",
    #         "discount_rate": "0",
    #         "gst_amount": "0",
    #         "discount_amount": "0",
    #         "net": "0",
    #         "total_amount": "0",
    #         "grand_total": "0",
    #         "status": "PD",
    #     }
    #     self.client.post(RECEIVE_URL, payload)
    #     exists = Receive.objects.filter(company=payload["company"])
    #     self.assertTrue(exists)

    # def test_create_receive_invalid(self):
    #     """Test creating a new receive with invalid payload"""
    #     purchase_order = PurchaseOrder.objects.create(
    #         supplier=self.supplier,
    #         company=self.company,
    #         date="2001-01-10",
    #         payment_date="2001-01-10",
    #         gst_rate="0.07",
    #         discount_rate="0",
    #         gst_amount="0",
    #         discount_amount="0",
    #         net="0",
    #         total_amount="0",
    #         grand_total="0",
    #         status="CP",
    #     )
    #     payload = {
    #         "supplier": "",
    #         "company": "",
    #         "purchase_order": purchase_order,
    #         "date": "2001-01-10",
    #         "payment_date": "2001-01-10",
    #         "gst_rate": "0.07",
    #         "discount_rate": "0",
    #         "gst_amount": "0",
    #         "discount_amount": "0",
    #         "net": "0",
    #         "total_amount": "0",
    #         "grand_total": "0",
    #         "status": "PD",
    #     }
    #     res = self.client.post(RECEIVE_URL, payload)

    #     self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
