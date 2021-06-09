from core.models import Company, Customer, Invoice, SalesOrder

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from customer.serializers import InvoiceSerializer


INVOICE_URL = reverse("customer:invoice-list")


class PublicInvoiceApiTest(TestCase):
    """Test the publicly available invoice API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retreiving invoices"""
        res = self.client.get(INVOICE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateInvoiceApiTest(TestCase):
    """Test authorized user invoice API"""

    def setUp(self):
        self.company = Company.objects.create(name="testcompany")
        self.customer = Customer.objects.create(
            company=self.company, name="testcompany"
        )
        self.user = get_user_model().objects.create_user(
            "test@crownkiraappdev.com",
            "password123",
            is_staff=True,
            company=self.company,
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retreive_invoice(self):
        """Test retreiving invoice"""
        user = get_user_model().objects.create_user(
            "testsales@crownkiraappdev.com" "password1234"
        )
        customer = Customer.objects.create(
            company=self.company, name="testcustomer"
        )
        salesorder = SalesOrder.objects.create(
            salesperson=user,
            customer=customer,
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
            status="CP",
        )
        salesorder2 = SalesOrder.objects.create(
            salesperson=user,
            customer=customer,
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
            status="CP",
        )
        Invoice.objects.create(
            date="2001-01-10",
            payment_date="2001-01-10",
            gst_rate="0.07",
            discount_rate="0",
            gst_amount="0",
            discount_amount="0",
            net="0",
            total_amount="0",
            grand_total="0",
            customer=customer,
            sales_order=salesorder,
            salesperson=user,
            status="PD",
            company=self.company,
        )
        Invoice.objects.create(
            date="2001-01-10",
            payment_date="2001-01-10",
            gst_rate="0.07",
            discount_rate="0",
            gst_amount="0",
            discount_amount="0",
            net="0",
            total_amount="1",
            grand_total="0",
            customer=customer,
            sales_order=salesorder2,
            salesperson=user,
            status="PD",
            company=self.company,
        )

        res = self.client.get(INVOICE_URL)

        invoices = Invoice.objects.all().order_by("-id")
        serializer = InvoiceSerializer(invoices, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get("results", None), serializer.data)

    # Deprecated
    # def test_invoice_not_limited_to_user(self):
    #     """Test that invoices returned are visible by every user"""
    #     user = get_user_model().objects.create_user(
    #         "testsales@crownkiraappdev.com", "password1234"
    #     )
    #     testcompany = Company.objects.create(name="testcompany")
    #     customer = Customer.objects.create(
    #         company=testcompany, name="testcompany"
    #     )
    #     salesorder = SalesOrder.objects.create(
    #         salesperson=user,
    #         customer=customer,
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
    #         status="CP",
    #     )
    #     Invoice.objects.create(
    #         date="2001-01-10",
    #         payment_date="2001-01-10",
    #         gst_rate="0.07",
    #         discount_rate="0",
    #         gst_amount="0",
    #         discount_amount="0",
    #         net="0",
    #         total_amount="0",
    #         grand_total="0",
    #         customer=customer,
    #         sales_order=salesorder,
    #         salesperson=user,
    #         company=testcompany,
    #         status="PD",
    #     )
    #     user2 = self.user
    #     testcompany = Company.objects.create(name="testcompany")
    #     customer = Customer.objects.create(
    #         company=testcompany, name="testcustomer"
    #     )
    #     salesorder = SalesOrder.objects.create(
    #         salesperson=user2,
    #         customer=customer,
    #         company=testcompany,
    #         date="2001-01-11",
    #         payment_date="2001-01-11",
    #         gst_rate="0.07",
    #         discount_rate="0",
    #         gst_amount="0",
    #         discount_amount="0",
    #         net="0",
    #         total_amount="0",
    #         grand_total="0",
    #     )
    #     Invoice.objects.create(
    #         date="2001-01-11",
    #         payment_date="2001-01-11",
    #         gst_rate="0.07",
    #         discount_rate="0",
    #         gst_amount="0",
    #         discount_amount="0",
    #         net="0",
    #         total_amount="0",
    #         grand_total="0",
    #         customer=customer,
    #         sales_order=salesorder,
    #         salesperson=user2,
    #         company=testcompany,
    #     )

    #     res = self.client.get(INVOICE_URL)

    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.assertEqual(len(res.data), 2)

    #     self.user = user
    #     self.client.force_authenticate(self.user)

    #     res = self.client.get(INVOICE_URL)

    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.assertEqual(len(res.data), 2)

    # TODO: rewrite
    # def test_create_invoice_successful(self):
    #     """Test creating a new invoice"""
    #     sales_order = SalesOrder.objects.create(
    #         salesperson=self.user,
    #         customer=self.customer,
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
    #         "salesperson": self.user,
    #         "testcustomer": self.customer,
    #         "sales_order": sales_order,
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
    #         "status": "PD",
    #     }
    #     self.client.post(INVOICE_URL, payload)
    #     exists = Invoice.objects.filter(customer=payload["testcustomer"])
    #     self.assertTrue(exists)

    # def test_create_invoice_invalid(self):
    #     """Test creating a new invoice with invalid payload"""
    #     payload = {
    #         "salesperson": "",
    #         "testcustomer": self.customer,
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
    #         "status": "PD",
    #     }
    #     res = self.client.post(INVOICE_URL, payload)

    #     self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
