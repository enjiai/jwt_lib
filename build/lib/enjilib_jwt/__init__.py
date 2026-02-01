"""JWT authentication utilities for Enji microservices.

This package provides JWT token verification and claims extraction
for all Enji backend services.

Usage:
    from enjilib_jwt import JWTAuthenticator, JWTClaims
    
    authenticator = JWTAuthenticator(secret_key, algorithm="HS256")
    claims = authenticator.verify_and_extract(token)
    
    if claims and authenticator.has_role(claims, "admin"):
        # User is admin
        pass
"""
from .authenticator import JWTAuthenticator
from .claims import JWTClaims

__version__ = "0.1.0"
__all__ = ["JWTAuthenticator", "JWTClaims"]
