from core.models.transaction import Invoice, SalesOrder
from core.models.maintenance import Customer
from core.models.user import Company
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from customer.serializers import InvoiceSerializer

INVOICE_URL = reverse('customer:invoice-list')


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
            'test@crownkiraappdev.com',
            'password123',
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retreive_invoice(self):
        """Test retreiving invoice"""
        testuser = get_user_model().objects.create_user(
            'testsales@crownkiraappdev.com'
            'password1234'
        )
        testcompany = Company.objects.create(name='testcompany')
        testcustomer = Customer.objects.create(company=testcompany, name='testname')
        testsalesorder = SalesOrder.objects.create(
            salesperson=testuser, customer=testcustomer, company=testcompany,
            date='2001-01-10', payment_date='2001-01-10', 
            gst_rate='0.07', discount_rate='0',
            gst_amount='0', discount_amount='0', 
            net='0', total_amount='0', grand_total='0'
            )
        Invoice.objects.create(
            date='2001-01-10', payment_date='2001-01-10', 
            gst_rate='0.07', discount_rate='0',
            gst_amount='0', discount_amount='0', 
            net='0', total_amount='0', grand_total='0',
            customer=testcustomer, sales_order=testsalesorder,
            salesperson=testuser, company=testcompany
        )

        res = self.client.get(INVOICE_URL)

        invoices = Invoice.objects.all().order_by('-id')
        serializer = InvoiceSerializer(invoices, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)