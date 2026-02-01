"""JWT token authenticator."""
import re
from typing import Optional

import jwt

from .claims import JWTClaims


class JWTAuthenticator:
    """Universal JWT authenticator for backend services with regex pattern matching."""

    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        """
        Initialize JWT authenticator.

        Args:
            secret_key: Secret key used by enji-auth to sign tokens
            algorithm: JWT algorithm (default: HS256)
        """
        self.secret_key = secret_key
        self.algorithm = algorithm

    def verify_and_extract(self, token: str) -> Optional[JWTClaims]:
        """
        Verify JWT token signature and extract claims.

        Args:
            token: JWT token string

        Returns:
            JWTClaims if token is valid, None if invalid

        Example:
            authenticator = JWTAuthenticator("secret_key")
            claims = authenticator.verify_and_extract(token)
            if claims:
                print(f"User: {claims.email}")
                print(f"Roles: {claims.roles}")
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
            )
            return JWTClaims.from_payload(payload)
        except jwt.InvalidTokenError:
            return None
        except Exception:
            return None

    @staticmethod
    def _match_permission(permission: str, pattern: str) -> bool:
        """
        Match permission against regex pattern.

        Patterns can be:
        - Exact match: "ff:access-copilot"
        - Regex with /: "/auth-db:(read|update|create)-roles$"
        - Wildcard: "/.*" or "/prefix:.*"

        Args:
            permission: Permission string to check
            pattern: Pattern string (can be regex)

        Returns:
            True if permission matches pattern
        """
        # If pattern starts with /, it's a regex pattern
        if pattern.startswith("/"):
            try:
                regex_pattern = pattern[1:]  # Remove leading /
                return bool(re.match(regex_pattern, permission))
            except re.error:
                # Invalid regex, skip
                return False
        else:
            # Exact match
            return permission == pattern

    @staticmethod
    def _check_permission_list(
        permission: str, permission_list: list[str]
    ) -> bool:
        """
        Check if permission matches any pattern in permission list.

        Args:
            permission: Permission to check
            permission_list: List of patterns (regex or exact match)

        Returns:
            True if permission matches any pattern
        """
        for pattern in permission_list:
            if JWTAuthenticator._match_permission(permission, pattern):
                return True
        return False

    @staticmethod
    def has_role(claims: JWTClaims, role: str) -> bool:
        """
        Check if user has specific role.

        Args:
            claims: JWTClaims object
            role: Role name to check

        Returns:
            True if user has the role

        Example:
            if authenticator.has_role(claims, "admin"):
                # Grant admin access
        """
        return role in claims.roles

    @staticmethod
    def has_any_role(claims: JWTClaims, roles: list[str]) -> bool:
        """
        Check if user has any of the specified roles.

        Args:
            claims: JWTClaims object
            roles: List of role names to check

        Returns:
            True if user has any of the roles

        Example:
            if authenticator.has_any_role(claims, ["admin", "moderator"]):
                # Grant special access
        """
        return any(role in claims.roles for role in roles)

    @staticmethod
    def has_all_roles(claims: JWTClaims, roles: list[str]) -> bool:
        """
        Check if user has all of the specified roles.

        Args:
            claims: JWTClaims object
            roles: List of role names to check

        Returns:
            True if user has all of the roles
        """
        return all(role in claims.roles for role in roles)

    @staticmethod
    def has_permission(claims: JWTClaims, permission: str) -> bool:
        """
        Check if user has specific permission using regex pattern matching.

        Permissions in JWT can be regex patterns:
        - Exact match: "ff:access-copilot"
        - Regex pattern: "/enji-db:(read|update|create|details)-(roles|users)"
        - Wildcard: "/.*"

        Args:
            claims: JWTClaims object
            permission: Permission to check

        Returns:
            True if user has the permission (pattern match)

        Example:
            # Check exact permission
            if authenticator.has_permission(claims, "ff:access-copilot"):
                # User has copilot access

            # Check permission from schema (will match regex patterns)
            if authenticator.has_permission(claims, "enji-db:read-roles"):
                # User has read-roles permission (matches /enji-db:(read|update)-roles$)
        """
        return JWTAuthenticator._check_permission_list(permission, claims.permissions)

    @staticmethod
    def has_any_permission(
        claims: JWTClaims, permissions: list[str]
    ) -> bool:
        """
        Check if user has any of the specified permissions.

        Args:
            claims: JWTClaims object
            permissions: List of permissions to check (can be exact or patterns)

        Returns:
            True if user has any of the permissions
        """
        for permission in permissions:
            if JWTAuthenticator.has_permission(claims, permission):
                return True
        return False

    @staticmethod
    def has_all_permissions(
        claims: JWTClaims, permissions: list[str]
    ) -> bool:
        """
        Check if user has all of the specified permissions.

        Args:
            claims: JWTClaims object
            permissions: List of permissions to check (can be exact or patterns)

        Returns:
            True if user has all of the permissions
        """
        for permission in permissions:
            if not JWTAuthenticator.has_permission(claims, permission):
                return False
        return True
