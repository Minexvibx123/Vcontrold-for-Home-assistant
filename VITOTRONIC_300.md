# 🔥 Viessmann Vitotronic 300 - Integration Guide

## Übersicht

Diese Integration ist speziell optimiert für die **Viessmann Vitotronic 300** Heizungsanlage. Sie ermöglicht lokale Steuerung und Überwachung ohne Cloud-Abhängigkeit.

---

## 🎯 Was ist die Vitotronic 300?

Die **Vitotronic 300** ist eine hochmoderne Heizungsregelung von Viessmann mit:
- ✅ Intelligente Temperaturregelung
- ✅ Energieeffizienz-Optimierung
- ✅ Mehrere Heizkreise (HK1, HK2)
- ✅ Warmwasserbereitung
- ✅ Modulierende Kesselleistung
- ✅ RS232/RS485 Schnittstelle

---

## 📋 Anforderungen für Vitotronic 300

### Hardware
- ✅ Viessmann Vitotronic 300 Regelung
- ✅ Heizgerät (Vitola, Vitodens, etc.)
- ✅ USB-RS232 Adapter oder serieller Port
- ✅ Home Assistant Installation
- ✅ Netzwerk-Zugang (lokal oder SSH-Tunnel)

### Software
- ✅ Home Assistant 2024.1.0+
- ✅ Python 3.8+
- ✅ vcontrold Daemon
- ✅ Diese Integration

### Konfiguration
- ✅ Serielles Gerät: `/dev/ttyUSB0` (oder andere)
- ✅ TCP Port: 3002 (konfigurierbar)
- ✅ Protokoll: KW (Komfortsignal) - Standard!
- ✅ Update-Intervall: 60s (empfohlen)

---

## 🚀 Installation für Vitotronic 300

### Schritt 1: Installation
```bash
# SSH in Home Assistant
docker exec -it homeassistant bash

# Integration kopieren
cp -r vcontrold /config/custom_components/

# Home Assistant neustarten
```

### Schritt 2: Home Assistant Neustart
```
Einstellungen → System → Restart Home Assistant
```

### Schritt 3: Setup Wizard
```
Einstellungen → Devices & Services
→ Create Integration
→ "vcontrold" suchen
→ Wizard starten
```

### Schritt 4: Konfiguriere für Vitotronic 300

#### Schritt 1: Setup-Modus
```
Wähle: 🔧 HA verwaltet Daemon (All-in-One)
```

#### Schritt 2: Heizungsmodell
```
Wähle: 🔥 Vitotronic 300 (empfohlen)
```

#### Schritt 3: Serielles Gerät
```
Gerät: /dev/ttyUSB0 (oder erkannter Port)
💡 Falls nicht erkannt: Prüfe USB-Verbindung
```

#### Schritt 4: Netzwerk
```
Host: localhost (für lokale Nutzung)
Port: 3002 (Standard für vcontrold)
```

#### Schritt 5: Erweiterte Einstellungen
```
Update-Intervall: 60 Sekunden (für Vitotronic 300 optimal)
Log-Level: INFO (oder ERROR für Produktion)
Protokoll: KW (Komfortsignal - Standard für Vitotronic 300)
```

### Schritt 6: Fertig! ✅
```
5 Sensoren erscheinen automatisch:
├─ Kesseltemperatur
├─ Außentemperatur
├─ Warmwasser Solltemperatur
├─ Warmwasser Isttemperatur
└─ Vorlauf Heizkreis 1
```

---

## 📊 Verfügbare Sensoren (Vitotronic 300)

| Sensor | Beschreibung | Einheit | Update |
|--------|-------------|---------|---------|
| `kesseltemperatur` | Aktuelle Kesseltemperatur | °C | 60s |
| `aussentemperatur` | Außentemperatur (Sensor) | °C | 60s |
| `warmwasser_soll` | Warmwasser-Solltemperatur | °C | 60s |
| `warmwasser_ist` | Warmwasser-Isttemperatur | °C | 60s |
| `vorlauf_hk1` | Vorlauftemperatur HK1 | °C | 60s |

**Beispiel Abfrage:**
```yaml
{{ states('sensor.vcontrold_kesseltemperatur') }}  # 45.3
{{ states('sensor.vcontrold_warmwasser_ist') }}   # 52.5
```

---

## 🎮 Verfügbare Services

### 1. Warmwasser-Solltemperatur setzen
```yaml
service: vcontrold.set_temp_ww_soll
data:
  temperature: 60  # 20-80°C
```

### 2. Betriebsart ändern
```yaml
service: vcontrold.set_betriebsart
data:
  mode: "auto"  # auto | standby | party | eco
```

---

## 🤖 Automations-Beispiele für Vitotronic 300

### Beispiel 1: Nachtabsenkung
```yaml
automation:
  - alias: "Vitotronic 300: Nacht (22:00)"
    trigger:
      platform: time
      at: "22:00:00"
    action:
      service: vcontrold.set_temp_ww_soll
      data:
        temperature: 45  # Nachts sparen
```

### Beispiel 2: Morgens aufheizen
```yaml
automation:
  - alias: "Vitotronic 300: Morgens (06:30)"
    trigger:
      platform: time
      at: "06:30:00"
    action:
      service: vcontrold.set_temp_ww_soll
      data:
        temperature: 60  # Morgens komfortabel
```

### Beispiel 3: Automatische Anpassung nach Außentemperatur
```yaml
automation:
  - alias: "Vitotronic 300: Außen <5°C → Boost"
    trigger:
      platform: numeric_state
      entity_id: sensor.vcontrold_aussentemperatur
      below: 5
    action:
      service: vcontrold.set_betriebsart
      data:
        mode: "auto"  # Volle Power
```

### Beispiel 4: Temperatur-Alarm
```yaml
automation:
  - alias: "Vitotronic 300: Alarm - Zu heiß!"
    trigger:
      platform: numeric_state
      entity_id: sensor.vcontrold_kesseltemperatur
      above: 75
    action:
      service: notify.notify
      data:
        message: "⚠️ Kessel zu heiß: {{ states('sensor.vcontrold_kesseltemperatur') }}°C"
```

---

## 🎨 Dashboard Setup für Vitotronic 300

### Einfache Temperatur-Übersicht
```yaml
type: vertical-stack
cards:
  - type: heading
    heading: "🔥 Vitotronic 300 Heizung"
  
  - type: grid
    columns: 2
    cards:
      - type: gauge
        entity: sensor.vcontrold_kesseltemperatur
        min: 0
        max: 80
        title: "Kessel"
      
      - type: gauge
        entity: sensor.vcontrold_aussentemperatur
        min: -20
        max: 40
        title: "Außen"
      
      - type: gauge
        entity: sensor.vcontrold_warmwasser_ist
        min: 0
        max: 80
        title: "WW Ist"
      
      - type: gauge
        entity: sensor.vcontrold_vorlauf_hk1
        min: 0
        max: 80
        title: "Vorlauf HK1"
  
  - type: entities
    entities:
      - entity: sensor.vcontrold_warmwasser_soll
        name: "WW Soll"
```

---

## 🔧 Vitotronic 300 spezifische Tipps

### Protokoll-Einstellungen
```
KW (Standard) ← Für Vitotronic 300 empfohlen
- Komfortsignal-Protokoll
- Meist zuverlässig
- Beste Kompatibilität

Raw
- Binäres Protokoll
- Nur wenn KW nicht funktioniert

Framing
- Spezial-Protokoll
- Für bestimmte Modelle
```

### Update-Intervall Optimierung
```
30s - Schnell, aber höhere Last
60s ← Empfohlen für Vitotronic 300
120s - Sparsam, aber träger
300s - Minimal-Betrieb
```

### Troubleshooting für Vitotronic 300

#### Problem: "Cannot connect"
```
1. Prüfe USB-Verbindung
2. Prüfe Serielles Gerät: ls -la /dev/ttyUSB*
3. Prüfe Daemon: ps aux | grep vcontrold
4. Prüfe Port: nc -zv localhost 3002
```

#### Problem: "Sensoren zeigen unavailable"
```
1. Überprüfe Protokoll-Einstellung (KW → Raw → Framing)
2. Überprüfe Log-Level auf DEBUG
3. Check Logs: Settings → System → Logs
4. Prüfe vcontrold Daemon-Ausgabe
```

#### Problem: Sporadische Verbindungsabbrüche
```
1. Erhöhe Update-Intervall (60s → 120s)
2. Prüfe Kabelverbindung
3. Prüfe USB-Hub (zu viele Geräte?)
4. Versuche anderes USB-Kabel
```

---

## 📱 Remote-Zugriff auf Vitotronic 300

Wenn deine Vitotronic 300 nicht lokal erreichbar ist, verwende SSH-Tunnel:

```bash
# SSH-Tunnel öffnen
ssh -L 3002:192.168.1.50:3002 user@heizung-server

# Dann in HA verwenden:
# Host: localhost
# Port: 3002
```

---

## 🌡️ Energieeffizienz-Tipps mit Vitotronic 300

### Smart Heating mit Automations
```yaml
# Tagesmodus: Komfortabel
automation:
  - alias: "Tag: Komfort"
    trigger:
      platform: time
      at: "07:00:00"
    action:
      service: vcontrold.set_temp_ww_soll
      data:
        temperature: 60

# Nachtmodus: Sparen
  - alias: "Nacht: Sparen"
    trigger:
      platform: time
      at: "23:00:00"
    action:
      service: vcontrold.set_temp_ww_soll
      data:
        temperature: 45

# Urlaubsmodus
  - alias: "Urlaub: Minimal"
    trigger:
      platform: state
      entity_id: input_boolean.urlaub
      to: "on"
    action:
      service: vcontrold.set_betriebsart
      data:
        mode: "eco"
```

---

## 📚 Weitere Ressourcen

- 📖 [README.md](README.md) - Hauptdokumentation
- 📘 [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) - Kompletter Guide
- 🔧 [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Fehlersuche
- 🏗️ [ARCHITECTURE.md](ARCHITECTURE.md) - Technische Details

---

## ✅ Vitotronic 300 Checkliste

- [ ] USB-Adapter angeschlossen
- [ ] vcontrold installiert
- [ ] Integration kopiert
- [ ] Home Assistant neu gestartet
- [ ] Setup Wizard durchlaufen
- [ ] Heizungsmodell: Vitotronic 300 ausgewählt
- [ ] 5 Sensoren erschienen
- [ ] Services funktionieren
- [ ] Dashboard erstellt
- [ ] Erste Automation getestet

---

## 🎉 Fertig!

Deine **Viessmann Vitotronic 300** ist nun mit Home Assistant verbunden! 🔥

**Nächste Schritte:**
1. Dashboard erstellen
2. Automations einrichten
3. Energie sparen
4. Genießen! 😊

---

**Viel Spaß mit deiner intelligenten Heizungssteuerung!** ❄️🔥

*Viessmann Vitotronic 300 Integration v1.0 - November 2025*
