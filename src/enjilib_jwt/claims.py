"""JWT claims data class."""

from dataclasses import dataclass, field


@dataclass
class JWTClaims:
    """JWT Claims extracted from token issued by enji-auth."""

    user_id: int
    email: str
    roles: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    disallows: list[str] = field(default_factory=list)
    employee_id: int | None = None

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
