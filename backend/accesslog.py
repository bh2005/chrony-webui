"""
Rollierendes In-Memory-Zugriffs-Log für den Admin-Bereich — welche IP hat wann
welchen Endpunkt aufgerufen (primär interessant für /auth/login: wer versucht sich
von wo einzuloggen). Kein externer Store, wie history.py — bei Backend-Neustart leer.
"""
from collections import deque
from fastapi import Request
import time

MAX_ENTRIES = 500
_log: deque = deque(maxlen=MAX_ENTRIES)


def get_client_ip(request: Request) -> str:
    """Bevorzugt die von Nginx gesetzten Header (siehe deploy/nginx.conf,
    proxy_set_header X-Real-IP/X-Forwarded-For) — request.client.host wäre sonst
    immer 127.0.0.1 (Nginx als Reverse-Proxy)."""
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip
    return request.client.host if request.client else "?"


def record(ip: str, method: str, path: str, status: int) -> None:
    _log.appendleft({
        "ts":     int(time.time()),
        "ip":     ip,
        "method": method,
        "path":   path,
        "status": status,
    })


def get_log() -> list[dict]:
    return list(_log)
