import subprocess, re, os
from config import settings

MOCK = os.getenv("MOCK_CHRONY", "false").lower() == "true"

# In-Memory-State für Mock-Modus
_mock_config = {
    "primary":  ["10.122.3.35", "10.122.3.36"],
    "fallback": ["0.pool.ntp.org", "1.pool.ntp.org"],
}

def _run(args: list[str]) -> str:
    if MOCK:
        return ""
    result = subprocess.run(
        [settings.chronyc_path] + args,
        capture_output=True, text=True, timeout=5
    )
    return result.stdout

def get_tracking() -> dict:
    if MOCK:
        return {
            "reference_id":    "0A7A0323 (ntp-intern.k-plus-s.net)",
            "stratum":         2,
            "ref_time":        "2026-06-19 10:00:00 UTC",
            "system_time":     "0.000123456 seconds fast of NTP time",
            "last_offset":     "+0.000022343 seconds",
            "rms_offset":      "0.000031245 seconds",
            "frequency":       "12.345 ppm slow",
            "residual_freq":   "+0.003 ppm",
            "skew":            "0.087 ppm",
            "root_delay":      "0.001234567 seconds",
            "root_dispersion": "0.000456789 seconds",
            "update_interval": "64.2 seconds",
            "leap_status":     "Normal",
        }

    raw = _run(["tracking"])
    fields = {}
    for line in raw.splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            fields[key.strip()] = val.strip()

    def f(k): return fields.get(k, "")
    return {
        "reference_id":    f("Reference ID"),
        "stratum":         _int(f("Stratum")),
        "ref_time":        f("Ref time (UTC)"),
        "system_time":     f("System time"),
        "last_offset":     f("Last offset"),
        "rms_offset":      f("RMS offset"),
        "frequency":       f("Frequency"),
        "residual_freq":   f("Residual freq"),
        "skew":            f("Skew"),
        "root_delay":      f("Root delay"),
        "root_dispersion": f("Root dispersion"),
        "update_interval": f("Update interval"),
        "leap_status":     f("Leap status"),
    }

def get_sources() -> list[dict]:
    if MOCK:
        return [
            {"mode": "^", "state": "*", "name": "10.122.3.35",              "stratum": 1, "poll": 6, "reach": "377", "last_rx": "2",  "last_sample_offset": "-0.123us", "last_sample_err": "+/- 1.2us", "offset": "-123ns"},
            {"mode": "^", "state": "-", "name": "10.122.3.36",              "stratum": 1, "poll": 6, "reach": "377", "last_rx": "3",  "last_sample_offset": "+0.234us", "last_sample_err": "+/- 0.9us", "offset": "+234ns"},
            {"mode": "^", "state": "?", "name": "0.pool.ntp.org",           "stratum": 0, "poll": 7, "reach": "000", "last_rx": "-",  "last_sample_offset": "+0ns",     "last_sample_err": "+/- 0ns",   "offset": "+0ns"},
            {"mode": "^", "state": "?", "name": "1.pool.ntp.org",           "stratum": 0, "poll": 7, "reach": "000", "last_rx": "-",  "last_sample_offset": "+0ns",     "last_sample_err": "+/- 0ns",   "offset": "+0ns"},
        ]

    raw = _run(["-c", "sources"])
    sources = []
    for line in raw.splitlines():
        parts = line.split(",")
        if len(parts) < 10:
            continue
        sources.append({
            "mode":               parts[0],
            "state":              parts[1],
            "name":               parts[2],
            "stratum":            _int(parts[3]),
            "poll":               _int(parts[4]),
            "reach":              parts[5],
            "last_rx":            parts[6],
            "last_sample_offset": parts[7],
            "last_sample_err":    parts[8],
            "offset":             parts[9] if len(parts) > 9 else "",
        })
    return sources

def get_activity() -> dict:
    if MOCK:
        return {"online": 2, "offline": 0, "burst_online": 0, "burst_offline": 0, "unresolved": 2}

    raw = _run(["activity"])
    nums = re.findall(r"\d+", raw)
    keys = ["online", "offline", "burst_online", "burst_offline", "unresolved"]
    return {k: int(v) for k, v in zip(keys, nums)} if len(nums) >= 5 else {}

def get_config() -> dict:
    if MOCK:
        return {
            "primary":  [{"address": a, "type": "server", "options": "iburst prefer"} for a in _mock_config["primary"]],
            "fallback": [{"address": a, "type": "server", "options": "iburst"}        for a in _mock_config["fallback"]],
        }

    primary, fallback = [], []
    try:
        with open(settings.chrony_conf_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("#") or not line:
                    continue
                m = re.match(r"^(server|pool)\s+(\S+)(.*)", line)
                if m:
                    opts = m.group(3)
                    entry = {"address": m.group(2), "type": m.group(1), "options": opts.strip()}
                    if "prefer" in opts:
                        primary.append(entry)
                    else:
                        fallback.append(entry)
    except FileNotFoundError:
        pass
    return {"primary": primary, "fallback": fallback}

def write_config(primary: list[str], fallback: list[str]) -> None:
    if MOCK:
        _mock_config["primary"]  = primary
        _mock_config["fallback"] = fallback
        return

    try:
        with open(settings.chrony_conf_path) as f:
            old = f.read()
    except FileNotFoundError:
        old = ""

    lines = [l for l in old.splitlines() if not re.match(r"^\s*(server|pool)\s+", l)]
    new_server_lines = [f"server {a} iburst prefer" for a in primary] + \
                       [f"server {a} iburst" for a in fallback]
    content = "\n".join(new_server_lines) + "\n" + "\n".join(lines).lstrip()

    with open(settings.chrony_conf_path, "w") as f:
        f.write(content)

    subprocess.run(settings.reload_command.split(), check=True, timeout=10)

def _int(s: str) -> int:
    try:
        return int(re.search(r"\d+", s).group())
    except Exception:
        return 0
