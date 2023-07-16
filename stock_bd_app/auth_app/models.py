from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator

# Create your models here.


class CustomUser(AbstractUser):
    # Add any additional fields you need
    username_validator = UnicodeUsernameValidator()
    pass

