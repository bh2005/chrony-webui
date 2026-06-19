import subprocess, re
from config import settings

def _run(args: list[str]) -> str:
    result = subprocess.run(
        [settings.chronyc_path] + args,
        capture_output=True, text=True, timeout=5
    )
    return result.stdout

def get_tracking() -> dict:
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
    raw = _run(["-c", "sources"])
    sources = []
    for line in raw.splitlines():
        parts = line.split(",")
        if len(parts) < 10:
            continue
        sources.append({
            "mode":       parts[0],   # ^, *, -, +, ?
            "state":      parts[1],   # * = synced, - = combined, + = candidate
            "name":       parts[2],
            "stratum":    _int(parts[3]),
            "poll":       _int(parts[4]),
            "reach":      parts[5],
            "last_rx":    parts[6],
            "last_sample_offset": parts[7],
            "last_sample_err":    parts[8],
            "offset":     parts[9] if len(parts) > 9 else "",
        })
    return sources

def get_activity() -> dict:
    raw = _run(["activity"])
    nums = re.findall(r"\d+", raw)
    keys = ["online", "offline", "burst_online", "burst_offline", "unresolved"]
    return {k: int(v) for k, v in zip(keys, nums)} if len(nums) >= 5 else {}

def get_config() -> dict:
    """Liest primary/fallback Server aus chrony.conf"""
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
    """Schreibt chrony.conf neu. Erhält andere Direktiven (makestep, driftfile etc.)"""
    try:
        with open(settings.chrony_conf_path) as f:
            old = f.read()
    except FileNotFoundError:
        old = ""

    # Entferne alle server/pool-Zeilen
    lines = [l for l in old.splitlines() if not re.match(r"^\s*(server|pool)\s+", l)]

    # Neue Server-Blöcke an den Anfang
    new_server_lines = []
    for addr in primary:
        new_server_lines.append(f"server {addr} iburst prefer")
    for addr in fallback:
        new_server_lines.append(f"server {addr} iburst")

    content = "\n".join(new_server_lines) + "\n" + "\n".join(lines).lstrip()

    with open(settings.chrony_conf_path, "w") as f:
        f.write(content)

    subprocess.run(settings.reload_command.split(), check=True, timeout=10)

def _int(s: str) -> int:
    try:
        return int(re.search(r"\d+", s).group())
    except Exception:
        return 0
