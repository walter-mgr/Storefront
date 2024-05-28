from django.contrib.auth.models import User
from rest_framework.test import APIClient
import pytest


@pytest.fixture
def api_client():
    return APIClient()


# Define a global fixture for authenticating users
@pytest.fixture
def authenticate_user(api_client):
    def do_authenticate_user(is_staff=False):
        return api_client.force_authenticate(user=User(is_staff=is_staff))

    return do_authenticate_user
