from core.models import Role, Company, Invoice

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from company.serializers import RoleSerializer


ROLE_URL = reverse("company:role-list")


class PublicRoleApiTest(TestCase):
    """Test the publicly available Role API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retreiving invoices"""
        res = self.client.get(ROLE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRoleApiTest(TestCase):
    """Test authorized user Role API"""

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

    def test_retreive_role(self):
        """Test retreiving role"""
        Role.objects.create(
            name="invoices",
            company=self.company,
        )
        Role.objects.create(
            name="departments",
            company=self.company,
        )
        Role.objects.create(
            name="departments",
            company=self.company2,
        )
        # tests to see how permissions are added for tests
        # invoice = Permission.objects.filter(pk__gte=29)
        # print(invoice)
        # add_invoice = Permission.objects.get(codename="add_invoice")
        # print(add_invoice)
        # testrole.permissions.add(add_invoice)

        res = self.client.get(ROLE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data.get("results", [])), 2)

    def test_role_permissions(self):
        """Test permissions provided from role"""
        # way to add permissions
        # https://docs.djangoproject.com/en/dev/topics/auth/default/#permissions-and-authorization
