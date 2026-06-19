from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess, os
import chrony
from config import settings
from auth import require_auth, login, logout, change_password, auth_header

app = FastAPI(
    title="chrony-webui API",
    version="1.0.0",
    description="NTP-Server Monitoring und Konfiguration via chrony",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Legacy API-Key (Check_MK / externe Tools)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def require_key_or_auth(
    api_key: str = Security(api_key_header),
    token:   str = Security(auth_header),
):
    if api_key and api_key == settings.api_key:
        return
    if token:
        require_auth(token)
        return
    raise HTTPException(status_code=401, detail="Authentifizierung erforderlich")


# ── Auth ──────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/auth/login", tags=["auth"])
def auth_login(body: LoginRequest):
    token = login(body.username, body.password)
    return {"token": token}

@app.post("/auth/logout", tags=["auth"])
def auth_logout(token: str = Depends(require_auth)):
    logout(token)
    return {"ok": True}

@app.get("/auth/me", tags=["auth"])
def auth_me(token: str = Depends(require_auth)):
    return {"username": settings.admin_username, "authenticated": True}

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password:     str

@app.post("/auth/change-password", tags=["auth"])
def auth_change_password(body: ChangePasswordRequest, _=Depends(require_auth)):
    change_password(body.current_password, body.new_password)
    return {"ok": True}


# ── Health (öffentlich) ───────────────────────────────────────────────────────

@app.get("/health", tags=["system"])
def health():
    try:
        tracking = chrony.get_tracking()
        activity = chrony.get_activity()
        stratum  = tracking.get("stratum", 0)
        synced   = stratum > 0 and stratum < 16
        return {
            "status":         "ok" if synced else "warn",
            "synced":         synced,
            "stratum":        stratum,
            "reference":      tracking.get("reference_id", ""),
            "leap_status":    tracking.get("leap_status", ""),
            "online_sources": activity.get("online", 0),
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}


# ── NTP Status (öffentlich lesbar) ────────────────────────────────────────────

@app.get("/api/status", tags=["ntp"])
def status():
    return {
        "tracking": chrony.get_tracking(),
        "activity": chrony.get_activity(),
    }

@app.get("/api/sources", tags=["ntp"])
def sources():
    return chrony.get_sources()


# ── Konfiguration (Login erforderlich) ────────────────────────────────────────

@app.get("/api/config", tags=["config"])
def get_config(_=Depends(require_auth)):
    return chrony.get_config()

class ConfigUpdate(BaseModel):
    primary:  list[str]
    fallback: list[str]

@app.put("/api/config", tags=["config"])
def update_config(body: ConfigUpdate, _=Depends(require_auth)):
    if not body.primary and not body.fallback:
        raise HTTPException(400, "Mindestens ein Server erforderlich")
    try:
        chrony.write_config(body.primary, body.fallback)
    except Exception as e:
        raise HTTPException(500, str(e))
    return {"ok": True}


@app.get("/api/chrony-conf", tags=["config"])
def get_raw_conf(_=Depends(require_auth)):
    if chrony.MOCK:
        return {"content": "# Mock-Modus — keine echte chrony.conf\nserver 10.122.3.35 iburst prefer\nserver 10.122.3.36 iburst\nserver 0.pool.ntp.org iburst\n"}
    try:
        with open(settings.chrony_conf_path) as f:
            return {"content": f.read()}
    except FileNotFoundError:
        raise HTTPException(404, f"{settings.chrony_conf_path} nicht gefunden")

class RawConfUpdate(BaseModel):
    content: str

@app.put("/api/chrony-conf", tags=["config"])
def put_raw_conf(body: RawConfUpdate, _=Depends(require_auth)):
    if chrony.MOCK:
        return {"ok": True}
    try:
        with open(settings.chrony_conf_path, "w") as f:
            f.write(body.content)
        subprocess.run(settings.reload_command.split(), check=True, timeout=10)
    except Exception as e:
        raise HTTPException(500, str(e))
    return {"ok": True}


# ── Dienste (Login erforderlich) ──────────────────────────────────────────────

@app.post("/api/service/restart", tags=["service"])
def restart_service(_=Depends(require_auth)):
    if chrony.MOCK:
        return {"ok": True, "message": "Mock: chrony restart simuliert"}
    try:
        result = subprocess.run(
            settings.restart_command.split(),
            capture_output=True, text=True, timeout=15
        )
        if result.returncode != 0:
            raise HTTPException(500, result.stderr or "Restart fehlgeschlagen")
        return {"ok": True, "message": "chrony neu gestartet"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/api/service/status", tags=["service"])
def service_status(_=Depends(require_auth)):
    if chrony.MOCK:
        return {"active": True, "status": "active (running)", "since": "today"}
    try:
        r = subprocess.run(
            ["systemctl", "is-active", "chrony"],
            capture_output=True, text=True, timeout=5
        )
        active = r.stdout.strip() == "active"
        r2 = subprocess.run(
            ["systemctl", "status", "chrony", "--no-pager", "-l"],
            capture_output=True, text=True, timeout=5
        )
        return {"active": active, "status": r.stdout.strip(), "detail": r2.stdout[:1000]}
    except Exception as e:
        return {"active": False, "status": "error", "detail": str(e)}
