# 🔧 All-in-One Integration - Dokumentation

## Übersicht: Was ist die All-in-One Lösung?

Die **All-in-One Integration** für vcontrold ist eine echte End-to-End Lösung, die vcontrold **direkt in Home Assistant** startet und verwaltet:

```
┌─────────────────────────────────────────┐
│         Home Assistant 🏠               │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │    vcontrold Integration 🔧     │   │
│  │                                 │   │
│  │  ┌─────────────────────────┐   │   │
│  │  │  Daemon Manager         │   │   │
│  │  │  ├─ Auto-Start/Stop     │   │   │
│  │  │  ├─ Health Checks       │   │   │
│  │  │  └─ Process Management  │   │   │
│  │  └──────────┬──────────────┘   │   │
│  │             ↓                   │   │
│  │  ┌─────────────────────────┐   │   │
│  │  │  vcontrold Daemon 📡    │   │   │
│  │  │  (läuft in HA)          │   │   │
│  │  │  Port: 3002             │   │   │
│  │  └──────────┬──────────────┘   │   │
│  └─────────────┼──────────────────┘   │
│                ↓                       │
│        ┌───────────────┐              │
│        │ TCP Socket    │              │
│        │ localhost:3002│              │
│        └───────┬───────┘              │
└────────────────┼────────────────────┘
                 ↓
         ┌──────────────────┐
         │  vcontrold Config│
         └────────┬─────────┘
                  ↓
         ┌──────────────────┐
         │   Viessmann      │
         │   Heizungsanlage │
         │   (RS232)        │
         └──────────────────┘
```

## 🎯 Hauptmerkmale

### 1. Automatisches Daemon Management
- **Auto-Start**: Daemon startet automatisch beim HA-Start
- **Auto-Stop**: Daemon wird sauber beim HA-Stop gestoppt
- **Auto-Restart**: Bei Fehlern wird Daemon automatisch neu gestartet
- **Health Checks**: Regelmäßige TCP-Checks auf Daemon-Verfügbarkeit

### 2. Flexible Setup-Optionen
```
Wähle Konfigurationsmodus:
├─ 🔧 HA verwaltet (Default)     ← Empfohlen
│  └─ Daemon läuft in HA
│     Keine externe Installation
│
└─ 🌐 Externe vcontrold
   └─ Du verwaltest Daemon
      HA verbindet sich per TCP
```

### 3. Daemon Management Services
```yaml
# Service 1: Daemon starten
service: vcontrold.start_daemon
data:
  device: /dev/ttyUSB0

# Service 2: Daemon stoppen
service: vcontrold.stop_daemon

# Service 3: Status prüfen
service: vcontrold.check_status
```

## 📦 Installation der All-in-One

### Schritt 1: Integration kopieren
```bash
cp -r vcontrold ~/.homeassistant/custom_components/
```

### Schritt 2: Home Assistant neustarten
```bash
docker restart homeassistant
# oder
systemctl restart homeassistant
```

### Schritt 3: Config Flow durchlaufen
1. Settings → Devices & Services → Create Integration
2. Suche: `vcontrold`
3. Wähle: "🔧 HA verwaltet Daemon (All-in-One)"
4. Wähle Serielles Gerät: `/dev/ttyUSB0`
5. Konfiguriere Host/Port (default OK)
6. Fertig!

## 🔍 Daemon Manager Details

### Automatische Health Checks
```python
# Alle 60 Sekunden prüfen
if daemon_not_running:
    log("Daemon nicht aktiv - neu starten")
    start_daemon()
    health_check()
```

### Prozess Management
```python
# Auto-Start beim HA-Start
async def async_setup_entry():
    daemon_manager.start_daemon()
    
# Auto-Stop beim HA-Stop
async def async_unload_entry():
    daemon_manager.stop_daemon()
```

### Status Reporting
```python
daemon_status = {
    "running": True,
    "pid": 12345,
    "uptime_seconds": 3600,
    "health_checks": 42,
    "last_health_check": "2025-11-07T12:30:00",
    "config": {
        "device": "/dev/ttyUSB0",
        "host": "localhost",
        "port": 3002,
    }
}
```

## 🛠️ Services im Detail

### Service 1: set_temp_ww_soll
```yaml
service: vcontrold.set_temp_ww_soll
data:
  temperature: 55  # 20-80°C
```

### Service 2: set_betriebsart
```yaml
service: vcontrold.set_betriebsart
data:
  mode: auto  # auto, standby, party, eco
```

### Service 3: start_daemon (NEU)
```yaml
service: vcontrold.start_daemon
data:
  device: /dev/ttyUSB0  # Optional
```

### Service 4: stop_daemon (NEU)
```yaml
service: vcontrold.stop_daemon
```

### Service 5: check_status (NEU)
```yaml
service: vcontrold.check_status
# Zeigt detaillierten Status in Benachrichtigung
```

## 💻 Automationen mit Daemon Management

### Beispiel 1: Daemon täglich neu starten
```yaml
automation:
  - id: daily_daemon_restart
    alias: "Täglicher Daemon-Restart"
    trigger:
      at: "04:00:00"
      platform: time
    action:
      - service: vcontrold.stop_daemon
      - delay: "00:00:05"
      - service: vcontrold.start_daemon
```

### Beispiel 2: Status-Check alle 30 Minuten
```yaml
automation:
  - id: daemon_health_check
    alias: "Daemon Health Check"
    trigger:
      minutes: 30
      platform: time_pattern
    action:
      - service: vcontrold.check_status
```

### Beispiel 3: Benachrichtigung bei Fehler
```yaml
automation:
  - id: daemon_error_alert
    alias: "Daemon Error Alert"
    trigger:
      platform: state
      entity_id: sensor.kesseltemperatur
      state: "unknown"
    action:
      - service: notify.mobile_app_iphone
        data:
          title: "⚠️ vcontrold Fehler"
          message: "Daemon antwortet nicht - versuche Neustart"
      - service: vcontrold.start_daemon
```

## 🔧 Fehlerbehandlung

### Problem: Daemon startet nicht
```bash
# 1. Logs prüfen
docker logs homeassistant | grep vcontrold

# 2. Binary prüfen
ls -la ~/.homeassistant/vcontrold_daemon/

# 3. Berechtigungen prüfen
chmod +x ~/.homeassistant/vcontrold_daemon/vcontrold_linux

# 4. Serielles Gerät prüfen
ls -la /dev/ttyUSB*
```

### Problem: Timeout-Fehler
```yaml
# Erhöhe Update-Intervall in Sensor Coordinator:
# (standardmäßig 60 Sekunden)
```

### Problem: Health Check schlägt fehl
```python
# Prüfung:
echo "ping" | nc localhost 3002
# Sollte antworten: OK
```

## 📊 Performance-Tipps

1. **Update-Intervall**: Standard 60s ist gut für meisten Fälle
2. **Caching**: 30s TTL reduziert TCP-Last
3. **Health Checks**: Auto-aktiviert, minimal Overhead
4. **Logging**: DEBUG-Level nur bei Problemen

## 🔐 Sicherheit

### Lokal
- ✅ Kein Cloud-Upload
- ✅ Keine Authentifizierung erforderlich
- ✅ Nur localhost:3002 (standardmäßig)

### Firewall
```bash
# Port 3002 nur lokal erlauben:
sudo ufw allow from 127.0.0.1 to 127.0.0.1 port 3002

# Oder SSH-Tunnel für Remote:
ssh -L 3002:localhost:3002 user@ha-server
```

## 🚀 Migration von alt → All-in-One

Wenn du bereits die alte externe vcontrold nutzt:

1. **Alte Integration deinstallieren** (falls separate Installation)
2. **Neue All-in-One Integration installieren**
3. **Config Flow durchlaufen** - wähle "HA verwaltet"
4. **Sensoren sollten automatisch laden**

Das wars! 🎉

## 📝 Zusammenfassung

| Feature | Status |
|---------|--------|
| Auto-Start/Stop | ✅ |
| Health Checks | ✅ |
| Prozess Management | ✅ |
| Service Calls | ✅ |
| Daemon Control Services | ✅ |
| Config Flow | ✅ |
| Hybrid Mode (extern) | ✅ |
| Logging | ✅ |

---

**Das ist die wahre All-in-One Lösung! 🎉**
