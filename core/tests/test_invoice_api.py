from core.models import Company, Customer, Invoice, SalesOrder

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from customer.serializers import InvoiceSerializer


INVOICE_URL = reverse("customer:invoice-list")


def create_sales_order(**params):
    return SalesOrder.objects.create(
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
        **params
        # salesperson=user,
        # customer=customer,
        # company=self.company,
    )


def create_invoice(**params):
    return Invoice.objects.create(
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
        # customer=customer,
        # sales_order=salesorder,
        # salesperson=user,
        # company=self.company,
    )


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
        self.company2 = Company.objects.create(name="testcompany2")
        self.customer = Customer.objects.create(
            company=self.company, name="testcompany"
        )
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
        self.customer = Customer.objects.create(
            company=self.company,
            name="testcustomer",
        )
        self.customer2 = Customer.objects.create(
            company=self.company2,
            name="testcustomer",
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retreive_invoice(self):
        """Test retreiving invoice"""
        salesorder = create_sales_order(
            **{
                "salesperson": self.user,
                "customer": self.customer,
                "company": self.company,
            }
        )
        salesorder2 = create_sales_order(
            **{
                "salesperson": self.user,
                "customer": self.customer,
                "company": self.company,
            }
        )

        create_invoice(
            **{
                "customer": self.customer,
                "sales_order": salesorder,
                "salesperson": self.user,
                "company": self.company,
            }
        )

        create_invoice(
            **{
                "customer": self.customer,
                "sales_order": salesorder2,
                "salesperson": self.user,
                "company": self.company,
            }
        )

        other_company_sales_order = create_sales_order(
            **{
                "salesperson": self.user2,
                "customer": self.customer2,
                "company": self.company2,
            }
        )

        create_invoice(
            **{
                "customer": self.customer2,
                "sales_order": other_company_sales_order,
                "salesperson": self.user2,
                "company": self.company2,
            }
        )

        res = self.client.get(INVOICE_URL)

        invoices = (
            Invoice.objects.all().filter(company=self.company).order_by("-id")
        )
        serializer = InvoiceSerializer(invoices, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get("results", None), serializer.data)
        self.assertEqual(len(res.data.get("results", [])), 2)

    def test_create_invoice_successful(self):
        """Test creating a new invoice"""
        sales_order = create_sales_order(
            **{
                "salesperson": self.user,
                "customer": self.customer,
                "company": self.company,
            }
        )
        payload = {
            "salesperson": self.user,
            "customer": self.customer.id,
            "sales_order": sales_order.id,
            "company": self.company,
            "date": "2001-01-10",
            "payment_date": "2001-01-11",
            "gst_rate": "0.07",
            "discount_rate": "0",
            "gst_amount": "0",
            "discount_amount": "0",
            "net": "0",
            "total_amount": "0",
            "grand_total": "0",
            "status": "PD",
        }
        self.client.post(INVOICE_URL, payload)
        exists = Invoice.objects.all().filter(company=self.company).exists()
        self.assertTrue(exists)

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
