from rest_framework.test import APIClient
import pytest


@pytest.fixture
def api_client():
    return APIClient()


# Define a global fixture for authenticating users
@pytest.fixture
def authenticate_user(api_client):
    def do_authenticate_user(user):
        return api_client.force_authenticate(user)

    return do_authenticate_user
