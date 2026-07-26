"""Pytest configuration and shared fixtures for enjilib-jwt-auth tests."""

import pytest

from enjilib_jwt import JWTAuthenticator
from tests.helpers.token_factory import encrypt_payload, make_access_token

TEST_SECRET = "test-secret-key-do-not-use"


@pytest.fixture
def jwt_secret() -> str:
    """Provide the test JWT secret."""
    return TEST_SECRET


@pytest.fixture
def authenticator(jwt_secret: str) -> JWTAuthenticator:
    """Provide a JWTAuthenticator instance for testing."""
    return JWTAuthenticator(secret_key=jwt_secret)


@pytest.fixture
def mint_token(jwt_secret: str):
    """Provide a helper function to mint tokens for testing."""
    def _mint(**kwargs):
        return make_access_token(jwt_secret, **kwargs)
    return _mint
