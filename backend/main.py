from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chrony
from config import settings

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

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def require_key(key: str = Security(api_key_header)):
    if key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return key


@app.get("/health", tags=["system"], summary="Health-Check (kein Auth)")
def health():
    """Liefert den Sync-Status von chrony. Geeignet für Monitoring-Systeme."""
    try:
        tracking = chrony.get_tracking()
        activity = chrony.get_activity()
        stratum  = tracking.get("stratum", 0)
        ref      = tracking.get("reference_id", "")
        synced   = stratum > 0 and stratum < 16

        return {
            "status":     "ok" if synced else "warn",
            "synced":     synced,
            "stratum":    stratum,
            "reference":  ref,
            "leap_status": tracking.get("leap_status", ""),
            "online_sources": activity.get("online", 0),
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}


@app.get("/api/status", tags=["ntp"], summary="Tracking-Info und Aktivität")
def status(_=Depends(require_key)):
    """chronyc tracking + activity als JSON."""
    return {
        "tracking": chrony.get_tracking(),
        "activity": chrony.get_activity(),
    }


@app.get("/api/sources", tags=["ntp"], summary="Alle NTP-Quellen")
def sources(_=Depends(require_key)):
    """Entspricht `chronyc -c sources`."""
    return chrony.get_sources()


@app.get("/api/config", tags=["config"], summary="Aktuelle NTP-Server-Konfiguration")
def get_config(_=Depends(require_key)):
    """Liest primäre und Fallback-Server aus chrony.conf."""
    return chrony.get_config()


class ConfigUpdate(BaseModel):
    primary:  list[str]
    fallback: list[str]

@app.put("/api/config", tags=["config"], summary="NTP-Server-Konfiguration aktualisieren")
def update_config(body: ConfigUpdate, _=Depends(require_key)):
    """
    Schreibt chrony.conf neu und führt chrony reload aus.
    Andere Direktiven (makestep, driftfile…) bleiben erhalten.
    """
    if not body.primary and not body.fallback:
        raise HTTPException(400, "At least one server required")
    try:
        chrony.write_config(body.primary, body.fallback)
    except Exception as e:
        raise HTTPException(500, str(e))
    return {"ok": True}
