import secrets, time
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from config import settings

_tokens: dict[str, float] = {}
TOKEN_TTL = 8 * 3600  # 8 Stunden

# Überschreibt das Env-Passwort zur Laufzeit
_password_override: str | None = None

auth_header = APIKeyHeader(name="X-Auth-Token", auto_error=False)

def _current_password() -> str:
    return _password_override if _password_override is not None else settings.admin_password

def login(username: str, password: str) -> str:
    if username != settings.admin_username or password != _current_password():
        raise HTTPException(status_code=401, detail="Ungültige Anmeldedaten")
    token = secrets.token_hex(32)
    _tokens[token] = time.time() + TOKEN_TTL
    return token

def change_password(current: str, new_pw: str) -> None:
    global _password_override
    if current != _current_password():
        raise HTTPException(status_code=401, detail="Aktuelles Passwort falsch")
    if len(new_pw) < 6:
        raise HTTPException(status_code=400, detail="Passwort muss mindestens 6 Zeichen haben")
    _password_override = new_pw
    # Alle anderen Sessions invalidieren (außer der aktuellen — Aufrufer bleibt eingeloggt)
    # Sessions bleiben gültig, nur neues Login braucht das neue PW

def logout(token: str):
    _tokens.pop(token, None)

def require_auth(token: str = Security(auth_header)):
    if not token:
        raise HTTPException(status_code=401, detail="Nicht angemeldet")
    exp = _tokens.get(token)
    if not exp:
        raise HTTPException(status_code=401, detail="Ungültiger Token")
    if time.time() > exp:
        _tokens.pop(token, None)
        raise HTTPException(status_code=401, detail="Session abgelaufen")
    return token
