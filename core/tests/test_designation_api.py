from core.models import Designation, Company, Department

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from company.serializers import DesignationSerializer


DESIGNATION_URL = reverse("company:designation-list")


class PublicDesignationApiTest(TestCase):
    """Test the publicly available Designation API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retreiving invoices"""
        res = self.client.get(DESIGNATION_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateDesingationApiTest(TestCase):
    """Test authorized user desingation API"""

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
        self.department = Department.objects.create(
            name="HR", company=self.company
        )
        self.department2 = Department.objects.create(
            name="HR", company=self.company2
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retreive_departmemt(self):
        """Test retreiving designation"""
        Designation.objects.create(
            name="salesperson", department=self.department
        )
        Designation.objects.create(
            name="salesrepresentative", department=self.department
        )
        Designation.objects.create(
            name="salesrepresentative", department=self.department2
        )
        res = self.client.get(DESIGNATION_URL)

        invoices = (
            Designation.objects.all()
            .filter(department=self.department)
            .order_by("-id")
        )
        serializer = DesignationSerializer(invoices, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get("results", None), serializer.data)
        self.assertEqual(len(res.data.get("results", [])), 2)

    def test_create_designation_invalid(self):
        """Test creating designation with invalid payload"""
        payload = {
            "name": "",
            "department":self.department
        }
        res = self.client.post(DESIGNATION_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
