"""Autenticación local de la Puerta XIL-AC para Windows.

No incluye credenciales preconfiguradas. Las credenciales se derivan con PBKDF2;
el almacén se protege además con Windows DPAPI ligado al usuario de Windows.
"""
from __future__ import annotations

import ctypes
import hashlib
import hmac
import json
import os
import secrets
import time
from ctypes import wintypes
from pathlib import Path
from typing import Any

ITERATIONS = 310_000
MAX_FAILURES = 5
LOCK_SECONDS = 60


class _DataBlob(ctypes.Structure):
    _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_ubyte))]


def _dpapi(payload: bytes, protect: bool) -> bytes:
    if os.name != "nt":
        # Allows unit tests on other platforms; the shipped app targets Windows.
        return payload
    crypt32 = ctypes.WinDLL("crypt32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    crypt_fn = crypt32.CryptProtectData if protect else crypt32.CryptUnprotectData
    if protect:
        crypt_fn.argtypes = [ctypes.POINTER(_DataBlob), wintypes.LPCWSTR,
                             ctypes.POINTER(_DataBlob), ctypes.c_void_p,
                             ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(_DataBlob)]
    else:
        crypt_fn.argtypes = [ctypes.POINTER(_DataBlob), ctypes.POINTER(wintypes.LPWSTR),
                             ctypes.POINTER(_DataBlob), ctypes.c_void_p,
                             ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(_DataBlob)]
    crypt_fn.restype = wintypes.BOOL
    kernel32.LocalFree.argtypes = [ctypes.c_void_p]
    kernel32.LocalFree.restype = ctypes.c_void_p

    source_buffer = ctypes.create_string_buffer(payload)
    source = _DataBlob(len(payload), ctypes.cast(source_buffer, ctypes.POINTER(ctypes.c_ubyte)))
    output = _DataBlob()
    description = wintypes.LPWSTR()
    if protect:
        ok = crypt_fn(ctypes.byref(source), "XIL-AC local credentials", None, None, None, 0, ctypes.byref(output))
    else:
        ok = crypt_fn(ctypes.byref(source), ctypes.byref(description), None, None, None, 0, ctypes.byref(output))
    if not ok:
        raise RuntimeError("Windows no pudo proteger o abrir el almacén de credenciales.")
    try:
        return ctypes.string_at(output.pbData, output.cbData)
    finally:
        kernel32.LocalFree(ctypes.cast(output.pbData, ctypes.c_void_p))
        if description:
            kernel32.LocalFree(ctypes.cast(description, ctypes.c_void_p))


def _store_path() -> Path:
    base = os.environ.get("LOCALAPPDATA")
    if base:
        return Path(base) / "XIL-AC" / "auth.dat"
    return Path.home() / ".xil-ac" / "auth.dat"


def _derive(secret: str, salt_hex: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", secret.encode("utf-8"),
                               bytes.fromhex(salt_hex), ITERATIONS).hex()


def _read(path: Path | None = None) -> dict[str, Any]:
    target = path or _store_path()
    if not target.exists():
        return {"version": 1, "users": {}}
    try:
        raw = _dpapi(target.read_bytes(), False)
        data = json.loads(raw.decode("utf-8"))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise RuntimeError("No se puede abrir el almacén de acceso local en este usuario de Windows.") from exc
    if data.get("version") != 1 or not isinstance(data.get("users"), dict):
        raise RuntimeError("El almacén de acceso local tiene un formato inválido.")
    return data


def _write(data: dict[str, Any], path: Path | None = None) -> None:
    target = path or _store_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    protected = _dpapi(json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"), True)
    temp = target.with_suffix(".tmp")
    temp.write_bytes(protected)
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
        _derive(credential, "00" * 16)
        return False, "Usuario o credencial incorrectos."
    now = time.time()
    if float(account.get("locked_until", 0)) > now:
        remaining = max(1, int(account["locked_until"] - now))
        return False, f"Acceso temporalmente bloqueado. Esperá {remaining} segundos."
    if method not in ("password", "pin"):
        return False, "Método de acceso inválido."
    candidate = _derive(credential, account[f"{method}_salt"])
    if hmac.compare_digest(candidate, account[f"{method}_hash"]):
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
