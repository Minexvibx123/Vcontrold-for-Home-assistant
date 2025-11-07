# 🎯 Vcontrold Home Assistant Integration - Complete Guide

## 📖 Table of Contents

1. [Quick Start](#quick-start) - 5 Minuten bis zur Funktion
2. [Detailed Setup](#detailed-setup) - Schritt-für-Schritt Installation
3. [Configuration Guide](#configuration-guide) - Alle Einstellungen erklärt
4. [GUI Tutorial](#gui-tutorial) - WebUI Setup erklärt
5. [Features & Usage](#features--usage) - Was kann man damit machen?
6. [Advanced Topics](#advanced-topics) - Für Power User
7. [Troubleshooting](#troubleshooting) - Problem? Hier ist die Lösung
8. [FAQ](#faq) - Häufig gestellte Fragen

---

## ⚡ Quick Start

### Für Ungeduld (5 Min)

#### Schritt 1: Integration installieren
```bash
# SSH in Home Assistant
docker exec -it homeassistant bash

# Kopiere Integration in custom_components
cp -r vcontrold /config/custom_components/
```

#### Schritt 2: Home Assistant neustarten
```
Einstellungen → System → Restart Home Assistant
```

#### Schritt 3: Integration hinzufügen
```
Einstellungen → Devices & Services
→ "Create Automation" ODER "Integrations"
→ "vcontrold" suchen und klicken
→ Setup-Assistent folgen (1 Min)
```

#### Schritt 4: Sensoren verwenden
```
Einstellungen → Devices & Services
→ "vcontrold" 
→ 5 neue Sensoren verfügbar!
```

### ✅ Fertig! Du hast:
- ✅ 5 Temperatur-Sensoren
- ✅ 2 Control-Services
- ✅ Auto-Update (60s Interval)
- ✅ Dashboard-Integration

---

## 🔧 Detailed Setup

### Voraussetzungen

#### Hardware
- [ ] Viessmann Heizung mit vcontrold Unterstützung
- [ ] USB-RS232 Adapter (oder serieller Port)
- [ ] Home Assistant Installation
- [ ] Netzwerk-Zugriff auf HA (lokal oder via SSH-Tunnel)

#### Software
- [ ] Home Assistant 2024.1.0 oder neuer
- [ ] Python 3.8+
- [ ] git (für Updates)

#### Netzwerk
- [ ] Lokal (HA + Heizung im selben Netz)
- [ ] oder Remote (SSH-Tunnel - siehe unten)

### Installation - Mehrere Optionen

#### Option A: Manuell über SFTP (Anfänger)

```bash
1. Öffne SFTP-Client (z.B. FileZilla)
2. Verbindung zu Home Assistant:
   Host: <HA-IP-Adresse>
   Port: 22
   Benutzername: root
   Passwort: <HA-Passwort>

3. Navigiere zu: /config/custom_components/
4. Laden Sie den "vcontrold" Ordner hoch
5. Home Assistant neustarten
```

#### Option B: SSH & Terminal (Fortgeschrittene)

```bash
# SSH in HA (über Web Terminal in HA)
ssh root@<HA-IP>

# Navigiere zum Ordner
cd /config/custom_components/

# Clone Repository
git clone https://github.com/Minexvibx123/Vcontrold-for-Home-assistant.git
mv Vcontrold-for-Home-assistant/vcontrold .
rm -rf Vcontrold-for-Home-assistant

# Fertig!
```

#### Option C: Docker-Compose (Docker User)

```yaml
# docker-compose.yml
volumes:
  - ./custom_components:/config/custom_components

# Statt manuell zu kopieren:
# - Mountpoint verwenden
# - custom_components/vcontrold/ hineinlegen
# - Container neustarten
```

### Installation verifizieren

```bash
# Check Installation
ls -la /config/custom_components/vcontrold/

# Sollte folgende Dateien enthalten:
# ✅ __init__.py
# ✅ sensor.py
# ✅ vcontrold_manager.py
# ✅ config_flow.py
# ✅ manifest.json
# ✅ services.yaml
# ✅ strings.json
```

### Home Assistant Neustart

```
Im Web-Interface:
1. Einstellungen → System
2. "Restart Home Assistant" klicken
3. Warten (2-3 Minuten)
4. Browser neuladen (F5)
```

---

## ⚙️ Configuration Guide

### Setup-Assistent (empfohlen)

```
Einstellungen → Devices & Services 
→ "Integrations" Tab
→ "Create Integration" Button
→ "vcontrold" suchen
→ Assistent starten
```

#### Schritt 1: Setup-Modus wählen

```
🔧 All-in-One (HA verwaltet Daemon)  ← STANDARD
   Vorteile:
   ✅ Automatisches Starten/Stoppen
   ✅ Einfache Installation
   ✅ Health Checks integriert
   
   Nachteile:
   ❌ vcontrold benötigt binäre Abhängigkeiten
   ❌ Mehr RAM-Verbrauch

🌐 Hybrid (externe vcontrold)
   Vorteile:
   ✅ Leichtgewichtig
   ✅ vcontrold läuft separat
   
   Nachteile:
   ❌ Manuelle Verwaltung
   ❌ Mehr Konfiguration
```

#### Schritt 2a: Gerät (für All-in-One)

```
Wähle USB-Gerät:
📋 /dev/ttyUSB0 (USB Adapter) ← Meist hier
📋 /dev/ttyACM0 (Arduino-style)
📋 /dev/ttyS0 (serieller Port)
📋 Eigene eingeben...

Wie finde ich mein Gerät?
→ Terminal: ls -la /dev/tty*
→ Home Assistant Terminal Add-on verwenden
```

#### Schritt 2b: Netzwerk (für All-in-One)

```
Host (Standard: localhost)
├─ localhost    ← Lokal (100% sicher)
├─ 127.0.0.1    ← Loopback
└─ 0.0.0.0      ← Alle Interfaces

Port (Standard: 3002)
├─ Range: 1024-65535
├─ Test: nc -zv localhost 3002
└─ Beliebt: 3002, 3003, 8000
```

#### Schritt 2c: Erweitert

```
Update-Intervall (Sekunden)
├─ Min: 30s (schnell, aber mehr Last)
├─ Default: 60s (Empfohlen)
└─ Max: 300s (5 Min, sparsam)

Log-Level
├─ ERROR (Nur Fehler)      ← Produktion
├─ WARN (Warnungen)
├─ INFO (Informationen)    ← Debug
└─ DEBUG (Alles)           ← Intensives Debug

Protokoll
├─ KW (Komfortsignal - Standard)  ← 99% der Fälle
├─ Raw (Binär)
└─ Framing (Spezial)
```

#### Schritt 3: Speichern

```
Klick "SUBMIT"
   ↓
Integration wird geladen
   ↓
5 Sensoren erscheinen
   ↓
Fertig! ✅
```

---

## 🎨 GUI Tutorial

### Erste Konfiguration (Assistent)

Siehe: [GUI_DOCUMENTATION.md](GUI_DOCUMENTATION.md)

#### Screenshot-Beschreibung: Schritt 1

```
┌─────────────────────────────────────┐
│  vcontrold Integration - Schritt 1/3 │
├─────────────────────────────────────┤
│                                     │
│  Wähle Setup-Modus:                 │
│  ○ 🔧 HA verwaltet (All-in-One)     │
│  ● 🌐 Externe vcontrold             │
│                                     │
│  [ZURÜCK]  [WEITER]                 │
└─────────────────────────────────────┘
```

### Nachträgliche Änderungen (Settings)

#### Pfad

```
Einstellungen 
  → Devices & Services
    → "Integrations" Tab
      → "vcontrold" klicken
        → Zahnrad-Icon oder "Configure"
          → Settings-Dialog
            → Änderung vornehmen
              → "SUBMIT"
                → ✅ Sofort aktiv!
```

#### Änderbare Einstellungen (ohne Neustart!)

```
🔧 Update-Intervall
   30-300s
   
🔧 Log-Level
   ERROR/WARN/INFO/DEBUG
   
🔧 Host (nur All-in-One)
   localhost/127.0.0.1/custom
   
🔧 Port (nur All-in-One)
   1024-65535
```

---

## 🚀 Features & Usage

### Verfügbare Sensoren

```yaml
sensor.vcontrold_kesseltemperatur
  unit_of_measurement: "°C"
  value: 45.3
  friendly_name: "Kesseltemperatur"

sensor.vcontrold_aussentemperatur
  unit_of_measurement: "°C"
  value: 12.5
  friendly_name: "Außentemperatur"

sensor.vcontrold_warmwasser_soll
  unit_of_measurement: "°C"
  value: 55.0
  friendly_name: "Warmwasser Soll"

sensor.vcontrold_warmwasser_ist
  unit_of_measurement: "°C"
  value: 54.8
  friendly_name: "Warmwasser Ist"

sensor.vcontrold_vorlauf_hk1
  unit_of_measurement: "°C"
  value: 38.2
  friendly_name: "Vorlauf Heizkreis 1"
```

### Verfügbare Services

#### Service 1: Warmwasser-Solltemperatur setzen

```yaml
service: vcontrold.set_temp_ww_soll
data:
  temperature: 60  # Celsius (20-80)
```

#### Service 2: Betriebsart ändern

```yaml
service: vcontrold.set_betriebsart
data:
  mode: "auto"  # auto|standby|party|eco
```

#### Service 3: Daemon starten (optional)

```yaml
service: vcontrold.start_daemon
```

#### Service 4: Daemon stoppen (optional)

```yaml
service: vcontrold.stop_daemon
```

#### Service 5: Status prüfen (optional)

```yaml
service: vcontrold.check_status
```

### Automation Beispiel

#### Beispiel 1: Nachtmodus aktivieren

```yaml
automation:
  - alias: Nachtmodus - Temperatur senken
    trigger:
      platform: time
      at: "22:00:00"
    action:
      service: vcontrold.set_temp_ww_soll
      data:
        temperature: 45
```

#### Beispiel 2: Bei Sonnenaufgang aufheizen

```yaml
automation:
  - alias: Morgens aufheizen
    trigger:
      platform: sun
      event: sunrise
    action:
      service: vcontrold.set_betriebsart
      data:
        mode: "auto"
```

#### Beispiel 3: Temperatur-Alarm

```yaml
automation:
  - alias: "Alarm: Heizung zu heiß"
    trigger:
      platform: numeric_state
      entity_id: sensor.vcontrold_kesseltemperatur
      above: 80
    action:
      service: notify.notify
      data:
        message: "⚠️ Kesseltemperatur: {{ states('sensor.vcontrold_kesseltemperatur') }}°C"
```

### Dashboard Beispiel

```yaml
# configuration.yaml
homeassistant:
  customize:
    sensor.vcontrold_kesseltemperatur:
      friendly_name: "🔥 Kessel"
    sensor.vcontrold_aussentemperatur:
      friendly_name: "❄️ Außen"
    sensor.vcontrold_warmwasser_soll:
      friendly_name: "💧 WW Soll"
```

#### Dashboard Card (YAML)

```yaml
type: vertical-stack
cards:
  - type: heading
    heading: "Heizungssteuerung"
    
  - type: grid
    cards:
      - type: gauge
        entity: sensor.vcontrold_kesseltemperatur
        min: 0
        max: 80
        
      - type: gauge
        entity: sensor.vcontrold_aussentemperatur
        min: -20
        max: 40
        
      - type: gauge
        entity: sensor.vcontrold_warmwasser_ist
        min: 0
        max: 80
        
  - type: entities
    entities:
      - entity: sensor.vcontrold_warmwasser_soll
      - entity: sensor.vcontrold_vorlauf_hk1
      
  - type: horizontal-stack
    cards:
      - type: custom:button-card
        entity: switch.heizung_auto
        tap_action:
          action: call-service
          service: vcontrold.set_betriebsart
          service_data:
            mode: "auto"
            
      - type: custom:button-card
        entity: switch.heizung_eco
        tap_action:
          action: call-service
          service: vcontrold.set_betriebsart
          service_data:
            mode: "eco"
```

---

## 🎓 Advanced Topics

### Remote Setup (SSH-Tunnel)

#### Problem: Heizung ist nicht lokal

```
Home Assistant (HA-Server)     Heizung (Remote)
        ↓ (kein direkter Zugriff)
        ❌ Cannot connect
```

#### Lösung: SSH-Tunnel

```bash
# Auf dem HA-Server/Gerät mit vcontrold:
# Tunnel zu Heizungsgerät öffnen

ssh -L 3002:192.168.1.50:3002 user@heizung-server

# Dann in HA verwenden:
# Host: localhost
# Port: 3002

# Tunnel bleibt bestehen → Verbindung funktioniert
```

#### Automatischer Tunnel (systemd)

```ini
# /etc/systemd/system/vcontrold-tunnel.service
[Unit]
Description=vcontrold SSH Tunnel
After=network.target

[Service]
Type=simple
User=ha
ExecStart=/usr/bin/ssh -N -L 3002:192.168.1.50:3002 user@heizung-server
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Custom Befehl hinzufügen

#### Erweiterung: Neuer Sensor

```python
# vcontrold/sensor.py - Sensor hinzufügen

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    
    # Neuer Sensor
    entities = [
        VcontroledTemperatureSensor(
            coordinator, 
            "heizkreis_solltemperatur",  # Neuer Befehl
            "Heizkreis Solltemperatur"
        ),
    ]
    
    async_add_entities(entities)
```

### Debugging & Logging

#### Debug-Modus aktivieren

```yaml
# configuration.yaml
logger:
  default: info
  logs:
    custom_components.vcontrold: debug
```

#### Logs prüfen

```bash
# SSH Terminal
tail -f /config/home-assistant.log | grep vcontrold

# Oder im Web-Interface:
Einstellungen → System → Logs
  → Suchfeld: "vcontrold"
```

#### Häufige Debug-Ausgaben

```
DEBUG (MainThread) [custom_components.vcontrold] Connection successful
  → ✅ TCP-Verbindung OK

DEBUG (MainThread) [custom_components.vcontrold] Sensor updated: 45.3°C
  → ✅ Daten empfangen

ERROR (MainThread) [custom_components.vcontrold] Connection timeout
  → ❌ Problem: TCP hängt fest
```

---

## 🔧 Troubleshooting

### Problem 1: Integration wird nicht geladen

```
❌ Integration not found
❌ AttributeError: module has no attribute 'CONFIG_SCHEMA'
```

**Ursache:** Falsche Installation oder Syntax-Fehler

**Lösung:**
```bash
# 1. Überprüfe Ordner-Struktur
ls -la /config/custom_components/vcontrold/
# Sollte __init__.py, sensor.py, etc. enthalten

# 2. Prüfe Syntax
python3 -m py_compile /config/custom_components/vcontrold/*.py

# 3. Home Assistant neu starten
# Einstellungen → System → Restart
```

### Problem 2: "Cannot connect" Fehler

```
❌ Cannot connect to vcontrold
❌ Connection refused on port 3002
```

**Ursache:** vcontrold läuft nicht oder Port ist falsch

**Lösung:**
```bash
# 1. Prüfe ob vcontrold läuft
ps aux | grep vcontrold

# 2. Prüfe Port
nc -zv localhost 3002

# 3. Prüfe Daemon Manager Logs
# Einstellungen → System → Logs
# Suche: "daemon_manager"

# 4. Starte manuell
docker exec homeassistant /config/vcontrold/vcontrold -f /config/vcontrold/vcontrold.conf
```

### Problem 3: Sensoren zeigen "unavailable"

```
❌ sensor.vcontrold_kesseltemperatur: unavailable
```

**Ursache:** Keine Daten vom Daemon empfangen

**Lösung:**
```bash
# 1. Prüfe Verbindung zum Daemon
python3 -c "
import socket
s = socket.socket()
s.settimeout(5)
try:
    s.connect(('localhost', 3002))
    print('✅ Connected')
    s.close()
except:
    print('❌ Cannot connect')
"

# 2. Prüfe Serial Device (für All-in-One)
ls -la /dev/ttyUSB* /dev/ttyACM*

# 3. Starte Integration neu
# Einstellungen → Devices & Services
# vcontrold → Menü → Reload
```

### Problem 4: Update-Fehler nach neuem Log-Level

```
❌ Service update_entity failed
```

**Ursache:** Falsche Konfiguration

**Lösung:**
```bash
# 1. Prüfe config_flow Fehler
grep "config_flow" /config/home-assistant.log | tail -20

# 2. Prüfe Einstellungen (settings)
cat /config/.storage/core.config_entries | grep vcontrold

# 3. Stelle Standardwerte wieder her
# Delete und neu hinzufügen:
# Einstellungen → Devices & Services
# vcontrold → Menü → Delete
# Dann neu hinzufügen
```

Weitere Fehler siehe: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## ❓ FAQ

### F: Brauche ich vcontrold extern zu installieren?

**A:** Nein! Mit All-in-One wird es automatisch von HA gemanagt.
- All-in-One: HA startet vcontrold selbst ✅
- Hybrid: Du brauchst externe vcontrold Installation

### F: Welcher Mode ist besser?

**A:** 
- **All-in-One (Standard)**: Einfacher, weniger Konfiguration ✅
- **Hybrid (Extern)**: Wenn vcontrold separat läuft (z.B. auf NAS)

### F: Kann ich den Port ändern?

**A:** Ja, im Setup-Assistent oder nachträglich:
```
Einstellungen → Devices & Services
→ vcontrold → Configure
→ Port ändern → Submit
```

### F: Wie oft werden Sensoren aktualisiert?

**A:** Standard 60 Sekunden (änderbar):
- Min: 30s (schneller, mehr CPU-Last)
- Max: 300s (sparsam, aber träger)

### F: Kann ich mehrere Heizungen ansteuern?

**A:** Aktuell nicht (nur eine Integration pro HA).
Geplant: Multi-Instance Support in v3.0

### F: Funktioniert das auch remote (über Internet)?

**A:** Nur lokal sicher. Für Remote: SSH-Tunnel verwenden.
```bash
ssh -L 3002:192.168.1.50:3002 user@server
```

### F: Was sind die Sensoren?

**A:** 5 Temperature-Sensoren:
1. Kesseltemperatur (Status)
2. Außentemperatur (Wetter)
3. Warmwasser Soll (Einstellung)
4. Warmwasser Ist (Status)
5. Vorlauf HK1 (Status)

### F: Wie setze ich Automation auf?

**A:** Beispiele siehe: [README.md](README.md) oder [automations.example.yaml](automations.example.yaml)

### F: Gibt es ein Dashboard Template?

**A:** Beispiel siehe: [README.md - Dashboard Setup](README.md#dashboard-setup)

### F: Kann ich die GUI übersetzen?

**A:** Ja! Bearbeite: `translations/en.json` + `strings.json`

### F: Was ist wenn es nicht funktioniert?

**A:** 
1. Siehe: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Prüfe Logs: Einstellungen → System → Logs
3. Debug-Modus: Log-Level auf DEBUG
4. Öffne Issue auf GitHub

---

## 📚 Weitere Dokumente

- 📖 [README.md](README.md) - Hauptdokumentation
- ⚡ [QUICKSTART.md](QUICKSTART.md) - 5 Min Setup
- 📦 [INSTALL.md](INSTALL.md) - Detaillierte Installation
- 🔧 [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Fehlersuche
- 🏗️ [ARCHITECTURE.md](ARCHITECTURE.md) - Technische Details
- 🎨 [GUI_DOCUMENTATION.md](GUI_DOCUMENTATION.md) - WebUI Guide
- 🔄 [ALL_IN_ONE_DOCS.md](ALL_IN_ONE_DOCS.md) - All-in-One Features
- 🎉 [PROJECT_COMPLETION.md](PROJECT_COMPLETION.md) - Projekt-Status

---

## 🆘 Support

- 📌 Issues: https://github.com/Minexvibx123/Vcontrold-for-Home-assistant/issues
- 💬 Discussions: https://github.com/Minexvibx123/Vcontrold-for-Home-assistant/discussions
- 📝 Home Assistant Docs: https://www.home-assistant.io/

---

## 🎯 Nächste Schritte

1. ✅ Installation abgeschlossen
2. ✅ Setup-Assistent durchlaufen
3. ✅ Sensoren verwenden
4. 📖 Automations-Beispiele ausprobieren
5. 🎨 Dashboard erstellen
6. 🚀 Custom Automations schreiben

**Viel Spaß mit deiner Heizungssteuerung!** 🔥❄️

---

*Letzte Aktualisierung: 2024 | vcontrold Integration v2.0.0+*
