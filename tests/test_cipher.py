"""Unit tests for enjilib_jwt.cipher payload decryption."""

import base64
import json
import zlib

import pytest
from cryptography.exceptions import InvalidTag

from enjilib_jwt.cipher import decrypt_payload
from tests.helpers.token_factory import encrypt_payload


class TestDecryptRoundtrip:
    """Tests for successful encrypt/decrypt round-trips."""

    def test_decrypt_roundtrip_sensitive_claims(self, jwt_secret):
        """
        AC-2: Round-trip test for a realistic sensitive claims dict.
        Encrypt a dict with typical sensitive claims, decrypt, and verify equality.
        """
        payload = {
            "sub": "user@example.com",
            "user_id": 7,
            "roles": ["admin", "viewer"],
            "permissions": ["ff:access-copilot", "enji-db:read-user"],
            "disallows": [],
            "employee_id": 99,
        }
        token = encrypt_payload(payload, jwt_secret)
        result = decrypt_payload(token, jwt_secret)
        assert result == payload

    def test_decrypt_roundtrip_unicode_and_nested(self, jwt_secret):
        """
        AC-2: Non-ASCII and nested structures survive round-trip.
        Verify that unicode characters and nested lists/dicts are preserved.
        """
        payload = {
            "sub": "josé@例え.jp",
            "email": "тест@тест.рф",
            "user_id": 123,
            "roles": ["admin", "用户"],
            "metadata": {
                "nested_list": ["item1", "åäö", "🎉"],
                "nested_dict": {"key1": "value1", "ключ": "значение"},
            },
            "permissions": [],
            "disallows": ["ff:restricted"],
            "employee_id": None,
        }
        token = encrypt_payload(payload, jwt_secret)
        result = decrypt_payload(token, jwt_secret)
        assert result == payload


class TestDecryptErrorHandling:
    """Tests for error conditions and exception handling."""

    def test_decrypt_wrong_secret_raises(self, jwt_secret):
        """
        AC-3: Wrong secret raises cryptography exception.
        Encrypt with one secret, decrypt with another → expect InvalidTag or similar.
        """
        payload = {"sub": "user@example.com", "user_id": 42}
        token = encrypt_payload(payload, jwt_secret)

        wrong_secret = "different-secret-key"
        with pytest.raises((InvalidTag, Exception)):
            decrypt_payload(token, wrong_secret)

    def test_decrypt_truncated_raises(self, jwt_secret):
        """
        AC-4: Malformed input raises exception.
        Test with empty string, non-base64, and too-short blob.
        """
        # Empty string
        with pytest.raises(Exception):
            decrypt_payload("", jwt_secret)

        # Not base64
        with pytest.raises(Exception):
            decrypt_payload("!!!not-base64!!!", jwt_secret)

        # Valid base64 but too short (less than 12 bytes after decode)
        short_token = base64.urlsafe_b64encode(b"short").decode()
        with pytest.raises(Exception):
            decrypt_payload(short_token, jwt_secret)

    def test_decrypt_tampered_ciphertext_raises(self, jwt_secret):
        """
        AC-5: Tampered ciphertext raises exception.
        Flip a bit in the ciphertext portion and verify decryption fails.
        """
        payload = {"sub": "user@example.com", "user_id": 99}
        token = encrypt_payload(payload, jwt_secret)

        # Decode the token, flip a bit in the ciphertext (after the 12-byte nonce)
        raw = base64.urlsafe_b64decode(token)
        nonce = raw[:12]
        ciphertext = raw[12:]

        # Flip the first bit of the ciphertext
        tampered_ciphertext = bytes([ciphertext[0] ^ 1]) + ciphertext[1:]
        tampered_raw = nonce + tampered_ciphertext
        tampered_token = base64.urlsafe_b64encode(tampered_raw).decode()

        # Verify that decryption with tampered data raises an exception
        with pytest.raises((InvalidTag, Exception)):
            decrypt_payload(tampered_token, jwt_secret)
