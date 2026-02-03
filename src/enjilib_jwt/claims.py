"""JWT claims data class."""

from dataclasses import dataclass


@dataclass
class JWTClaims:
    """JWT Claims extracted from token issued by enji-auth."""

    user_id: int
    email: str
    roles: list[str]
    permissions: list[str]
    disallows: list[str] = None
    employee_id: int | None = None

    def __post_init__(self):
        """Set default values for optional fields."""
        if self.disallows is None:
            self.disallows = []

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
            disallows=payload.get("disallows", []),
            employee_id=payload.get("employee_id"),
        )
