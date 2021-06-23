from core.models import Department, Company

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from company.serializers import DepartmentSerializer


DEPARTMENT_URL = reverse("company:department-list")


class PublicDepartmentApiTest(TestCase):
    """Test the publicly available department API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retreiving invoices"""
        res = self.client.get(DEPARTMENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateDepartmentApiTest(TestCase):
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
            company=self.company2,
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retreive_department(self):
        """Test retreiving department"""
        Department.objects.create(name="Human resources", company=self.company)
        Department.objects.create(name="Acounting", company=self.company)
        Department.objects.create(
            name="Human resources", company=self.company2
        )

        res = self.client.get(DEPARTMENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data.get("results", [])), 2)

    def test_create_department(self):
        """Test creating department"""
        payload = {
            "name": "Human Resource",
            "company": self.company,
            "designation_set": [],
        }
        res = self.client.post(DEPARTMENT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        exists = Department.objects.all().filter(company=self.company).exists()
        self.assertTrue(exists)

    def test_create_department_invalid(self):
        """Test creating department with invalid payload"""
        payload = {
            "name": "",
            "company": self.company,
            "designation_set": [],
        }
        res = self.client.post(DEPARTMENT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
