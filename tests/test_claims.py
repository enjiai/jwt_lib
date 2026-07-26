"""Unit tests for JWTClaims.from_payload() — Wave B.2."""

from enjilib_jwt import JWTClaims


def test_from_payload_maps_all_fields():
    """Test that from_payload correctly maps all fields, including sub→email."""
    payload = {
        "sub": "a@b.c",
        "user_id": 12,
        "roles": ["admin"],
        "permissions": ["x"],
        "disallows": ["y"],
        "employee_id": 34,
        "exp": 1,
        "type": "access",
    }
    claims = JWTClaims.from_payload(payload)
    assert claims.email == "a@b.c"
    assert claims.user_id == 12
    assert claims.roles == ["admin"]
    assert claims.permissions == ["x"]
    assert claims.disallows == ["y"]
    assert claims.employee_id == 34


def test_from_payload_defaults_empty_lists():
    """Test that missing optional lists default to []."""
    payload = {
        "sub": "test@example.com",
        "user_id": 42,
    }
    claims = JWTClaims.from_payload(payload)
    assert claims.email == "test@example.com"
    assert claims.user_id == 42
    assert claims.roles == []
    assert claims.permissions == []
    assert claims.disallows == []


def test_from_payload_employee_id_optional():
    """Test that missing employee_id yields None."""
    payload = {
        "sub": "user@company.org",
        "user_id": 99,
        "roles": ["user"],
    }
    claims = JWTClaims.from_payload(payload)
    assert claims.employee_id is None


def test_from_payload_ignores_unknown_keys():
    """Test that unknown keys do not break construction or appear as attributes."""
    payload = {
        "sub": "alice@example.com",
        "user_id": 5,
        "unknown_field": "should be ignored",
        "another_random_key": 12345,
        "rand_str": "abc123",
    }
    claims = JWTClaims.from_payload(payload)
    assert claims.email == "alice@example.com"
    assert claims.user_id == 5
    assert not hasattr(claims, "unknown_field")
    assert not hasattr(claims, "another_random_key")
    assert not hasattr(claims, "rand_str")


def test_from_payload_missing_user_id_and_sub():
    """Test that missing user_id and sub yield None (pins current permissive behavior)."""
    payload = {}
    claims = JWTClaims.from_payload(payload)
    # Current behavior: .get() returns None if key missing
    assert claims.user_id is None
    assert claims.email is None
    assert claims.roles == []
    assert claims.permissions == []
    assert claims.disallows == []
    assert claims.employee_id is None
