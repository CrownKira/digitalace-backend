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
        self.user = get_user_model().objects.create_user(
            "test@crownkiraappdev.com",
            "password123",
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retreive_invoice(self):
        """Test retreiving invoice"""
        testuser = get_user_model().objects.create_user(
            "testsales@crownkiraappdev.com" "password1234"
        )
        testcompany2 = Company.objects.create(name="testcompany2")
        testcompany = Company.objects.create(name="testcompany")
        testcustomer = Customer.objects.create(
            company=testcompany, name="testname"
        )
        testsalesorder = SalesOrder.objects.create(
            salesperson=testuser,
            customer=testcustomer,
            company=testcompany,
            date="2001-01-10",
            payment_date="2001-01-10",
            gst_rate="0.07",
            discount_rate="0",
            gst_amount="0",
            discount_amount="0",
            net="0",
            total_amount="0",
            grand_total="0",
        )
        testsalesorder2 = SalesOrder.objects.create(
            salesperson=testuser,
            customer=testcustomer,
            company=testcompany,
            date="2001-01-10",
            payment_date="2001-01-10",
            gst_rate="0.07",
            discount_rate="0",
            gst_amount="0",
            discount_amount="0",
            net="0",
            total_amount="0",
            grand_total="0",
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
            customer=testcustomer,
            sales_order=testsalesorder,
            salesperson=testuser,
            company=testcompany,
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
            customer=testcustomer,
            sales_order=testsalesorder2,
            salesperson=testuser,
            company=testcompany2,
        )

        res = self.client.get(INVOICE_URL)

        invoices = Invoice.objects.all().order_by("id")
        serializer = InvoiceSerializer(invoices, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_invoice_not_limited_to_user(self):
        """Test that invoices returned are visible by every user"""
        testuser = get_user_model().objects.create_user(
            "testsales@crownkiraappdev.com" "password1234"
        )
        testcompany = Company.objects.create(name="testcompany")
        testcustomer = Customer.objects.create(
            company=testcompany, name="testname"
        )
        testsalesorder = SalesOrder.objects.create(
            salesperson=testuser,
            customer=testcustomer,
            company=testcompany,
            date="2001-01-10",
            payment_date="2001-01-10",
            gst_rate="0.07",
            discount_rate="0",
            gst_amount="0",
            discount_amount="0",
            net="0",
            total_amount="0",
            grand_total="0",
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
            customer=testcustomer,
            sales_order=testsalesorder,
            salesperson=testuser,
            company=testcompany,
        )
        testuser2 = self.user
        testcompany = Company.objects.create(name="testcompany")
        testcustomer = Customer.objects.create(
            company=testcompany, name="testname"
        )
        testsalesorder = SalesOrder.objects.create(
            salesperson=testuser2,
            customer=testcustomer,
            company=testcompany,
            date="2001-01-11",
            payment_date="2001-01-11",
            gst_rate="0.07",
            discount_rate="0",
            gst_amount="0",
            discount_amount="0",
            net="0",
            total_amount="0",
            grand_total="0",
        )
        Invoice.objects.create(
            date="2001-01-11",
            payment_date="2001-01-11",
            gst_rate="0.07",
            discount_rate="0",
            gst_amount="0",
            discount_amount="0",
            net="0",
            total_amount="0",
            grand_total="0",
            customer=testcustomer,
            sales_order=testsalesorder,
            salesperson=testuser2,
            company=testcompany,
        )

        res = self.client.get(INVOICE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

        self.user = testuser
        self.client.force_authenticate(self.user)

        res = self.client.get(INVOICE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_create_invoice_successful(self):
        """Test creating a new invoice"""
        self.Company = Company.objects.create(name="testcompany")
        self.Customer = Customer.objects.create(
            company=self.Company, name="testname"
        )
        self.SalesOrder = SalesOrder.objects.create(
            salesperson=self.user,
            customer=self.Customer,
            company=self.Company,
            date="2001-01-10",
            payment_date="2001-01-10",
            gst_rate="0.07",
            discount_rate="0",
            gst_amount="0",
            discount_amount="0",
            net="0",
            total_amount="0",
            grand_total="0",
        )
        payload = {
            "salesperson": self.user.id,
            "customer": self.Customer.id,
            "sales_order": self.SalesOrder.id,
            "company": self.Company.id,
            "date": "2001-01-10",
            "payment_date": "2001-01-10",
            "gst_rate": "0.07",
            "discount_rate": "0",
            "gst_amount": "0",
            "discount_amount": "0",
            "net": "0",
            "total_amount": "0",
            "grand_total": "0",
        }
        self.client.post(INVOICE_URL, payload)
        exists = Invoice.objects.filter(customer=payload["customer"])
        self.assertTrue(exists)

    def test_create_invoice_invalid(self):
        """Test creating a new invoice with invalid payload"""
        testcompany = Company.objects.create(name="testcompany")
        testcustomer = Customer.objects.create(
            company=testcompany, name="testname"
        )
        payload = {
            "salesperson": "",
            "customer": testcustomer,
            "company": testcompany,
            "date": "2001-01-10",
            "payment_date": "2001-01-10",
            "gst_rate": "0.07",
            "discount_rate": "0",
            "gst_amount": "0",
            "discount_amount": "0",
            "net": "0",
            "total_amount": "0",
            "grand_total": "0",
        }
        res = self.client.post(INVOICE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
