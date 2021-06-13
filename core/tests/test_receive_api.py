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


def create_purchase_order(**params):
    return PurchaseOrder.objects.create(
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
        **params
        # supplier=supplier,
        # company=self.company,
    )


def create_receive(**params):
    return Receive.objects.create(
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
        **params
        # supplier=supplier,
        # purchase_order=purchase_order,
        # company=self.company,
    )


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
        self.company2 = Company.objects.create(name="testcompany2")
        self.user = get_user_model().objects.create_user(
            "test@crownkiraappdev.com",
            "password123",
            is_staff=True,
            company=self.company,
        )
        self.user2 = get_user_model().objects.create_user(
            "test2@crownkiraappdev.com",
            "password123",
            is_staff=True,
            company=self.company2,
        )
        self.supplier = Supplier.objects.create(
            company=self.company, name="testsupplier"
        )
        self.supplier2 = Supplier.objects.create(
            company=self.company2, name="testsupplier2"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retreive_receive(self):
        """Test retreiving receive"""
        purchase_order = create_purchase_order(
            **{"supplier": self.supplier, "company": self.company}
        )
        purchase_order2 = create_purchase_order(
            **{"supplier": self.supplier, "company": self.company}
        )
        create_receive(
            **{
                "supplier": self.supplier,
                "purchase_order": purchase_order,
                "company": self.company,
            }
        )
        create_receive(
            **{
                "supplier": self.supplier,
                "purchase_order": purchase_order2,
                "company": self.company,
            }
        )
        other_company_purchase_order = create_purchase_order(
            **{"supplier": self.supplier2, "company": self.company2}
        )
        create_receive(
            **{
                "supplier": self.supplier2,
                "purchase_order": other_company_purchase_order,
                "company": self.company2,
            }
        )

        res = self.client.get(RECEIVE_URL)

        receives = (
            Receive.objects.all().filter(company=self.company).order_by("-id")
        )
        serializer = ReceiveSerializer(receives, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get("results", None), serializer.data)
        self.assertEqual(len(res.data.get("results", [])), 2)

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
