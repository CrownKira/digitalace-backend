import os

from api.settings.common import *

with open(os.path.join(BASE_DIR, "secret_key.txt")) as f:
    SECRET_KEY = f.read().strip()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost", "api"]
