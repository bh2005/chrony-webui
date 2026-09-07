"""
Rollierender In-Memory-Verlauf für die Dashboard-Grafiken (Offset, NTP-Anfragen/s).

chrony selbst hält keine Zeitreihe vor — `chronyc tracking`/`serverstats` liefern nur
Momentaufnahmen bzw. kumulative Zähler seit chronyd-Start. Ein Hintergrund-Task tastet
daher periodisch ab, bildet aus den kumulativen Zählern eine Rate (Anfragen/s) und legt
das Ergebnis in einem Ringpuffer ab. Kein externer Store — bei einem Neustart des
Backends beginnt der Verlauf einfach wieder leer.
"""
import asyncio, time
from collections import deque
import chrony

SAMPLE_INTERVAL = 10          # Sekunden — deckt sich mit dem Dashboard-Auto-Refresh
MAX_RANGE_MIN   = 24 * 60     # längster im Dashboard wählbarer Zeitraum: 24 Stunden
MAX_SAMPLES     = (MAX_RANGE_MIN * 60) // SAMPLE_INTERVAL  # 8640 Samples — im Speicher vernachlässigbar

_history: deque = deque(maxlen=MAX_SAMPLES)
_last_ntp_packets: int | None = None
_last_sample_time: float | None = None


def _sample_once() -> None:
    global _last_ntp_packets, _last_sample_time

    now = time.time()
    tracking    = chrony.get_tracking()
    activity    = chrony.get_activity()
    serverstats = chrony.get_serverstats()

    offset_us = None
    parsed = chrony.parse_offset_seconds(tracking.get("last_offset", ""))
    if parsed is not None:
        offset_us = parsed * 1_000_000  # Mikrosekunden — lesbarer als 1e-6-Sekundenwerte

    ntp_packets = serverstats.get("ntp_packets_received")
    ntp_reqs_per_sec = None
    if ntp_packets is not None and _last_ntp_packets is not None and _last_sample_time is not None:
        dt = now - _last_sample_time
        if dt > 0:
            rate = (ntp_packets - _last_ntp_packets) / dt
            ntp_reqs_per_sec = round(rate, 2) if rate >= 0 else 0.0  # Zähler-Reset (chronyd-Neustart) abfangen
    if ntp_packets is not None:
        _last_ntp_packets = ntp_packets
        _last_sample_time = now

    _history.append({
        "ts":               int(now),
        "stratum":          tracking.get("stratum"),
        "offset_us":        round(offset_us, 3) if offset_us is not None else None,
        "online_sources":   activity.get("online"),
        "ntp_reqs_per_sec": ntp_reqs_per_sec,
    })


async def _sampler_loop() -> None:
    while True:
        try:
            _sample_once()
        except Exception:
            pass  # ein einzelner fehlgeschlagener Sample-Zyklus soll den Loop nicht beenden
        await asyncio.sleep(SAMPLE_INTERVAL)


def start() -> None:
    asyncio.create_task(_sampler_loop())


def get_history(minutes: int | None = None) -> list[dict]:
    if not minutes:
        return list(_history)
    minutes = max(1, min(minutes, MAX_RANGE_MIN))
    cutoff = time.time() - minutes * 60
    return [s for s in _history if s["ts"] >= cutoff]
