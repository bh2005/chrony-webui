# chrony-webui

Web-Frontend zur Überwachung und Konfiguration eines [chrony](https://chrony-project.org/) NTP-Servers.

**Stack:** FastAPI (Python 3.12) · Vue 3 + Tailwind CSS · Nginx  
**Lizenz:** MIT

---

## Features

| | |
|---|---|
| **Status-Dashboard** | Referenz-Server, Stratum, System-Offset, Root-Delay; alle NTP-Quellen mit Sync-Status (`^*` / `^-`), Reach und Offset; Auto-Refresh alle 10 s |
| **Verlaufs-Grafiken** | System-Offset und NTP-Anfragen/s als Trend über die letzte Stunde (rollierender In-Memory-Verlauf, kein externer Store) |
| **Erlaubte Netze** | `allow`-Liste (welche Clients diesen Server als NTP-Quelle nutzen dürfen) direkt im Server-Tab verwaltbar |
| **Zugriffe** | NTP-Client-IPs (`chronyc clients`) und ein rollierendes Web/API-Zugriffs-Log (IP, Methode, Pfad, Status je Request) im Admin-Bereich |
| **Server-Konfiguration** | Primäre Server (`iburst prefer`) und Fallback-Server (`iburst`) verwalten; schreibt `chrony.conf` neu und führt `chrony reload` aus |
| **chrony.conf-Editor** | Direkte Inline-Bearbeitung der Konfigurationsdatei im Browser |
| **Dienste** | chrony-Service-Status anzeigen und neu starten |
| **Konto** | Admin-Passwort im laufenden Betrieb ändern |
| **Zertifikat** | TLS-Zertifikat per ACME (HTTP-01) gegen die interne K+S step-CA ausstellen/erneuern, Status & Ablaufdatum im Blick |
| **Dark Mode** | Toggle in der Sidebar, persistiert im LocalStorage |
| **Live-Uhrzeit** | Aktuelle Uhrzeit und Datum in der Sidebar (sekundengenau) |
| **Login-Schutz** | Status-Dashboard öffentlich; Konfiguration nur nach Login |
| **Check_MK** | Local-Check-Plugin für NTP-Sync-Monitoring |
| **Swagger/OpenAPI** | Interaktive API-Dokumentation unter `/api/docs` |

---

## Schnellstart (Docker · lokal)

```bash
git clone https://github.com/bh2005/chrony-webui.git
cd chrony-webui
docker compose up --build
```

| URL | Beschreibung |
|---|---|
| http://localhost:8080 | Web-Frontend |
| http://localhost:8080/api/docs | Swagger UI |
| http://localhost:8080/health | Health-Check (JSON) |

**Standard-Login:** `admin` / `admin`

> Im Standard-Docker-Setup läuft chrony im **Mock-Modus** (`MOCK_CHRONY=true`) —  
> es werden realistische Demo-Daten angezeigt, ohne dass chrony installiert sein muss.  
> Konfigurationsänderungen werden im Arbeitsspeicher gehalten (kein echter Schreibzugriff).

---

## Projektstruktur

```
chrony-webui/
├── backend/
│   ├── main.py            # FastAPI-App, alle Endpunkte
│   ├── auth.py            # Session-Token-Auth, Passwort-Verwaltung
│   ├── chrony.py          # chronyc-Parser + Mock-Modus
│   ├── config.py          # Einstellungen via Env-Variablen
│   ├── acme.py            # ACME-Client-Wrapper (acme.sh) gegen interne step-CA
│   ├── history.py         # Rollierender In-Memory-Verlauf für Dashboard-Grafiken
│   ├── accesslog.py       # Rollierendes Web/API-Zugriffs-Log (IP, Methode, Pfad, Status)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   │   ├── LoginView.vue      # Login-Seite
│   │   │   ├── Dashboard.vue      # Status-Dashboard
│   │   │   └── Config.vue         # Konfiguration (4 Tabs)
│   │   ├── components/
│   │   │   ├── AppSidebar.vue     # Navigation + Uhrzeit + Auth
│   │   │   ├── SidebarNavLink.vue
│   │   │   └── StatCard.vue
│   │   ├── api.js                 # Axios-Wrapper
│   │   └── main.js                # Router + Guards
│   ├── Dockerfile
│   └── nginx-docker.conf
├── deploy/
│   ├── chrony-webui.service       # systemd-Unit
│   ├── nginx.conf                 # Nginx Reverse Proxy
│   ├── config.env.example         # Konfigurationsvorlage
│   └── checkmk/
│       └── chrony_webui_health    # Check_MK Local Check
└── docker-compose.yml
```

---

## Deployment auf einem NTP-Server (nativ)

### Voraussetzungen

```bash
apt-get install -y chrony python3 python3-venv nginx
```

### 1. Backend installieren

```bash
mkdir -p /opt/chrony-webui
cp -r backend/* /opt/chrony-webui/
python3 -m venv /opt/chrony-webui/venv
/opt/chrony-webui/venv/bin/pip install -r /opt/chrony-webui/requirements.txt
```

### 2. Konfiguration anlegen

```bash
mkdir -p /etc/chrony-webui
cp deploy/config.env.example /etc/chrony-webui/config.env
nano /etc/chrony-webui/config.env
```

Mindestens `CHRONYWEBUI_ADMIN_PASSWORD` und `CHRONYWEBUI_API_KEY` setzen.

### 3. systemd-Service

```bash
cp deploy/chrony-webui.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now chrony-webui
systemctl status chrony-webui
```

### 4. Frontend bauen und deployen

```bash
cd frontend
npm ci
npm run build
mkdir -p /var/www/chrony-webui
cp -r dist/* /var/www/chrony-webui/
```

### 5. Nginx konfigurieren

```bash
cp deploy/nginx.conf /etc/nginx/sites-available/chrony-webui
ln -s /etc/nginx/sites-available/chrony-webui /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx
```

---

## Konfiguration (Env-Variablen)

Alle Variablen haben das Präfix `CHRONYWEBUI_`. Siehe auch [`deploy/config.env.example`](deploy/config.env.example).

| Variable | Standard | Beschreibung |
|---|---|---|
| `CHRONYWEBUI_ADMIN_USERNAME` | `admin` | Login-Benutzername |
| `CHRONYWEBUI_ADMIN_PASSWORD` | `admin` | Login-Passwort (bitte ändern!) |
| `CHRONYWEBUI_API_KEY` | `changeme` | API-Key für externe Tools (Check_MK etc.) |
| `CHRONYWEBUI_CHRONY_CONF_PATH` | `/etc/chrony/chrony.conf` | Pfad zur chrony.conf |
| `CHRONYWEBUI_CHRONYC_PATH` | `/usr/bin/chronyc` | Pfad zum chronyc-Binary |
| `CHRONYWEBUI_RELOAD_COMMAND` | `systemctl reload chrony` | Befehl nach Config-Änderung |
| `CHRONYWEBUI_RESTART_COMMAND` | `systemctl restart chrony` | Befehl für Service-Neustart |
| `CHRONYWEBUI_ACME_SH_PATH` | `/etc/acme/acme.sh` | Pfad zum installierten acme.sh-Client |
| `CHRONYWEBUI_ACME_CA_URL` | `https://dekdli047.corp.k-plus-s.net/acme/acme/directory` | Directory-URL der internen step-CA |
| `CHRONYWEBUI_ACME_CERT_HOME` | `/etc/acme/certs` | acme.sh Cert-Home |
| `CHRONYWEBUI_ACME_WEBROOT` | `/var/www/chrony-webui` | Webroot für HTTP-01 (= Nginx `root`) |
| `CHRONYWEBUI_ACME_EMAIL` | `monitoring@k-plus-s.com` | Standard-E-Mail für die Account-Registrierung |
| `CHRONYWEBUI_CERT_INSTALL_DIR` | `/etc/ssl/chrony-webui` | Zielverzeichnis für fullchain.pem/privkey.pem |
| `CHRONYWEBUI_CERT_DEPLOY_RELOAD_COMMAND` | `systemctl reload nginx` | Befehl nach Ausstellung/Erneuerung |
| `MOCK_CHRONY` | `false` | `true` = Demo-Daten ohne chrony (deckt auch das Zertifikat-Tab ab) |

---

## API-Referenz

Interaktive Dokumentation: **`/api/docs`** (Swagger UI) · **`/api/redoc`**

### Authentifizierung

Geschützte Endpunkte benötigen entweder:
- Header `X-Auth-Token: <session-token>` (Web-Login)
- Header `X-API-Key: <key>` (externe Tools, Check_MK)

### Endpunkte

| Methode | Pfad | Auth | Beschreibung |
|---|---|---|---|
| `GET` | `/health` | — | Health-Check mit Sync-Status |
| `POST` | `/auth/login` | — | Login → Session-Token |
| `POST` | `/auth/logout` | ✓ | Session beenden |
| `GET` | `/auth/me` | ✓ | Aktueller Benutzer |
| `POST` | `/auth/change-password` | ✓ | Passwort ändern |
| `GET` | `/api/status` | — | Tracking-Info + Aktivität |
| `GET` | `/api/sources` | — | Alle NTP-Quellen |
| `GET` | `/api/history` | — | Rollierender Verlauf (Offset, NTP-Anfragen/s) der letzten Stunde für die Dashboard-Grafiken |
| `GET` | `/api/clients` | ✓ | NTP-Client-IPs mit Anfrage-/Drop-Zählern (`chronyc clients`) |
| `GET` | `/api/access-log` | ✓ | Rollierendes Web/API-Zugriffs-Log (Zeit, IP, Methode, Pfad, Status) |
| `GET` | `/api/config` | ✓ | Server-Konfiguration lesen |
| `PUT` | `/api/config` | ✓ | Server-Konfiguration schreiben |
| `GET` | `/api/chrony-conf` | ✓ | chrony.conf als Rohtext |
| `PUT` | `/api/chrony-conf` | ✓ | chrony.conf direkt schreiben |
| `GET` | `/api/service/status` | ✓ | systemd-Service-Status |
| `POST` | `/api/service/restart` | ✓ | chrony neu starten |
| `GET` | `/api/cert/status` | ✓ | Status des ACME-Zertifikats (Domain, Aussteller, Ablauf) |
| `POST` | `/api/cert/issue` | ✓ | Zertifikat per ACME (HTTP-01) ausstellen |
| `POST` | `/api/cert/renew` | ✓ | Zertifikat erzwungen erneuern |

### Beispiel: Login + Status abfragen

```bash
# Login
TOKEN=$(curl -s -X POST http://server/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}' | jq -r .token)

# Status abfragen
curl -s http://server/api/status -H "X-Auth-Token: $TOKEN" | jq .
```

---

## Check_MK Integration

Das Local-Check-Script [`deploy/checkmk/chrony_webui_health`](deploy/checkmk/chrony_webui_health) auf dem Check_MK-Agenten-Host installieren:

```bash
cp deploy/checkmk/chrony_webui_health /usr/lib/check_mk_agent/local/
chmod +x /usr/lib/check_mk_agent/local/chrony_webui_health
```

**Konfiguration via Env-Variablen** (z. B. in `/etc/check_mk/agent.conf`):

```bash
CHRONYWEBUI_URL=http://ntp-server    # Standard: http://localhost:8080
CHRONYWEBUI_TIMEOUT=5                # Standard: 5 Sekunden
```

**Erzeugte Services:**

| Service | OK | WARN | CRIT |
|---|---|---|---|
| `chrony_webui_reachable` | API erreichbar | — | Timeout / Verbindungsfehler |
| `chrony_ntp_sync` | Stratum 1–7 | Stratum ≥ 8 | Nicht synchronisiert |
| `chrony_leap_status` | Normal | Leap-Sekunde aktiv | — |

Perfdata: `stratum`, `online_sources`

---

## Empfohlene chrony.conf

```
# /etc/chrony/chrony.conf

# Primäre interne NTP-Server (K+S)
server 192.0.2.35 iburst prefer
server 192.0.2.36 iburst

# Fallback: öffentliche NTP-Server (nur wenn interne nicht erreichbar)
server 0.pool.ntp.org iburst
server 1.pool.ntp.org iburst

# Drift-Datei
driftfile /var/lib/chrony/drift

# Schrittkorrektur beim Start (bis zu 1 Sekunde, max. 3 Mal)
makestep 1.0 3

# Hardware-Uhr synchronisieren
rtcsync

# Als NTP-Server für das interne Netz agieren
allow 10.0.0.0/8

# Logging
logdir /var/log/chrony
log tracking measurements statistics
```

---

## Zertifikat (ACME gegen interne step-CA)

Über den Tab **Konfiguration → Zertifikat** stellt die WebUI sich selbst ein TLS-Zertifikat
per ACME (HTTP-01) gegen die interne K+S step-CA aus — ohne den laufenden Nginx zu stoppen
(Webroot-Modus, `.well-known/acme-challenge` wird über die bestehende Website ausgeliefert).

**Voraussetzung:** `acme.sh` ist auf dem Server installiert und bei der internen CA registriert:

```bash
sudo bash Scripts/acme/01-setup-acme-client.sh \
  --ca-url https://dekdli047.corp.k-plus-s.net/acme/acme/directory
```

**Ablauf:**

1. Domain (CN) und optional SANs/E-Mail im Zertifikat-Tab eintragen
2. „Zertifikat anfordern" → acme.sh validiert per HTTP-01 über Nginx, Zertifikat landet in
   `CHRONYWEBUI_CERT_INSTALL_DIR` (Standard `/etc/ssl/chrony-webui`), Nginx wird per
   `CHRONYWEBUI_CERT_DEPLOY_RELOAD_COMMAND` neu geladen
3. In [`deploy/nginx.conf`](deploy/nginx.conf) den auskommentierten `443`-Server-Block aktivieren
   und `nginx -t && systemctl reload nginx`
4. „Jetzt erneuern" erzwingt eine Erneuerung; automatische Erneuerung siehe
   `Scripts/acme/03-renew-systemd.sh` (täglicher systemd-Timer, erneuert bei <30 Tagen Restlaufzeit)

Im Docker-Demo-Setup (`MOCK_CHRONY=true`) liefert der Tab Beispieldaten, ohne echte ACME-Requests.

---

## Sicherheitshinweise

- Das Admin-Passwort im Docker-Betrieb unter **Konfiguration → Konto** ändern oder in `docker-compose.yml` anpassen
- `CHRONYWEBUI_API_KEY` auf einen zufälligen Wert setzen: `openssl rand -hex 24`
- In Produktivumgebungen HTTPS via Nginx (Let's Encrypt / internes CA-Zertifikat) einrichten
- Das Backend (`localhost:8000`) **nicht** direkt exponieren — immer über Nginx
- Passwortänderungen im laufenden Betrieb gelten nur bis zum nächsten Neustart — für Persistenz `CHRONYWEBUI_ADMIN_PASSWORD` in der Env-Datei aktualisieren
