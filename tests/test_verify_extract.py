"""Tests for JWTAuthenticator.verify_and_extract - highest-value security tests."""

from datetime import timedelta

import jwt
import pytest

from enjilib_jwt import JWTAuthenticator
from tests.helpers.token_factory import encrypt_payload, make_access_token


class TestVerifyAndExtract:
    """Test suite for JWTAuthenticator.verify_and_extract method."""

    # AC-2: Valid token returns JWTClaims with expected fields
    def test_verify_valid_token_returns_claims(self, authenticator, mint_token):
        """Happy path: valid token with all fields returns JWTClaims."""
        token = mint_token(
            sub="user@example.com",
            user_id=5,
            roles=["admin"],
            permissions=["ff:access-copilot"],
            disallows=["danger:do-not"],
            employee_id=9,
        )
        claims = authenticator.verify_and_extract(token)

        assert claims is not None
        assert claims.email == "user@example.com"
        assert claims.user_id == 5
        assert claims.roles == ["admin"]
        assert claims.permissions == ["ff:access-copilot"]
        assert claims.disallows == ["danger:do-not"]
        assert claims.employee_id == 9

    # AC-2 continued: verify multiple roles/permissions
    def test_verify_valid_token_with_multiple_roles_and_permissions(
        self, authenticator, mint_token
    ):
        """Valid token with multiple roles and permissions."""
        token = mint_token(
            sub="alice@example.com",
            user_id=42,
            roles=["admin", "moderator", "viewer"],
            permissions=[
                "ff:access-copilot",
                "ff:access-research",
                "/enji-db:(read|write)-.*",
            ],
            disallows=["/admin:delete-.*"],
            employee_id=123,
        )
        claims = authenticator.verify_and_extract(token)

        assert claims is not None
        assert claims.email == "alice@example.com"
        assert claims.user_id == 42
        assert claims.roles == ["admin", "moderator", "viewer"]
        assert claims.permissions == [
            "ff:access-copilot",
            "ff:access-research",
            "/enji-db:(read|write)-.*",
        ]
        assert claims.disallows == ["/admin:delete-.*"]
        assert claims.employee_id == 123

    # AC-3: Expired token returns None
    def test_verify_expired_token_returns_none(self, authenticator, mint_token):
        """Expired token (negative exp_delta) returns None."""
        token = mint_token(
            sub="user@example.com",
            user_id=1,
            exp_delta=timedelta(seconds=-10),
        )
        claims = authenticator.verify_and_extract(token)

        assert claims is None

    # AC-4: Malformed token string returns None
    def test_verify_malformed_token_not_a_jwt_returns_none(self, authenticator):
        """Malformed token ('not-a-jwt') returns None."""
        claims = authenticator.verify_and_extract("not-a-jwt")
        assert claims is None

    def test_verify_malformed_token_empty_string_returns_none(self, authenticator):
        """Empty token string returns None."""
        claims = authenticator.verify_and_extract("")
        assert claims is None

    def test_verify_malformed_token_garbage_returns_none(self, authenticator):
        """Garbage token string returns None."""
        claims = authenticator.verify_and_extract("garbage.string.with.dots")
        assert claims is None

    # AC-5: Missing 'enc' claim returns None
    def test_verify_missing_enc_returns_none(self, jwt_secret):
        """Token without 'enc' claim returns None."""
        # Manually craft a token without the 'enc' claim
        payload = {
            "exp": 9999999999,  # far future
            "type": "access",
            "sub": "user@example.com",
            "user_id": 1,
        }
        token = jwt.encode(payload, jwt_secret, algorithm="HS256")

        authenticator = JWTAuthenticator(secret_key=jwt_secret)
        claims = authenticator.verify_and_extract(token)

        assert claims is None

    # AC-6: Wrong secret authenticator returns None
    def test_verify_wrong_secret_returns_none(self, jwt_secret, mint_token):
        """Token minted with secret A, verified with secret B → None."""
        token = mint_token(
            sub="user@example.com",
            user_id=5,
            roles=["admin"],
        )

        # Create authenticator with different secret
        wrong_secret = "different-secret-key"
        wrong_authenticator = JWTAuthenticator(secret_key=wrong_secret)

        claims = wrong_authenticator.verify_and_extract(token)
        assert claims is None

    # AC-7: Tampered signature returns None
    def test_verify_tampered_signature_returns_none(self, authenticator, mint_token):
        """Token with flipped signature bytes returns None."""
        token = mint_token(
            sub="user@example.com",
            user_id=5,
        )

        # Tamper with the signature (last part after last dot)
        parts = token.split(".")
        if len(parts) == 3:
            # Flip some characters in the signature
            tampered_sig = parts[2]
            if len(tampered_sig) > 0:
                # Flip first character by rotating it in the base64url alphabet
                tampered_sig = (
                    chr((ord(tampered_sig[0]) + 1) % 256) + tampered_sig[1:]
                )
            tampered_token = f"{parts[0]}.{parts[1]}.{tampered_sig}"

            claims = authenticator.verify_and_extract(tampered_token)
            assert claims is None

    # AC-7: Bad/garbage 'enc' value returns None
    def test_verify_bad_enc_returns_none(self, jwt_secret):
        """Valid JWT with garbage 'enc' claim (decrypt fails) → None."""
        # Create a valid JWT structure but with garbage in the 'enc' field
        payload = {
            "exp": 9999999999,
            "type": "access",
            "enc": "not-base64-garbage-!!!",  # Invalid enc value
        }
        token = jwt.encode(payload, jwt_secret, algorithm="HS256")

        authenticator = JWTAuthenticator(secret_key=jwt_secret)
        claims = authenticator.verify_and_extract(token)

        # Should return None because decrypt fails
        assert claims is None

    # Recommended: Algorithm mismatch
    def test_verify_algorithm_mismatch_returns_none(self, jwt_secret):
        """Token signed with HS512, verified with HS256 → None."""
        # Create token with HS512
        payload = {
            "exp": 9999999999,
            "type": "access",
            "sub": "user@example.com",
            "user_id": 1,
        }
        token = jwt.encode(payload, jwt_secret, algorithm="HS512")

        # Try to verify with HS256 authenticator
        authenticator = JWTAuthenticator(secret_key=jwt_secret, algorithm="HS256")
        claims = authenticator.verify_and_extract(token)

        assert claims is None
