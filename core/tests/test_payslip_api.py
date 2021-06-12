from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Payslip, Company
from company.serializers import PayslipSerializer

PAYSLIP_URL = reverse("company:payslip-list")


def create_payslip(**params):
    return Payslip.objects.create(
        date='2001-01-10',
        year='2001',
        month='september',
        basic_salary='1000',
        total_allowances='300',
        total_deductions='0',
        sale_price='100',
        commission='200',
        commission_amt='100',
        net_pay='1100',
        payment_method='cash',
        bank='UOB',
        status='paid',
        comment='CP',
        **params,
    )


class PublicPayslipTest(TestCase):
    """Test publicly available payslip API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retreiving products"""
        res = self.client.get(PAYSLIP_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivatePaysliptest(TestCase):
    """Test authorized user payslip API"""

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
            company=self.company,
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retreive_payslip(self):
        """Test retreiving payslip from company"""
        create_payslip(**{
            'user': self.user,
            'company': self.company,
        })
        create_payslip(**{
            'user': self.user,
            'company': self.company,
        })
        create_payslip(**{
            'user': self.user2,
            'company': self.company2,
        })

        res = self.client.get(PAYSLIP_URL)

        payslips = Payslip.objects.all().filter(company=self.company).order_by('-id')
        serializer = PayslipSerializer(payslips, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data.get('results', None)), 2)
        self.assertEqual(res.data.get('results', None), serializer.data)
