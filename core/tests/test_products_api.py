from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from company.serializers import ProductSerializer
from core.models import Product, ProductCategory, Supplier, Company

PRODUCT_URL = reverse("company:product-list")


class PublicProductApiTest(TestCase):
    """Test the publicly available product API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retreiving products"""
        res = self.client.get(PRODUCT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateProductApiTest(TestCase):
    """Test authorized user product API"""

    def setUp(self):
        self.company = Company.objects.create(name="testcompany")
        self.user = get_user_model().objects.create_user(
            "test@crownkiraappdev.com",
            "password123",
            is_staff=True,
            company=self.company,
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retreive_product(self):
        """Test retreiving product"""
        testsupplier = Supplier.objects.create(
            company=self.company, name="testsupplier"
        )
        testproductcategory = ProductCategory.objects.create(
            company=self.company, name="testproductname"
        )
        Product.objects.create(
            category=testproductcategory,
            supplier=testsupplier,
            name="testproduct",
            unit="0",
            cost="0",
            unit_price="0",
        )
        Product.objects.create(
            category=testproductcategory,
            supplier=testsupplier,
            name="testproduct2",
            unit="0",
            cost="0",
            unit_price="0",
        )
        res = self.client.get(PRODUCT_URL)

        products = Product.objects.all().order_by("-id")
        serializer = ProductSerializer(products, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get("results", None), serializer.data)

    # Deprecated: since user can only view products owned by their company
    # def test_product_not_limited(self):
    #     """Test that product returned are visible by every user"""
    #     testuser = get_user_model().objects.create_user(
    #         "testsales@crownkiraappdev.com" "password1234"
    #     )
    #     testcompany = Company.objects.create(name="testcompany")
    #     testsupplier = Supplier.objects.create(
    #         company=testcompany, name='testsupplier'
    #     )
    #     testproductcategory = ProductCategory.objects.create(
    #         company=testcompany, name='testproductname'
    #     )
    #     Product.objects.create(
    #         category=testproductcategory,
    #         supplier=testsupplier,
    #         name='testproduct',
    #         unit='0',
    #         cost='0',
    #         unit_price='0',
    #     )
    #     Product.objects.create(
    #         category=testproductcategory,
    #         supplier=testsupplier,
    #         name='testproduct2',
    #         unit='0',
    #         cost='0',
    #         unit_price='0',
    #     )
    #     res = self.client.get(PRODUCT_URL)

    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.assertEqual(len(res.data), 2)

    #     self.user = testuser
    #     self.client.force_authenticate(self.user)

    #     res = self.client.get(PRODUCT_URL)

    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.assertEqual(len(res.data), 2)
