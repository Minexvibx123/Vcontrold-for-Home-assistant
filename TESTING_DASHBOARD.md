# 🎨 Test-Dashboard für vcontrold Integration

Verwende dieses Dashboard zur visuellen Überprüfung aller Funktionen!

## Installation

1. Kopiere den YAML-Code
2. Gehe zu: Dashboards → Erstelle Dashboard → Code-Editor
3. Füge den Code ein
4. Speichern

---

## 📊 Test-Dashboard YAML

```yaml
title: 🧪 vcontrold Test-Dashboard
views:
  - title: 🔥 Sensoren & Status
    path: vcontrold-test
    cards:
      # Titel
      - type: heading
        heading: "🔥 Vitotronic 300 - Live Status"
      
      # Sensoren als Gauge
      - type: grid
        columns: 2
        cards:
          - type: gauge
            entity: sensor.vcontrold_kesseltemperatur
            title: "🔥 Kessel"
            min: 0
            max: 80
            unit: "°C"
            
          - type: gauge
            entity: sensor.vcontrold_aussentemperatur
            title: "❄️ Außen"
            min: -20
            max: 40
            unit: "°C"
            
          - type: gauge
            entity: sensor.vcontrold_warmwasser_soll
            title: "💧 WW Soll"
            min: 0
            max: 80
            unit: "°C"
            
          - type: gauge
            entity: sensor.vcontrold_warmwasser_ist
            title: "💧 WW Ist"
            min: 0
            max: 80
            unit: "°C"
      
      # Vorlauf Extra
      - type: gauge
        entity: sensor.vcontrold_vorlauf_hk1
        title: "🔄 Vorlauf HK1"
        min: 0
        max: 80
        unit: "°C"
        width: full
      
      # Sensoren-Entities
      - type: entities
        title: "📊 Sensor-Details"
        entities:
          - entity: sensor.vcontrold_kesseltemperatur
          - entity: sensor.vcontrold_aussentemperatur
          - entity: sensor.vcontrold_warmwasser_soll
          - entity: sensor.vcontrold_warmwasser_ist
          - entity: sensor.vcontrold_vorlauf_hk1

  - title: 🎮 Services Testen
    path: vcontrold-services
    cards:
      - type: heading
        heading: "🎮 Service-Aufrufe Testen"
      
      # Information
      - type: markdown
        content: |
          ## Service 1: Warmwasser-Solltemperatur setzen
          
          Diese Schaltflächen setzen die Warmwasser-Solltemperatur
      
      # Service Buttons
      - type: grid
        columns: 4
        cards:
          - type: custom:button-card
            name: "WW 45°C"
            tap_action:
              action: call-service
              service: vcontrold.set_temp_ww_soll
              service_data:
                temperature: 45
            
          - type: custom:button-card
            name: "WW 50°C"
            tap_action:
              action: call-service
              service: vcontrold.set_temp_ww_soll
              service_data:
                temperature: 50
            
          - type: custom:button-card
            name: "WW 55°C"
            tap_action:
              action: call-service
              service: vcontrold.set_temp_ww_soll
              service_data:
                temperature: 55
            
          - type: custom:button-card
            name: "WW 60°C"
            tap_action:
              action: call-service
              service: vcontrold.set_temp_ww_soll
              service_data:
                temperature: 60
      
      # Service 2 Info
      - type: markdown
        content: |
          ## Service 2: Betriebsart ändern
          
          Diese Schaltflächen ändern den Betriebsmodus
      
      # Mode Buttons
      - type: grid
        columns: 4
        cards:
          - type: custom:button-card
            name: "🤖 Auto"
            tap_action:
              action: call-service
              service: vcontrold.set_betriebsart
              service_data:
                mode: "auto"
            
          - type: custom:button-card
            name: "⏸️ Standby"
            tap_action:
              action: call-service
              service: vcontrold.set_betriebsart
              service_data:
                mode: "standby"
            
          - type: custom:button-card
            name: "🎉 Party"
            tap_action:
              action: call-service
              service: vcontrold.set_betriebsart
              service_data:
                mode: "party"
            
          - type: custom:button-card
            name: "♻️ Eco"
            tap_action:
              action: call-service
              service: vcontrold.set_betriebsart
              service_data:
                mode: "eco"

  - title: 📈 Historisch
    path: vcontrold-history
    cards:
      - type: heading
        heading: "📈 Temperatur-Verlauf"
      
      # History Graph für Kessel
      - type: statistics-graph
        title: "🔥 Kesseltemperatur (24h)"
        entities:
          - sensor.vcontrold_kesseltemperatur
        stat_types:
          - mean
          - min
          - max
        period: day
      
      # History Graph für Außen
      - type: statistics-graph
        title: "❄️ Außentemperatur (24h)"
        entities:
          - sensor.vcontrold_aussentemperatur
        stat_types:
          - mean
          - min
          - max
        period: day
      
      # History für Vorlauf
      - type: statistics-graph
        title: "🔄 Vorlauf HK1 (24h)"
        entities:
          - sensor.vcontrold_vorlauf_hk1
        stat_types:
          - mean
          - min
          - max
        period: day

  - title: ⚙️ Diagnostik
    path: vcontrold-diagnostic
    cards:
      - type: heading
        heading: "⚙️ Diagnostik & Debug"
      
      # Integration Status
      - type: markdown
        content: |
          ## 🔍 Integration Status
          
          Öffne die HA Logs um Debug-Informationen zu sehen:
          Einstellungen → System → Logs
          Filter: "vcontrold"
      
      # Test Automation
      - type: markdown
        content: |
          ## 🤖 Test-Automation
          
          Verwende diese Services um die Verbindung zu testen:
          
          ### Service: start_daemon
          - Startet den vcontrold Daemon
          
          ### Service: stop_daemon
          - Stoppt den vcontrold Daemon
          
          ### Service: check_status
          - Prüft die Daemon-Gesundheit
      
      # Service Buttons für Daemon
      - type: grid
        columns: 3
        cards:
          - type: custom:button-card
            name: "▶️ Start Daemon"
            tap_action:
              action: call-service
              service: vcontrold.start_daemon
            
          - type: custom:button-card
            name: "⏹️ Stop Daemon"
            tap_action:
              action: call-service
              service: vcontrold.stop_daemon
            
          - type: custom:button-card
            name: "🏥 Status"
            tap_action:
              action: call-service
              service: vcontrold.check_status
      
      # Tipps
      - type: markdown
        content: |
          ## 💡 Test-Tipps
          
          1. **Sensoren nicht sichtbar?**
             - USB-Gerät prüfen: `ls -la /dev/ttyUSB*`
             - Port prüfen: `nc -zv localhost 3002`
             - Log-Level erhöhen: VITOTRONIC_300.md
          
          2. **Service antwortet nicht?**
             - Daemon läuft? Logs prüfen
             - Verbindung OK? Terminal-Test machen
             - Protokoll richtig? (KW vs Raw)
          
          3. **Sporadische Fehler?**
             - Update-Intervall erhöhen (60s → 120s)
             - USB-Kabel prüfen
             - Home Assistant neustarten
```

---

## 🎯 So nutzt du das Dashboard

### Zur Überprüfung während Testen:

1. **Tab "Sensoren & Status"**
   - Zeigt Live-Werte aller 5 Sensoren
   - Gauge-Visualisierung mit Min/Max
   - Sollten sich ~alle 60s aktualisieren

2. **Tab "Services Testen"**
   - Buttons zum Aufrufen von Services
   - Warmwasser-Solltemperatur setzen (45°C bis 60°C)
   - Betriebsart ändern (Auto, Standby, Party, Eco)
   - Immediately prüfen ob Sensoren reagieren

3. **Tab "Historisch"**
   - Zeigt 24h Temperatur-Verlauf
   - Min/Max/Durchschnitt
   - Nach 24h Test sichtbar

4. **Tab "Diagnostik"**
   - Daemon-Kontrolle (Start/Stop/Status)
   - Debug-Tipps
   - Troubleshooting Anlaufpunkte

---

## 📋 Test-Szenarien mit Dashboard

### Szenario 1: Sensor-Update Test (5 Min)
```
1. Öffne Dashboard "Sensoren & Status"
2. Beobachte die Gauge-Werte
3. Nach ~60 Sekunden sollten sich Werte aktualisieren
4. ✅ = Sensoren funktionieren!
```

### Szenario 2: Service-Test (3 Min)
```
1. Öffne Dashboard "Services Testen"
2. Klick auf "WW 55°C" Button
3. Warte ~1 Minute
4. Prüfe ob sensor.vcontrold_warmwasser_soll zu 55 wechselt
5. ✅ = Service funktioniert!
```

### Szenario 3: Daemon Recovery (5 Min)
```
1. Öffne Dashboard "Diagnostik"
2. Klick "Stop Daemon"
3. Sensoren sollten "unavailable" werden
4. Klick "Start Daemon"
5. Nach ~30s sollten Sensoren wieder da sein
6. ✅ = Auto-Recovery funktioniert!
```

### Szenario 4: Fehlerdiagnose
```
1. Sensoren zeigen "unavailable"?
   → Öffne Logs in HA
   → Filter: "vcontrold"
   → Suche nach Fehlern

2. Service antwortet nicht?
   → Tab "Diagnostik"
   → Klick "Status"
   → Logs prüfen

3. Nichts funktioniert?
   → Tab "Diagnostik"
   → Tipps lesen
```

---

## 🛠️ Dashboard anpassen

Falls du `custom:button-card` nicht hast:

```yaml
# Alternative für Standard-Button (ohne custom-card)
- type: button
  name: "WW 55°C"
  tap_action:
    action: call-service
    service: vcontrold.set_temp_ww_soll
    service_data:
      temperature: 55
```

---

## ✅ Fertig!

Du hast jetzt ein **vollständiges Test-Dashboard** zur visuellen Überprüfung! 🎉

Teste damit alle Funktionen und debugge Probleme grafisch! 📊✨

---

*vcontrold Test-Dashboard - November 2025*
