import os

from decouple import config

from api.settings.common import *


SECRET_KEY = config("SECRET_KEY")
if not SECRET_KEY:
    with open(os.path.join(BASE_DIR, "secret_key.txt")) as f:
        SECRET_KEY = f.read().strip()


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost", "api"]

AWS_STORAGE_BUCKET_NAME = "crownkira-digitalace-bucket"
AWS_S3_CUSTOM_DOMAIN = "%s.s3.amazonaws.com" % AWS_STORAGE_BUCKET_NAME
