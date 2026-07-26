"""Authorization tests for role and permission checking logic.

This module tests the authorization helpers in JWTAuthenticator:
- Role-based access (has_role, has_any_role, has_all_roles)
- Permission-based access (has_permission, has_any_permission, has_all_permissions)
- Permission disallow list (is_permission_disallowed)

Notable behavior:
- "stakeholder" role is always allowed (bypass mechanism)
- Permissions support regex patterns prefixed with /
- Invalid regex patterns are treated as non-matches (no exception)
- Deny list takes precedence over allow list
"""

import pytest

from enjilib_jwt import JWTAuthenticator, JWTClaims


def make_claims(*, roles=None, permissions=None, disallows=None):
    """Helper to build JWTClaims for testing.
    
    Args:
        roles: List of roles (default: [])
        permissions: List of allowed permissions (default: [])
        disallows: List of disallowed permissions (default: [])
        
    Returns:
        JWTClaims instance with specified claims
    """
    return JWTClaims(
        user_id=1,
        email="u@example.com",
        roles=roles or [],
        permissions=permissions or [],
        disallows=disallows or [],
    )


# ============================================================================
# ROLE TESTS
# ============================================================================


class TestHasRole:
    """Test basic has_role checks."""

    def test_has_role_true_when_user_has_role(self):
        """User with 'admin' role should have has_role(..., 'admin') == True."""
        claims = make_claims(roles=["admin", "editor"])
        assert JWTAuthenticator.has_role(claims, "admin") is True

    def test_has_role_false_when_user_lacks_role(self):
        """User without 'editor' role should have has_role(..., 'editor') == False."""
        claims = make_claims(roles=["admin"])
        assert JWTAuthenticator.has_role(claims, "editor") is False

    def test_has_role_false_for_empty_roles(self):
        """User with no roles should not have any role (except stakeholder)."""
        claims = make_claims(roles=[])
        assert JWTAuthenticator.has_role(claims, "admin") is False

    def test_has_role_stakeholder_bypass_always_true(self):
        """Stakeholder bypass: has_role(..., 'stakeholder') is always True.
        
        This is surprising but intentional behavior: even users with empty roles
        are granted stakeholder access unconditionally.
        """
        claims = make_claims(roles=[])
        assert JWTAuthenticator.has_role(claims, "stakeholder") is True

    def test_has_role_stakeholder_bypass_with_other_roles(self):
        """Stakeholder bypass works regardless of other roles."""
        claims = make_claims(roles=["admin", "editor"])
        assert JWTAuthenticator.has_role(claims, "stakeholder") is True


class TestHasAnyRole:
    """Test has_any_role checks."""

    @pytest.mark.parametrize(
        "user_roles,check_roles,expected",
        [
            (["admin"], ["admin", "editor"], True),
            (["editor"], ["admin", "editor"], True),
            (["admin", "editor"], ["admin", "editor"], True),
            (["moderator"], ["admin", "editor"], False),
            ([], ["admin", "editor"], False),
        ],
    )
    def test_has_any_role_matrix(self, user_roles, check_roles, expected):
        """Test has_any_role with various role combinations."""
        claims = make_claims(roles=user_roles)
        result = JWTAuthenticator.has_any_role(claims, check_roles)
        assert result is expected

    def test_has_any_role_stakeholder_bypass_always_true(self):
        """Stakeholder in check list bypasses: has_any_role(..., ['stakeholder', ...]) is always True.
        
        This is surprising but intentional: requesting stakeholder access is always granted
        regardless of actual user roles.
        """
        claims = make_claims(roles=[])
        assert JWTAuthenticator.has_any_role(claims, ["stakeholder"]) is True

    def test_has_any_role_stakeholder_bypass_with_other_check_roles(self):
        """Stakeholder in check list takes precedence."""
        claims = make_claims(roles=["editor"])
        assert JWTAuthenticator.has_any_role(claims, ["admin", "stakeholder"]) is True


class TestHasAllRoles:
    """Test has_all_roles checks."""

    @pytest.mark.parametrize(
        "user_roles,check_roles,expected",
        [
            (["admin", "editor"], ["admin", "editor"], True),
            (["admin"], ["admin", "editor"], False),
            (["editor"], ["admin", "editor"], False),
            ([], ["admin", "editor"], False),
        ],
    )
    def test_has_all_roles_matrix(self, user_roles, check_roles, expected):
        """Test has_all_roles with various role combinations."""
        claims = make_claims(roles=user_roles)
        result = JWTAuthenticator.has_all_roles(claims, check_roles)
        assert result is expected

    def test_has_all_roles_stakeholder_bypass_always_true(self):
        """Stakeholder in check list bypasses: has_all_roles(..., [..., 'stakeholder']) is always True.
        
        This is surprising but intentional: even if the user lacks 'admin', if we require
        ['admin', 'stakeholder'], the stakeholder bypass makes the entire check True.
        """
        claims = make_claims(roles=[])
        assert JWTAuthenticator.has_all_roles(claims, ["admin", "stakeholder"]) is True

    def test_has_all_roles_stakeholder_bypass_even_missing_other_roles(self):
        """Stakeholder in check list bypasses even when other required roles are missing."""
        claims = make_claims(roles=["editor"])
        # User has editor but not admin; normally False
        # But with stakeholder in the list, True (bypass)
        assert JWTAuthenticator.has_all_roles(claims, ["admin", "stakeholder"]) is True

    def test_has_all_roles_without_stakeholder_requires_all(self):
        """Without stakeholder, all roles must be present."""
        claims = make_claims(roles=["editor"])
        assert JWTAuthenticator.has_all_roles(claims, ["admin", "editor"]) is False


# ============================================================================
# PERMISSION TESTS — EXACT MATCHES
# ============================================================================


class TestHasPermissionExact:
    """Test exact permission matching."""

    def test_has_permission_exact_allow_true(self):
        """Permission in allow list should return True."""
        claims = make_claims(permissions=["ff:access-copilot"])
        assert JWTAuthenticator.has_permission(claims, "ff:access-copilot") is True

    def test_has_permission_exact_not_in_allow_false(self):
        """Permission not in allow list should return False."""
        claims = make_claims(permissions=["ff:access-copilot"])
        assert JWTAuthenticator.has_permission(claims, "ff:access-other") is False

    def test_has_permission_empty_allow_false(self):
        """No permissions in allow list should return False."""
        claims = make_claims(permissions=[])
        assert JWTAuthenticator.has_permission(claims, "ff:access-copilot") is False

    def test_has_permission_disallow_blocks_even_when_allowed(self):
        """Permission in disallow list blocks even if also in allow list.
        
        Disallow list takes precedence over allow list.
        """
        claims = make_claims(
            permissions=["ff:access-copilot"],
            disallows=["ff:access-copilot"],
        )
        assert JWTAuthenticator.has_permission(claims, "ff:access-copilot") is False

    def test_has_permission_disallow_specific_blocks_allow_general(self):
        """Specific disallow takes precedence over general allow."""
        claims = make_claims(
            permissions=["ff:*"],
            disallows=["ff:access-copilot"],
        )
        # If we were to check exact "ff:*", it would be in allow, but let's check exact:
        # This should be blocked because disallow is checked first
        assert JWTAuthenticator.has_permission(claims, "ff:access-copilot") is False


# ============================================================================
# PERMISSION TESTS — REGEX PATTERNS
# ============================================================================


class TestHasPermissionRegex:
    """Test regex pattern permission matching."""

    def test_has_permission_regex_allows_matching_permission(self):
        """Regex pattern /enji-db:(read|update)-roles$ should match valid permissions."""
        claims = make_claims(permissions=["/enji-db:(read|update)-roles$"])
        assert JWTAuthenticator.has_permission(claims, "enji-db:read-roles") is True
        assert JWTAuthenticator.has_permission(claims, "enji-db:update-roles") is True

    def test_has_permission_regex_rejects_non_matching_permission(self):
        """Regex pattern should reject non-matching permissions."""
        claims = make_claims(permissions=["/enji-db:(read|update)-roles$"])
        assert JWTAuthenticator.has_permission(claims, "enji-db:delete-roles") is False
        assert JWTAuthenticator.has_permission(claims, "enji-db:read-users") is False

    def test_has_permission_wildcard_allows_arbitrary(self):
        """Wildcard /.*/ pattern allows arbitrary permissions."""
        claims = make_claims(permissions=["/.*"])
        assert JWTAuthenticator.has_permission(claims, "anything") is True
        assert JWTAuthenticator.has_permission(claims, "enji-db:read-roles") is True
        assert JWTAuthenticator.has_permission(claims, "ff:access-copilot") is True

    def test_has_permission_wildcard_can_be_disallowed(self):
        """Specific disallow takes precedence over wildcard allow."""
        claims = make_claims(
            permissions=["/.*"],
            disallows=["admin:delete-users"],
        )
        assert JWTAuthenticator.has_permission(claims, "admin:delete-users") is False
        assert JWTAuthenticator.has_permission(claims, "anything:else") is True

    def test_has_permission_disallow_regex_overrides_allow_regex(self):
        """Disallow regex takes precedence over allow regex."""
        claims = make_claims(
            permissions=["/enji-db:.*"],
            disallows=["/enji-db:delete-.*"],
        )
        assert JWTAuthenticator.has_permission(claims, "enji-db:read-roles") is True
        assert JWTAuthenticator.has_permission(claims, "enji-db:delete-roles") is False

    def test_has_permission_prefix_matching_with_rematch(self):
        """Pattern 'admin' matches 'admin.extra' via re.match (prefix behavior).
        
        re.match is prefix-anchored, so 'admin' pattern matches any permission starting
        with 'admin'. This is current behavior, documented here to pin it.
        """
        claims = make_claims(permissions=["admin"])
        # 'admin' pattern matches 'admin.extra' because re.match is prefix-anchored
        assert JWTAuthenticator.has_permission(claims, "admin") is True
        assert JWTAuthenticator.has_permission(claims, "admin.extra") is True
        assert JWTAuthenticator.has_permission(claims, "admin-something") is True
        # But doesn't match if 'admin' is not at the start
        assert JWTAuthenticator.has_permission(claims, "not-admin") is False


# ============================================================================
# PERMISSION TESTS — EDGE CASES
# ============================================================================


class TestHasPermissionEdgeCases:
    """Test edge cases in permission matching."""

    def test_has_permission_invalid_regex_treated_as_non_match(self):
        """Invalid regex patterns should be treated as non-matches, not raise exceptions.
        
        An unclosed bracket '[' is invalid regex and should return False without raising.
        """
        claims = make_claims(permissions=["/[unclosed"])
        # Should not raise; should return False because pattern is invalid
        result = JWTAuthenticator.has_permission(claims, "anything")
        assert result is False

    def test_has_permission_invalid_regex_in_disallow_ignored(self):
        """Invalid regex in disallow list should be treated as non-match."""
        claims = make_claims(
            permissions=["anything"],
            disallows=["/[unclosed"],
        )
        # Invalid regex in disallow should not match, so permission is allowed
        result = JWTAuthenticator.has_permission(claims, "anything")
        assert result is True

    def test_has_permission_multiple_patterns_any_match_succeeds(self):
        """Multiple patterns in allow list: any match grants permission."""
        claims = make_claims(permissions=["admin", "editor", "/.*-special"])
        assert JWTAuthenticator.has_permission(claims, "admin") is True
        assert JWTAuthenticator.has_permission(claims, "editor") is True
        assert JWTAuthenticator.has_permission(claims, "read-special") is True
        assert JWTAuthenticator.has_permission(claims, "unknown") is False


# ============================================================================
# PERMISSION TESTS — COMPOSITION METHODS
# ============================================================================


class TestHasAnyPermission:
    """Test has_any_permission composing multiple permission checks."""

    @pytest.mark.parametrize(
        "permissions,check_perms,expected",
        [
            (["admin", "editor"], ["admin", "viewer"], True),
            (["viewer"], ["admin", "editor"], False),
            (["/.*"], ["admin", "editor"], True),
            ([], ["admin", "editor"], False),
        ],
    )
    def test_has_any_permission_matrix(self, permissions, check_perms, expected):
        """Test has_any_permission with various permission combinations."""
        claims = make_claims(permissions=permissions)
        result = JWTAuthenticator.has_any_permission(claims, check_perms)
        assert result is expected

    def test_has_any_permission_disallow_precedence(self):
        """Disallow blocks even in has_any_permission."""
        claims = make_claims(
            permissions=["admin", "editor"],
            disallows=["admin"],
        )
        # admin is disallowed, so checking it returns False
        assert JWTAuthenticator.has_any_permission(claims, ["admin"]) is False
        # editor is allowed
        assert JWTAuthenticator.has_any_permission(claims, ["editor"]) is True
        # both: editor is allowed, so True
        assert JWTAuthenticator.has_any_permission(claims, ["admin", "editor"]) is True


class TestHasAllPermissions:
    """Test has_all_permissions composing multiple permission checks."""

    @pytest.mark.parametrize(
        "permissions,check_perms,expected",
        [
            (["admin", "editor"], ["admin", "editor"], True),
            (["admin"], ["admin", "editor"], False),
            (["/.*"], ["admin", "editor"], True),
            ([], ["admin", "editor"], False),
        ],
    )
    def test_has_all_permissions_matrix(self, permissions, check_perms, expected):
        """Test has_all_permissions with various permission combinations."""
        claims = make_claims(permissions=permissions)
        result = JWTAuthenticator.has_all_permissions(claims, check_perms)
        assert result is expected

    def test_has_all_permissions_disallow_precedence(self):
        """Disallow blocks even in has_all_permissions."""
        claims = make_claims(
            permissions=["admin", "editor", "viewer"],
            disallows=["editor"],
        )
        # admin and viewer are allowed
        assert JWTAuthenticator.has_all_permissions(claims, ["admin", "viewer"]) is True
        # editor is disallowed
        assert JWTAuthenticator.has_all_permissions(claims, ["editor"]) is False
        # admin and editor: editor is disallowed, so False
        assert JWTAuthenticator.has_all_permissions(claims, ["admin", "editor"]) is False


# ============================================================================
# PERMISSION TESTS — DISALLOW CHECKS
# ============================================================================


class TestIsPermissionDisallowed:
    """Test is_permission_disallowed checks."""

    def test_is_permission_disallowed_exact_match(self):
        """Permission in disallow list should return True."""
        claims = make_claims(disallows=["admin:delete-users"])
        assert JWTAuthenticator.is_permission_disallowed(claims, "admin:delete-users") is True

    def test_is_permission_disallowed_not_disallowed(self):
        """Permission not in disallow list should return False."""
        claims = make_claims(disallows=["admin:delete-users"])
        assert JWTAuthenticator.is_permission_disallowed(claims, "admin:read-users") is False

    def test_is_permission_disallowed_empty_disallow_false(self):
        """Empty disallow list should return False."""
        claims = make_claims(disallows=[])
        assert JWTAuthenticator.is_permission_disallowed(claims, "admin:delete-users") is False

    def test_is_permission_disallowed_regex_pattern(self):
        """Disallow can use regex patterns."""
        claims = make_claims(disallows=["/admin:delete-.*"])
        assert JWTAuthenticator.is_permission_disallowed(claims, "admin:delete-users") is True
        assert JWTAuthenticator.is_permission_disallowed(claims, "admin:delete-roles") is True
        assert JWTAuthenticator.is_permission_disallowed(claims, "admin:read-users") is False

    def test_is_permission_disallowed_wildcard(self):
        """Wildcard disallow blocks all permissions."""
        claims = make_claims(disallows=["/.*"])
        assert JWTAuthenticator.is_permission_disallowed(claims, "anything") is True
        assert JWTAuthenticator.is_permission_disallowed(claims, "admin:delete-users") is True

    def test_is_permission_disallowed_invalid_regex(self):
        """Invalid regex in disallow returns False (non-match)."""
        claims = make_claims(disallows=["/[unclosed"])
        assert JWTAuthenticator.is_permission_disallowed(claims, "anything") is False


# ============================================================================
# INTEGRATION TESTS — COMBINED SCENARIOS
# ============================================================================


class TestCombinedScenarios:
    """Integration tests combining roles and permissions."""

    def test_full_authorization_scenario_allowed(self):
        """Complete scenario: user with multiple roles and permissions."""
        claims = make_claims(
            roles=["admin", "editor"],
            permissions=["ff:access-copilot", "/enji-db:(read|write)-.*"],
        )
        # Role checks
        assert JWTAuthenticator.has_role(claims, "admin") is True
        assert JWTAuthenticator.has_any_role(claims, ["admin", "viewer"]) is True
        # Permission checks
        assert JWTAuthenticator.has_permission(claims, "ff:access-copilot") is True
        assert JWTAuthenticator.has_permission(claims, "enji-db:read-roles") is True
        assert JWTAuthenticator.has_permission(claims, "enji-db:write-users") is True

    def test_full_authorization_scenario_denied(self):
        """Complete scenario: user denied specific permissions."""
        claims = make_claims(
            roles=["editor"],
            permissions=["/.*"],
            disallows=["admin:.*"],
        )
        # Role check
        assert JWTAuthenticator.has_role(claims, "admin") is False
        assert JWTAuthenticator.has_role(claims, "editor") is True
        # Permission checks
        assert JWTAuthenticator.has_permission(claims, "ff:access-copilot") is True
        assert JWTAuthenticator.has_permission(claims, "admin:delete-users") is False
        # Stakeholder bypass still works
        assert JWTAuthenticator.has_role(claims, "stakeholder") is True

    def test_empty_claims_all_denied_except_stakeholder(self):
        """User with no roles/permissions/disallows should be denied everything except stakeholder."""
        claims = make_claims()
        # Empty claims
        assert JWTAuthenticator.has_role(claims, "admin") is False
        assert JWTAuthenticator.has_permission(claims, "ff:access-copilot") is False
        # But stakeholder bypass still works
        assert JWTAuthenticator.has_role(claims, "stakeholder") is True
