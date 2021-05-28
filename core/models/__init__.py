# https://www.webforefront.com/django/modelsoutsidemodels.html
# #:~:text=By%20default%2C%20Django%20models%20are,dozens%20or%20hundreds%20of%20models.
from .maintenance import Customer, Supplier, ProductCategory, Product
from .transaction import Invoice, SalesOrder
from .user import Company, Department, Role, User, UserConfig
from .user import user_image_file_path, user_resume_file_path

# TODO: review this
# https://github.com/django/django/blob/main/django/conf/urls/__init__.py
__all__ = [
    "Customer",
    "Supplier",
    "ProductCategory",
    "Product",
    "Invoice",
    "SalesOrder",
    "Company",
    "Department",
    "Role",
    "User",
    "UserConfig",
    "user_image_file_path",
    "user_resume_file_path",
]
