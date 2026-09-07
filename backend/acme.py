"""
ACME-Client-Wrapper (acme.sh) gegen die interne K+S step-ca.

Stellt Zertifikate per HTTP-01 (Webroot, über das bereits laufende Nginx)
aus und installiert sie für den Nginx-Reverse-Proxy dieser WebUI.
Voraussetzung: acme.sh ist bereits installiert und bei der internen CA
registriert (siehe Scripts/acme/01-setup-acme-client.sh).
"""
import subprocess, os, re
from datetime import datetime, timezone
from config import settings
from chrony import MOCK

# In-Memory-State für Mock-Modus (siehe chrony.py)
_mock_state = {
    "issued":    True,
    "domain":    "ntp01.corp.k-plus-s.net",
    "issuer":    "K+S Internal Issuing CA (step-ca) [Mock]",
    "not_after": "2026-11-15 12:00:00",
    "serial":    "7F3A9B2C1D",
}


def _cert_file() -> str:
    return os.path.join(settings.cert_install_dir, "fullchain.pem")


def _key_file() -> str:
    return os.path.join(settings.cert_install_dir, "privkey.pem")


def _run(args: list[str], timeout: int = 60) -> tuple[int, str]:
    result = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    return result.returncode, (result.stdout + result.stderr)


def get_status() -> dict:
    if MOCK:
        not_after = datetime.strptime(_mock_state["not_after"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        return {
            "acme_sh_available": True,
            "ca_url":            settings.acme_ca_url,
            "cert_exists":       _mock_state["issued"],
            "domain":            _mock_state["domain"],
            "issuer":            _mock_state["issuer"],
            "not_after":         _mock_state["not_after"],
            "days_remaining":    (not_after - datetime.now(timezone.utc)).days,
            "serial":            _mock_state["serial"],
        }

    acme_sh_available = os.path.isfile(settings.acme_sh_path)
    cert_file = _cert_file()

    if not os.path.isfile(cert_file):
        return {
            "acme_sh_available": acme_sh_available,
            "ca_url":            settings.acme_ca_url,
            "cert_exists":       False,
        }

    rc, out = _run([
        "openssl", "x509", "-noout", "-subject", "-issuer", "-enddate", "-serial",
        "-in", cert_file,
    ])
    fields: dict[str, str] = {}
    for line in out.splitlines():
        key, sep, val = line.partition("=")
        if sep:
            fields.setdefault(key.strip(), val.strip())

    not_after_raw = fields.get("notAfter", "")
    days_remaining = None
    if not_after_raw:
        try:
            not_after = datetime.strptime(not_after_raw, "%b %d %H:%M:%S %Y %Z")
            days_remaining = (not_after.replace(tzinfo=timezone.utc) - datetime.now(timezone.utc)).days
        except ValueError:
            pass

    domain_match = re.search(r"CN\s*=\s*([^,/\n]+)", fields.get("subject", ""))

    return {
        "acme_sh_available": acme_sh_available,
        "ca_url":            settings.acme_ca_url,
        "cert_exists":       True,
        "domain":            domain_match.group(1).strip() if domain_match else "",
        "issuer":            fields.get("issuer", ""),
        "not_after":         not_after_raw,
        "days_remaining":    days_remaining,
        "serial":            fields.get("serial", ""),
    }


def issue_cert(domain: str, sans: list[str] | None = None, email: str | None = None) -> str:
    if MOCK:
        _mock_state.update(
            issued=True, domain=domain,
            issuer="K+S Internal Issuing CA (step-ca) [Mock]",
            not_after="2026-12-01 12:00:00", serial="MOCK-SERIAL",
        )
        return f"Mock: Zertifikat für {domain} ausgestellt (kein echter ACME-Request, MOCK_CHRONY=true)."

    if not os.path.isfile(settings.acme_sh_path):
        raise RuntimeError(
            f"acme.sh nicht gefunden unter {settings.acme_sh_path} — "
            "bitte zuerst Scripts/acme/01-setup-acme-client.sh ausführen"
        )
    if not os.path.isdir(settings.acme_webroot):
        raise RuntimeError(f"Webroot-Verzeichnis nicht gefunden: {settings.acme_webroot}")

    san_args = []
    for s in (sans or []):
        san_args += ["-d", s]

    log = []

    # Account bei der internen CA registrieren (idempotent, falls E-Mail geändert wurde)
    if email:
        _, out = _run([
            settings.acme_sh_path, "--register-account",
            "--server", settings.acme_ca_url,
            "--accountemail", email,
        ])
        log.append(out)

    rc, out = _run([
        settings.acme_sh_path, "--issue",
        "-d", domain, *san_args,
        "--webroot", settings.acme_webroot,
        "--server", settings.acme_ca_url,
        "--cert-home", settings.acme_cert_home,
        "--keylength", "ec-256",  # step-ca erwartet EC, kein RSA
    ], timeout=120)
    log.append(out)
    if rc not in (0, 2):  # acme.sh: 2 = Zertifikat bereits gültig, keine Neuausstellung nötig
        raise RuntimeError("\n".join(log))

    os.makedirs(settings.cert_install_dir, exist_ok=True)
    rc, out = _run([
        settings.acme_sh_path, "--install-cert",
        "-d", domain, "--ecc",
        "--cert-file",      os.path.join(settings.cert_install_dir, "cert.pem"),
        "--key-file",       _key_file(),
        "--fullchain-file", _cert_file(),
        "--ca-file",        os.path.join(settings.cert_install_dir, "ca.pem"),
        "--reloadcmd",      settings.cert_deploy_reload_command,
        "--cert-home",      settings.acme_cert_home,
    ], timeout=30)
    log.append(out)
    if rc != 0:
        raise RuntimeError("\n".join(log))

    return "\n".join(log)


def renew_cert(domain: str) -> str:
    if MOCK:
        _mock_state["not_after"] = "2027-03-01 12:00:00"
        return f"Mock: Zertifikat für {domain} erneuert."

    if not os.path.isfile(settings.acme_sh_path):
        raise RuntimeError(f"acme.sh nicht gefunden unter {settings.acme_sh_path}")

    rc, out = _run([
        settings.acme_sh_path, "--renew", "-d", domain, "--force", "--ecc",
        "--cert-home", settings.acme_cert_home,
    ], timeout=120)
    if rc != 0:
        raise RuntimeError(out)
    return out
