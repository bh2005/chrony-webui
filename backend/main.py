from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chrony
from config import settings

app = FastAPI(title="chrony-webui API", version="1.0.0")
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


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/status")
def status(_=Depends(require_key)):
    return {
        "tracking": chrony.get_tracking(),
        "activity": chrony.get_activity(),
    }


@app.get("/api/sources")
def sources(_=Depends(require_key)):
    return chrony.get_sources()


@app.get("/api/config")
def get_config(_=Depends(require_key)):
    return chrony.get_config()


class ConfigUpdate(BaseModel):
    primary: list[str]
    fallback: list[str]

@app.put("/api/config")
def update_config(body: ConfigUpdate, _=Depends(require_key)):
    if not body.primary and not body.fallback:
        raise HTTPException(400, "At least one server required")
    try:
        chrony.write_config(body.primary, body.fallback)
    except Exception as e:
        raise HTTPException(500, str(e))
    return {"ok": True}
