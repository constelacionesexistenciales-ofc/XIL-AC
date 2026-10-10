"""Autenticación local restringida y validación OIDC para staging/producción."""
from __future__ import annotations

import hmac
import os
from dataclasses import dataclass
from typing import Annotated, Callable

import jwt
from fastapi import Depends, Header, HTTPException, status
from jwt import PyJWKClient
from jwt.exceptions import PyJWKClientConnectionError, PyJWKClientError, PyJWTError

from core.config import Settings

settings = Settings()


@dataclass(frozen=True)
class Principal:
    subject: str
    roles: frozenset[str]


def _verify_oidc_token(token: str, issuer: str, audience: str, jwks_url: str) -> dict:
    client = PyJWKClient(jwks_url, cache_jwk_set=True, lifespan=300, timeout=5)
    signing_key = client.get_signing_key_from_jwt(token)
    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256", "ES256"],
        issuer=issuer,
        audience=audience,
        options={"require": ["exp", "iss", "aud", "sub"]},
        leeway=30,
    )


def _claim_value(claims: dict, dotted_path: str):
    value = claims
    for part in dotted_path.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def get_current_principal(
    authorization: Annotated[str | None, Header()] = None,
) -> Principal:
    supplied = authorization or ""
    prefix = "Bearer "
    if not supplied.startswith(prefix) or not supplied[len(prefix):].strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = supplied[len(prefix):].strip()

    if settings.environment in {"staging", "production"}:
        issuer = settings.oidc_issuer
        audience = settings.oidc_audience
        jwks_url = settings.oidc_jwks_url
        if not issuer or not audience or not jwks_url:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="La autenticación de identidad no está configurada",
            )
        try:
            claims = _verify_oidc_token(token, issuer, audience, jwks_url)
        except PyJWKClientConnectionError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="El proveedor de identidad no está disponible",
            ) from None
        except (PyJWKClientError, PyJWTError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas",
                headers={"WWW-Authenticate": "Bearer"},
            ) from None

        subject = claims.get("sub")
        raw_roles = _claim_value(claims, settings.oidc_roles_claim)
        if not isinstance(subject, str) or not subject.strip():
            raise HTTPException(status_code=401, detail="Token sin identidad válida")
        if not isinstance(raw_roles, list) or not all(
            isinstance(role, str) for role in raw_roles
        ):
            raise HTTPException(status_code=403, detail="El token no contiene roles válidos")
        return Principal(subject=subject, roles=frozenset(raw_roles))

    expected = os.getenv("XILAC_API_TOKEN", "")
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Token local no configurado",
        )
    if not hmac.compare_digest(token, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Principal(
        subject="local-development",
        roles=frozenset({"admin", "facilitator", "auditor"}),
    )


def require_roles(*allowed_roles: str) -> Callable:
    allowed = frozenset(allowed_roles)

    def dependency(
        principal: Annotated[Principal, Depends(get_current_principal)],
    ) -> Principal:
        if not allowed.intersection(principal.roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El rol no permite esta operación",
            )
        return principal

    return dependency
