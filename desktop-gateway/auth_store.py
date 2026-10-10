"""Autenticación local para la Puerta XIL-AC (prototipo Windows).

No incluye credenciales preconfiguradas. Los secretos nunca se guardan en texto
legible; las contraseñas y los PIN se derivan con PBKDF2-HMAC-SHA256.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import time
from pathlib import Path
from typing import Any

ITERATIONS = 310_000
MAX_FAILURES = 5
LOCK_SECONDS = 60


def _store_path() -> Path:
    base = os.environ.get("LOCALAPPDATA")
    if base:
        return Path(base) / "XIL-AC" / "auth.json"
    return Path.home() / ".xil-ac" / "auth.json"


def _derive(secret: str, salt_hex: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", secret.encode("utf-8"), bytes.fromhex(salt_hex), ITERATIONS
    ).hex()


def _read(path: Path | None = None) -> dict[str, Any]:
    target = path or _store_path()
    if not target.exists():
        return {"version": 1, "users": {}}
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError("No se puede leer el almacén de acceso local.") from exc
    if data.get("version") != 1 or not isinstance(data.get("users"), dict):
        raise RuntimeError("El almacén de acceso local tiene un formato inválido.")
    return data


def _write(data: dict[str, Any], path: Path | None = None) -> None:
    target = path or _store_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_suffix(".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        os.chmod(temp, 0o600)
    except OSError:
        pass
    temp.replace(target)


def has_users(path: Path | None = None) -> bool:
    return bool(_read(path)["users"])


def create_initial_user(username: str, password: str, pin: str,
                       path: Path | None = None) -> None:
    name = username.strip()
    if not name:
        raise ValueError("El usuario es obligatorio.")
    if len(password) < 10:
        raise ValueError("La contraseña debe tener al menos 10 caracteres.")
    if not pin.isdigit() or not 4 <= len(pin) <= 8:
        raise ValueError("El PIN debe tener entre 4 y 8 dígitos.")
    data = _read(path)
    if data["users"]:
        raise ValueError("Ya existe una cuenta inicial configurada.")
    data["users"][name.casefold()] = {
        "username": name,
        "password_salt": secrets.token_hex(16),
        "password_hash": "",
        "pin_salt": secrets.token_hex(16),
        "pin_hash": "",
        "failed_attempts": 0,
        "locked_until": 0,
    }
    account = data["users"][name.casefold()]
    account["password_hash"] = _derive(password, account["password_salt"])
    account["pin_hash"] = _derive(pin, account["pin_salt"])
    _write(data, path)


def authenticate(username: str, credential: str, method: str,
                 path: Path | None = None) -> tuple[bool, str]:
    """Returns (success, message). method is 'password' or 'pin'."""
    name = username.strip().casefold()
    data = _read(path)
    account = data["users"].get(name)
    if account is None:
        # Similar-cost derivation reduces trivial username timing differences.
        _derive(credential, "00" * 16)
        return False, "Usuario o credencial incorrectos."
    now = time.time()
    if float(account.get("locked_until", 0)) > now:
        remaining = max(1, int(account["locked_until"] - now))
        return False, f"Acceso temporalmente bloqueado. Esperá {remaining} segundos."
    if method not in ("password", "pin"):
        return False, "Método de acceso inválido."
    salt_key = f"{method}_salt"
    hash_key = f"{method}_hash"
    candidate = _derive(credential, account[salt_key])
    if hmac.compare_digest(candidate, account[hash_key]):
        account["failed_attempts"] = 0
        account["locked_until"] = 0
        _write(data, path)
        return True, "Acceso autorizado."
    account["failed_attempts"] = int(account.get("failed_attempts", 0)) + 1
    if account["failed_attempts"] >= MAX_FAILURES:
        account["failed_attempts"] = 0
        account["locked_until"] = now + LOCK_SECONDS
    _write(data, path)
    return False, "Usuario o credencial incorrectos."
