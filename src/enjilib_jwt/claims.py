"""JWT claims data class."""
from dataclasses import dataclass


@dataclass
class JWTClaims:
    """JWT Claims extracted from token issued by enji-auth."""

    user_id: int
    email: str
    roles: list[str]
    permissions: list[str]

    @classmethod
    def from_payload(cls, payload: dict) -> "JWTClaims":
        """
        Create JWTClaims from JWT payload dict.

        Args:
            payload: Decoded JWT payload

        Returns:
            JWTClaims instance
        """
        return cls(
            user_id=payload.get("user_id"),
            email=payload.get("sub"),
            roles=payload.get("roles", []),
            permissions=payload.get("permissions", []),
        )
