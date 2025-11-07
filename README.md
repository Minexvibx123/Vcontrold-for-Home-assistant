# Vcontrold-for-Home-Assistant

Custom Home Assistant Integration für die Viessmann-Heizungssteuerung mit lokalem **vcontrold** Daemon.

Diese Integration ermöglicht es dir, deine Viessmann-Heizung über Home Assistant zu überwachen und zu steuern - **ohne Cloud** und **ohne ViCare**!

## 🎯 Features

- ✅ **TCP-Socket Kommunikation** mit vcontrold Daemon
- ✅ **Automatische Datenabfrage** (konfigurierbar, Standard: 60 Sekunden)
- ✅ **Caching-Mechanismus** zur Reduktion von Socket-Anfragen
- ✅ **5 Temperatur-Sensoren** für umfassende Überwachung
- ✅ **Service-Aufrufe** zum Steuern der Heizung
- ✅ **Robuste Fehlerbehandlung** mit Timeout-Erkennung
- ✅ **Mehrsprachig** (Deutsch & Englisch)
- ✅ **Lokale Verarbeitung** - keine Cloud-Abhängigkeit
- ✅ **🆕 Integrierte Daemon-Verwaltung** - vcontrold kann direkt in HA starten
- ✅ **🆕 Non-Docker Support** - systemd, native Installation

## 📋 Voraussetzungen

### Home Assistant
- **Home Assistant** (mindestens Version 2024.1.0)
- Läuft nativ auf Linux/macOS/Windows oder im Docker

### vcontrold Daemon

**Option 1: Integriert (Empfohlen)**
- vcontrold Binary im Integration Verzeichnis
- Wird automatisch von Home Assistant gestartet/gestoppt
- Keine separate Installation notwendig

**Option 2: Extern**
- vcontrold läuft separat auf dem Netzwerk
- Standard-Port: `localhost:3002`
- Host und Port konfigurierbar

### Hardware
- **Viessmann Heizungsanlage** mit vcontrold Unterstützung
- **USB-Seriengerät** oder Netzwerkzugang zur Heizung

## 🔧 Installation

### 🆕 Installation für Non-Docker (Direktes System)

Falls Home Assistant **nicht** in Docker läuft, sondern nativ auf dem System:

#### 1. vcontrold Daemon installieren

```bash
# Debian/Ubuntu
sudo apt-get install vcontrold

# Oder von Source
git clone https://github.com/openv/vcontrold.git
cd vcontrold
./configure
make
sudo make install
```

#### 2. vcontrold Konfigurieren

```bash
# Konfigurationsdatei erstellen
sudo nano /etc/vcontrold/vcontrold.conf
```

Beispielkonfiguration:
```conf
# vcontrold Konfiguration
listen localhost 3002
device /dev/ttyUSB0
```

#### 3. vcontrold als systemd Service starten

```bash
# Service-Datei
sudo systemctl start vcontrold
sudo systemctl enable vcontrold

# Status prüfen
sudo systemctl status vcontrold
```

#### 4. Verbindung testen

```bash
# Verbindung zu vcontrold testen
telnet localhost 3002
```

### Integration herunterladen

Klone oder lade das Repository herunter:

```bash
git clone https://github.com/Minexvibx123/Vcontrold-for-Home-assistant.git
```

### 2. Integration in Home Assistant einbinden

Kopiere den `vcontrold`-Ordner in dein Home Assistant Konfigurationsverzeichnis:

```bash
# Bei Standard HA User Installation
sudo cp -r vcontrold /home/homeassistant/.homeassistant/custom_components/

# Oder bei venv Installation
source /path/to/venv/bin/activate
cp -r vcontrold ~/.homeassistant/custom_components/
```

Die finale Struktur muss so aussehen:
```
~/.homeassistant/
├── custom_components/
│   └── vcontrold/               ← Der vcontrold Ordner
│       ├── __init__.py
│       ├── manifest.json
│       ├── config_flow.py
│       ├── const.py
│       ├── sensor.py
│       ├── daemon_manager.py     ← 🆕 Daemon-Verwaltung
│       ├── vcontrold_manager.py
│       ├── services.yaml
│       ├── strings.json
│       └── translations/
│           └── en.json
├── configuration.yaml
└── [weitere Dateien]
```

### 3. Home Assistant neu starten

```bash
# Systemd Service
sudo systemctl restart homeassistant

# Oder manuell
docker restart homeassistant
```

### 4. Integration konfigurieren

#### Variante 1: WebUI (empfohlen) ⭐

1. Öffne Home Assistant WebUI: `http://<IP>:8123`
2. Gehe zu: **Settings → Devices & Services**
3. Klick: **Create Integration**
4. Suche: **vcontrold**
5. Fülle aus:
   - **Host**: `localhost` (oder IP-Adresse)
   - **Port**: `3002`
   - **Update Interval**: `60` (Sekunden)
   - **🆕 Daemon Enabled**: `true/false` (Daemon-Verwaltung durch HA)
   - **🆕 Daemon Device**: `/dev/ttyUSB0` (Serielles Gerät)
   - **🆕 Daemon Log Level**: `ERROR` (Logging-Level)
6. Klick: **Create**

Integration ist erstellt und Sensoren sind verfügbar! ✅

#### Variante 2: YAML (Alternative)

Füge folgende Zeilen in die `configuration.yaml` ein:

```yaml
vcontrold:
  host: localhost
  port: 3002
  update_interval: 60
```

Mit Daemon-Verwaltung:
```yaml
vcontrold:
  host: localhost
  port: 3002
  update_interval: 60
  daemon_enabled: true          # 🆕 HA verwaltet den Daemon
  daemon_device: /dev/ttyUSB0   # 🆕 Serielles Gerät
  daemon_log_level: ERROR       # 🆕 Logging-Level
```

Nach Änderungen Home Assistant neu laden:
- WebUI: Developer Tools → Restart
- Terminal: `systemctl restart homeassistant`

#### Optionen:

| Option | Typ | Standard | Beschreibung |
|--------|-----|----------|-------------|
| `host` | string | `localhost` | IP oder Hostname des vcontrold Daemons |
| `port` | int | `3002` | Port des vcontrold Daemons |
| `update_interval` | int | `60` | Update-Intervall in Sekunden |
| `daemon_enabled` | bool | `true` | 🆕 Home Assistant verwaltet Daemon |
| `daemon_device` | string | `/dev/ttyUSB0` | 🆕 Serielles Gerät für Daemon |
| `daemon_log_level` | string | `ERROR` | 🆕 Daemon Log Level (ERROR, WARN, INFO, DEBUG) |

Beispiel mit Remote-Host:

```yaml
vcontrold:
  host: 192.168.1.100
  port: 3002
  update_interval: 60
  daemon_enabled: false  # Daemon läuft extern
```

### 5. Home Assistant neu laden

Nach der Konfiguration muss Home Assistant neu geladen werden:

- **Über WebUI**: Developer Tools → Restart
- **Via Terminal**: `systemctl restart homeassistant`

## 📊 Verfügbare Sensoren

Nach erfolgreicher Installation findest du folgende Sensoren:

| Sensor | Entity ID | Wert | Einheit |
|--------|-----------|------|--------|
| Kesseltemperatur | `sensor.kesseltemperatur` | Aktuelle Kesseltemperatur | °C |
| Außentemperatur | `sensor.aussentemperatur` | Außenlufttemperatur | °C |
| Warmwasser-Solltemperatur | `sensor.warmwasser_solltemperatur` | Zieltemperatur Warmwasser | °C |
| Warmwasser-Isttemperatur | `sensor.warmwasser_isttemperatur` | Aktuelle Warmwassertemperatur | °C |
| Heizkreis Vorlauftemperatur | `sensor.heizkreis_vorlauftemperatur` | Vorlauftemperatur Heizkreis 1 | °C |

## 🎮 Services

### Service: `vcontrold.set_temp_ww_soll`

Setze die Warmwasser-Solltemperatur.

**Parameter:**
- `temperature` (erforderlich): Zieltemperatur (20-80°C)

**Beispiel (YAML):**

```yaml
service: vcontrold.set_temp_ww_soll
data:
  temperature: 55
```

**Beispiel (Python Template):**

```jinja2
service: vcontrold.set_temp_ww_soll
data:
  temperature: "{{ states('input_number.warmwasser_ziel') | float }}"
```

### Service: `vcontrold.set_betriebsart`

Ändere die Betriebsart der Heizung.

**Parameter:**
- `mode` (erforderlich): Betriebsart
  - `auto` - Automatischer Modus
  - `standby` - Standby-Modus
  - `party` - Party-Modus (erhöhte Temperatur kurzzeitig)
  - `eco` - Eco-Modus (reduzierte Temperatur)

**Beispiel (YAML):**

```yaml
service: vcontrold.set_betriebsart
data:
  mode: auto
```

## 📱 Home Assistant Automation Beispiele

### Beispiel 1: Warmwasser bei Sonnenaufgang aktivieren

```yaml
automation:
  - id: warmwasser_sonnenaufgang
    alias: "Warmwasser bei Sonnenaufgang"
    trigger:
      platform: sun
      event: sunrise
    action:
      service: vcontrold.set_temp_ww_soll
      data:
        temperature: 60
```

### Beispiel 2: Eco-Modus nachts

```yaml
automation:
  - id: eco_modus_nacht
    alias: "Eco-Modus nachts"
    trigger:
      platform: time
      at: "22:00:00"
    action:
      service: vcontrold.set_betriebsart
      data:
        mode: eco
  
  - id: auto_modus_morgen
    alias: "Auto-Modus morgens"
    trigger:
      platform: time
      at: "06:00:00"
    action:
      service: vcontrold.set_betriebsart
      data:
        mode: auto
```

### Beispiel 3: Dynamische Warmwasser-Temperatur

```yaml
automation:
  - id: warmwasser_temperatur_dynamisch
    alias: "Warmwasser-Temperatur anpassen"
    trigger:
      platform: state
      entity_id: sensor.aussentemperatur
    action:
      choose:
        - conditions:
            - condition: numeric_state
              entity_id: sensor.aussentemperatur
              below: 5
          sequence:
            - service: vcontrold.set_temp_ww_soll
              data:
                temperature: 65
        - conditions:
            - condition: numeric_state
              entity_id: sensor.aussentemperatur
              below: 15
          sequence:
            - service: vcontrold.set_temp_ww_soll
              data:
                temperature: 60
        - default:
            - service: vcontrold.set_temp_ww_soll
              data:
                temperature: 55
```

## 🔍 Dashboard Setup (Lovelace)

Erstelle eine schöne Übersicht im Home Assistant Dashboard:

```yaml
type: vertical-stack
cards:
  - type: entities
    title: Viessmann Heizung
    entities:
      - sensor.kesseltemperatur
      - sensor.aussentemperatur
      - sensor.warmwasser_solltemperatur
      - sensor.warmwasser_isttemperatur
      - sensor.heizkreis_vorlauftemperatur

  - type: custom:button-card
    template: button_large_command_row
    entity: automation.warmwasser_sonnenaufgang
    name: Warmwasser
    tap_action:
      action: call-service
      service: vcontrold.set_temp_ww_soll
      service_data:
        temperature: 60

  - type: custom:button-card
    template: button_large_command_row
    entity: automation.eco_modus_nacht
    name: Betriebsart
    tap_action:
      action: call-service
      service: vcontrold.set_betriebsart
      service_data:
        mode: auto
```

## 🐛 Fehlerbehandlung

### vcontrold nicht erreichbar

**Problem:** Integration startet nicht, Fehler: "vcontrold nicht erreichbar"

**Lösungen:**
1. Prüfe, ob vcontrold läuft: `systemctl status vcontrold` oder `docker ps | grep vcontrold`
2. Prüfe Netzwerkkonnektivität: `telnet localhost 3002`
3. Prüfe die Konfiguration (Host, Port)
4. Schau die Home Assistant Logs an: `docker logs homeassistant | grep vcontrold`

### Timeout-Fehler

**Problem:** Regelmäßige Timeouts beim Abfragen der Sensoren

**Lösungen:**
1. Erhöhe das Update-Intervall in der Konfiguration
2. Prüfe die Netzwerkqualität
3. Stelle sicher, dass vcontrold nicht überlastet ist
4. Schau die vcontrold Logs an

### Sensoren zeigen `unknown`

**Problem:** Sensoren sind unbekannt oder zeigen keine Werte

**Lösungen:**
1. Prüfe, ob die Integration aktiv ist (DevTools → States)
2. Schau die Home Assistant Logs (Level: DEBUG)
3. Prüfe die vcontrold-Konfiguration
4. Starte Home Assistant neu

## 📝 Logging

Für erweiterte Fehlerdiagnose kannst du das Logging auf DEBUG-Ebene erhöhen:

```yaml
logger:
  logs:
    custom_components.vcontrold: debug
```

Logs anschauen:

```bash
docker logs -f homeassistant | grep vcontrold
```

## 🏗️ Projektstruktur

```
custom_components/vcontrold/
├── __init__.py              # Integration Entry Point
├── manifest.json            # Integration Metadaten
├── sensor.py                # Sensor Entities & Coordinator
├── services.yaml            # Service-Definitionen
├── vcontrold_manager.py     # TCP-Socket Manager
├── strings.json             # Deutsche Strings
└── translations/
    └── en.json              # Englische Translations
```

## 🔐 Sicherheit

- **Lokale Kommunikation**: Alle Daten bleiben lokal auf dem Netzwerk
- **Keine Cloud**: Keine externe Abhängigkeit
- **Firewall**: Stelle sicher, dass Port 3002 nur lokal zugänglich ist
- **Encryption**: Optional: nutze SSH-Tunneling für remote Zugriff

```bash
# SSH-Tunnel für Remote-Zugriff
ssh -L 3002:localhost:3002 user@heizung-server
```

## 🤝 Beitragen

Beiträge sind willkommen! Bitte erstelle einen Pull Request oder öffne ein Issue auf GitHub.

## 📄 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert.

## 📞 Support

Bei Fragen oder Problemen öffne bitte ein Issue auf GitHub:
https://github.com/Minexvibx123/Vcontrold-for-Home-assistant/issues

## 🔗 Weiterführende Ressourcen

- [Home Assistant Integration Development](https://developers.home-assistant.io/docs/creating_integration_manifest/)
- [vcontrold Dokumentation](https://github.com/openv/vcontrold)
- [Viessmann Heizungssteuerung](https://www.viessmann.de/)