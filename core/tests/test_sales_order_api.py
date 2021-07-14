from core.models import SalesOrder, Customer, Company

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from customer.serializers import SalesOrderSerializer

SALESORDER_URL = reverse("customer:salesorder-list")


class PublicSalesOrderApiTest(TestCase):
    """Test the publicly available salesorder API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retreiving invoices"""
        res = self.client.get(SALESORDER_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateSalesOrderApiTest(TestCase):
    """Test authorized user SalesOrder API"""

    def setUp(self):
        self.company = Company.objects.create(name="testcompany")
        self.customer = Customer.objects.create(
            company=self.company,
            name="testcustomer",
        )
        self.user = get_user_model().objects.create_user(
            "test@crownkiraappdev.com",
            "password123",
            is_staff=True,
            company=self.company,
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    # TODO: rewrite
    # def test_retreive_salesorder(self):
    #     """Test retreiving salesorder"""
    #     customer = Customer.objects.create(
    #         company=self.company,
    #         name="testcustomer",
    #     )
    #     customer2 = Customer.objects.create(
    #         company=self.company,
    #         name="testcustomer2",
    #     )
    #     SalesOrder.objects.create(
    #         company=self.company,
    #         customer=customer,
    #         salesperson=self.user,
    #         date="2001-01-10",
    #         # payment_date="2001-01-10",
    #         gst_rate="0.07",
    #         discount_rate="0",
    #         gst_amount="0",
    #         discount_amount="0",
    #         net="0",
    #         total_amount="0",
    #         grand_total="0",
    #         status="CP",
    #     )
    #     SalesOrder.objects.create(
    #         company=self.company,
    #         customer=customer2,
    #         salesperson=self.user,
    #         date="2001-01-10",
    #         # payment_date="2001-01-10",
    #         gst_rate="0.07",
    #         discount_rate="0",
    #         gst_amount="0",
    #         discount_amount="0",
    #         net="0",
    #         total_amount="0",
    #         grand_total="0",
    #         status="CP",
    #     )
    #     res = self.client.get(SALESORDER_URL)

    #     receives = SalesOrder.objects.all().order_by("-id")
    #     serializer = SalesOrderSerializer(receives, many=True)
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.assertEqual(res.data.get("results", None), serializer.data)

    # Deprecated
    # def test_salesorder_not_limited_to_user(self):
    #     """Test that salesorder returned are visible by every user"""
    #     testuser = get_user_model().objects.create_user(
    #         "testsales@crownkiraappdev.com" "password1234"
    #     )
    #     testcompany = Company.objects.create(name="testcompany")
    #     customer = Customer.objects.create(
    #         company=testcompany,
    #         name="testcustomer",
    #     )
    #     customer2 = Customer.objects.create(
    #         company=testcompany,
    #         name="testcustomer2",
    #     )
    #     SalesOrder.objects.create(
    #         customer=customer,
    #         salesperson=self.user,
    #         company=testcompany,
    #         date="2001-01-10",
    #         payment_date="2001-01-10",
    #         gst_rate="0.07",
    #         discount_rate="0",
    #         gst_amount="0",
    #         discount_amount="0",
    #         net="0",
    #         total_amount="0",
    #         grand_total="0",
    #     )
    #     SalesOrder.objects.create(
    #         customer=customer2,
    #         salesperson=self.user,
    #         company=testcompany,
    #         date="2001-01-10",
    #         payment_date="2001-01-10",
    #         gst_rate="0.07",
    #         discount_rate="0",
    #         gst_amount="0",
    #         discount_amount="0",
    #         net="0",
    #         total_amount="0",
    #         grand_total="0",
    #     )
    #     res = self.client.get(SALESORDER_URL)

    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.assertEqual(len(res.data), 2)

    #     self.user = testuser
    #     self.client.force_authenticate(self.user)

    #     res = self.client.get(SALESORDER_URL)

    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.assertEqual(len(res.data), 2)

    # TODO: rewrite
    # def test_create_salesorder_successful(self):
    #     """Test creating a new salesorder"""
    #     payload = {
    #         "testcustomer": self.customer,
    #         "salesperson": self.user,
    #         "company": self.company,
    #         "date": "2001-01-10",
    #         "payment_date": "2001-01-10",
    #         "gst_rate": "0.07",
    #         "discount_rate": "0",
    #         "gst_amount": "0",
    #         "discount_amount": "0",
    #         "net": "0",
    #         "total_amount": "0",
    #         "grand_total": "0",
    #         "status": "CP",
    #     }
    #     self.client.post(SALESORDER_URL, payload)
    #     exists = SalesOrder.objects.filter(customer=payload["testcustomer"])
    #     self.assertTrue(exists)

    # def test_create_salesorder_invalid(self):
    #     """Test creating a new supplier with invalid payload"""
    #     payload = {
    #         "testcustomer": "",
    #         "salesperson": self.user,
    #         "date": "2001-01-10",
    #         "payment_date": "2001-01-10",
    #         "gst_rate": "0.07",
    #         "discount_rate": "0",
    #         "gst_amount": "0",
    #         "discount_amount": "0",
    #         "net": "0",
    #         "total_amount": "0",
    #         "grand_total": "0",
    #         "status": "CP",
    #     }
    #     res = self.client.post(SALESORDER_URL, payload)
    #     self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
