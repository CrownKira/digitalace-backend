from core.models import Department, Company

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from company.serializers import DepartmentSerializer


DEPARTMENT_URL = reverse("company:department-list")


def create_department(**params):
    return Department.objects.create(**params)


class PublicDepartmentApiTest(TestCase):
    """Test the publicly available department API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retreiving invoices"""
        res = self.client.get(DEPARTMENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateDepartmentTest(TestCase):
    """Test authorized user department API"""

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

    def test_retreive_department(self):
        """Test retreiving department"""
        create_department(
            **{"name": "human resources", "company": self.company}
        )
        create_department(
            **{"name": "acounting department", "company": self.company}
        )
        create_department(
            **{"name": "acounting department", "company": self.company2}
        )

        res = self.client.get(DEPARTMENT_URL)
        departments = (
            Department.objects.all()
            .filter(company=self.company)
            .order_by("-id")
        )
        serializer = DepartmentSerializer(departments, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data.get("results", None)), 2)
        self.assertEqual(res.data.get("results", None), serializer.data)
