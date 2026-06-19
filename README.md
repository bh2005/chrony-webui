# chrony-webui

Web-Frontend zur Überwachung und Konfiguration eines [chrony](https://chrony-project.org/) NTP-Servers.

**Stack:** FastAPI (Python) · Vue 3 + Tailwind CSS · Nginx

![Status Dashboard](docs/screenshot-dashboard.png)

---

## Features

- **Status-Dashboard** — Referenz-Server, Stratum, System-Offset, Root-Delay; alle NTP-Quellen mit Sync-Status, Reach und Offset; Auto-Refresh alle 10 s
- **Konfigurationsseite** — Primäre Server (K+S-intern, `iburst prefer`) und Fallback-Server (Internet, `iburst`) direkt bearbeiten; schreibt `chrony.conf` neu und führt `chrony reload` aus
- **Dark Mode** — toggle in der Sidebar, persistiert im LocalStorage
- **API-Key-Auth** — einfacher Bearer-Key, konfigurierbar per Env-Var

---

## Schnellstart (Docker · lokal)

```bash
docker compose up --build
```

Frontend: **http://localhost:8080** · API Key: `dev-key-local`

Im Standard-Docker-Setup läuft chrony im **Mock-Modus** (`MOCK_CHRONY=true`) — es werden Beispieldaten angezeigt, ohne dass chrony installiert sein muss.

---

## Deployment auf dem NTP-Server

### 1. Abhängigkeiten

```bash
apt-get install -y chrony python3 python3-venv nginx
```

### 2. Backend installieren

```bash
mkdir -p /opt/chrony-webui
cp -r backend/* /opt/chrony-webui/
python3 -m venv /opt/chrony-webui/venv
/opt/chrony-webui/venv/bin/pip install -r /opt/chrony-webui/requirements.txt
```

### 3. Konfiguration

```bash
mkdir -p /etc/chrony-webui
cp deploy/config.env.example /etc/chrony-webui/config.env
# CHRONYWEBUI_API_KEY setzen!
nano /etc/chrony-webui/config.env
```

### 4. systemd-Service

```bash
cp deploy/chrony-webui.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now chrony-webui
```

### 5. Frontend bauen und deployen

```bash
cd frontend
npm ci
npm run build
cp -r dist/* /var/www/chrony-webui/
```

### 6. Nginx

```bash
cp deploy/nginx.conf /etc/nginx/sites-available/chrony-webui
ln -s /etc/nginx/sites-available/chrony-webui /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

---

## Konfiguration (Env-Variablen)

| Variable | Standard | Beschreibung |
|---|---|---|
| `CHRONYWEBUI_API_KEY` | `changeme` | API-Schlüssel für die WebUI |
| `CHRONYWEBUI_CHRONY_CONF_PATH` | `/etc/chrony/chrony.conf` | Pfad zur chrony.conf |
| `CHRONYWEBUI_CHRONYC_PATH` | `/usr/bin/chronyc` | Pfad zu chronyc |
| `CHRONYWEBUI_RELOAD_COMMAND` | `systemctl reload chrony` | Befehl nach Config-Änderung |
| `MOCK_CHRONY` | `false` | `true` = Demo-Daten ohne chrony |

---

## API

Alle Endpunkte benötigen den Header `X-API-Key: <key>`.

| Methode | Pfad | Beschreibung |
|---|---|---|
| `GET` | `/api/status` | Tracking-Info + Aktivität |
| `GET` | `/api/sources` | Liste aller NTP-Quellen |
| `GET` | `/api/config` | Aktuelle Server-Konfiguration |
| `PUT` | `/api/config` | Server-Konfiguration aktualisieren |
| `GET` | `/health` | Health-Check (kein Auth) |

---

## Chrony-Konfiguration (Empfehlung)

```
# /etc/chrony/chrony.conf
# Primäre interne Server
server 10.122.3.35 iburst prefer
server 10.122.3.36 iburst

# Fallback: Internet NTP (nur wenn interne Server nicht erreichbar)
server 0.pool.ntp.org iburst
server 1.pool.ntp.org iburst

# Drift-Datei
driftfile /var/lib/chrony/drift

# Schrittkorrektur beim Start (max. 1 Sekunde)
makestep 1.0 3

# RTC synchronisieren
rtcsync

# Als NTP-Server für lokales Netz agieren
allow 10.0.0.0/8

# Logging
logdir /var/log/chrony
```
