import os

from api.settings.common import *

# TODO: fix F401, F403, F405

SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = False

# SECURITY WARNING: update this when you have the production host
ALLOWED_HOSTS = ["api"]

# HTTPS settings
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
# TODO: Configuring HTTPS for your Elastic Beanstalk environment
# SECURE_SSL_REDIRECT = True

# HSTS settings
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
