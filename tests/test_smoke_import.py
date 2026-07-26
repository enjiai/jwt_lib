"""Smoke test to verify package exports are available."""


def test_package_exports():
    """Verify that main package exports are importable."""
    from enjilib_jwt import JWTAuthenticator, JWTClaims

    assert JWTAuthenticator is not None
    assert JWTClaims is not None
