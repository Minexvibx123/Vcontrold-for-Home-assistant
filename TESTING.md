# 🧪 vcontrold Integration - Umfassende Test-Anleitung

## 🎯 Test-Strategie

Es gibt mehrere Ebenen zum Testen der Integration:

1. **Installation & Basis-Setup** ✅ (Sollte funktionieren)
2. **Sensorwerte-Abfrage** 📊 (Daten kommen?)
3. **Service-Aufrufe** 🎮 (Steuerung funktioniert?)
4. **Automations** 🤖 (Logik funktioniert?)
5. **Fehlertoleranz** 🛡️ (Robustheit?)

---

## 📋 Test 1: Installation & Grundkonfiguration

### Schritt 1: Integration richtig installiert?

```bash
# SSH zu Home Assistant
docker exec -it homeassistant bash

# Prüfe Installation
ls -la /config/custom_components/vcontrold/

# Sollte zeigen:
# ✅ __init__.py
# ✅ sensor.py
# ✅ config_flow.py
# ✅ vcontrold_manager.py
# ✅ manifest.json
# ✅ services.yaml
# ✅ strings.json
```

### Schritt 2: Home Assistant neugestartet?

```bash
# Prüfe dass kein Fehler in Startup-Logs
docker logs homeassistant | grep vcontrold

# Sollte zeigen:
# ✅ "Integration loaded successfully" (oder ähnlich)
# ❌ Keine Fehler!
```

### Schritt 3: Setup Wizard durchlaufen?

```
Einstellungen → Devices & Services
→ "Create Integration"
→ "vcontrold" suchen
→ Wizard durchlaufen (5 Minuten)

Sollte zeigen:
✅ Integration "vcontrold" erscheint
✅ Entry mit Konfiguration
```

---

## 🔌 Test 2: Serielles Gerät & USB-Verbindung

### Prüfe USB-Adapter

```bash
# SSH zu Home Assistant
docker exec -it homeassistant bash

# Zeige verfügbare serielle Geräte
ls -la /dev/tty*

# Sollte zeigen:
# /dev/ttyUSB0    ← Falls USB-Adapter
# /dev/ttyACM0    ← Falls Arduino-style
# /dev/ttyS0      ← Falls echter serieller Port
```

### Test: Ist das Gerät erkannt?

```bash
# Versuche mit dem Gerät zu schreiben (dummt nicht wirklich)
echo "test" > /dev/ttyUSB0 2>&1

# Sollte zeigen:
# ✅ Keine Fehlermeldung (oder nur Device-Fehler, das ist OK)
# ❌ "Device not found" → USB-Adapter nicht angeschlossen!
```

### Test: Baudrate/Verbindung

```bash
# Mit pyserial testen
python3 << 'EOF'
import serial
try:
    ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
    print(f"✅ Verbindung OK: {ser.name}")
    ser.close()
except Exception as e:
    print(f"❌ Fehler: {e}")
EOF
```

---

## 📊 Test 3: Sensoren-Daten auslesen

### Test 3.1: Sind die 5 Sensoren da?

**GUI:**
```
Einstellungen → Devices & Services
→ "vcontrold" klicken
→ Sollte zeigen: 5 Entities/Sensoren
  ├─ sensor.vcontrold_kesseltemperatur
  ├─ sensor.vcontrold_aussentemperatur
  ├─ sensor.vcontrold_warmwasser_soll
  ├─ sensor.vcontrold_warmwasser_ist
  └─ sensor.vcontrold_vorlauf_hk1
```

### Test 3.2: Haben Sensoren Werte?

**Developer Tools (in HA):**
```
Einstellungen → Developer Tools → States

Suche: "vcontrold_kesseltemperatur"

Sollte zeigen:
✅ Wert: "45.3" (oder andere Zahl)
✅ Unit: "°C"
✅ Nicht "unavailable" oder "unknown"
```

### Test 3.3: Template-Test

```
Einstellungen → Developer Tools → Templates

Gib ein:
{{ states('sensor.vcontrold_kesseltemperatur') }}

Sollte zeigen:
✅ "45.3" (aktueller Wert)
❌ Wenn "unavailable" → Problem mit vcontrold Connection
```

### Test 3.4: Logs prüfen

```
Einstellungen → System → Logs

Filter: "vcontrold"

Sollte zeigen:
✅ "Sensor updated: 45.3°C"
✅ "Connection successful"
❌ Keine Fehler!
```

---

## 🎮 Test 4: Services testen

### Service 1: Warmwasser-Solltemperatur setzen

**GUI-Test:**
```
Einstellungen → Developer Tools → Services

Service: vcontrold.set_temp_ww_soll

Data:
{
  "temperature": 55
}

Klick "Call Service"

Sollte zeigen:
✅ Keine Fehler
✅ Sensorwert ändert sich (nach ~1 Minute)
```

**YAML-Test (in Automation):**
```yaml
service: vcontrold.set_temp_ww_soll
data:
  temperature: 60
```

### Service 2: Betriebsart ändern

**GUI-Test:**
```
Einstellungen → Developer Tools → Services

Service: vcontrold.set_betriebsart

Data:
{
  "mode": "auto"
}

Klick "Call Service"

Sollte zeigen:
✅ Keine Fehler
✅ Heizung ändert Modus
```

**Mögliche Modes:**
```
"auto"     → Normal
"standby"  → Aus
"party"    → Komfort
"eco"      → Sparen
```

---

## 🤖 Test 5: Automations Test

### Simple Test-Automation

```yaml
# configuration.yaml
automation:
  - alias: "Test: Warmwasser setzen"
    trigger:
      platform: time
      at: "15:00:00"  # Täglich um 15:00
    action:
      service: vcontrold.set_temp_ww_soll
      data:
        temperature: 60

  - alias: "Test: Temperatur-Anzeige"
    trigger:
      platform: numeric_state
      entity_id: sensor.vcontrold_kesseltemperatur
      above: 50
    action:
      service: notify.notify
      data:
        message: "🔥 Kessel warm: {{ states('sensor.vcontrold_kesseltemperatur') }}°C"
```

### Test durchführen:

```
1. Automation speichern
2. Home Assistant neu laden
3. Automatisch triggern:
   Developer Tools → Services
   Service: automation.trigger
   Data: {"entity_id": "automation.test_warmwasser_setzen"}

Sollte zeigen:
✅ Service wird aufgerufen
✅ Wert wird gesetzt
✅ Keine Fehler in Logs
```

---

## 🔧 Test 6: Fehlerbehandlung testen

### Test 6.1: USB-Kabel abziehen

```
1. USB-Kabel von Adapter abziehen
2. Log-Level auf DEBUG setzen
3. Beobachte Logs

Sollte zeigen:
✅ Fehler: "Connection refused"
✅ Auto-Retry nach Update-Intervall
✅ Nach Rekonnect: Sensoren wieder verfügbar
```

### Test 6.2: Falscher Port konfigurieren

```
1. Stelle Port auf 9999 (falsch)
2. Warte auf Timeout

Sollte zeigen:
✅ Timeout-Fehler nach 10 Sekunden
✅ Sensoren zeigen "unavailable"
❌ Integration sollte nicht crashen
```

### Test 6.3: Daemon absichtlich stoppen

```bash
docker exec -it homeassistant bash
ps aux | grep vcontrold
kill <PID>

Sollte zeigen:
✅ Sensoren werden "unavailable"
✅ Auto-Restart aktiviert sich
✅ Nach ~30-60s: Wieder online
```

---

## 📈 Test 7: Performance & Stabilität

### Test 7.1: Update-Intervall testen

```
Standard: 60 Sekunden

Teste verschiedene Intervalle:
- 30s  → Schnell, aber mehr Last
- 60s  → Standard (empfohlen)
- 120s → Sparsam
- 300s → Minimal

Prüfe:
✅ CPU-Last (nicht zu hoch)
✅ RAM-Nutzung (nicht zu hoch)
✅ Sensoren aktualisieren regelmäßig
```

### Test 7.2: Langzeit-Stabilität (24h+)

```
1. Stelle Log-Level auf ERROR
2. Lasse Integration 24 Stunden laufen
3. Prüfe nach 24h:

Sollte zeigen:
✅ Keine Fehlermeldungen gehäuft
✅ Sensoren korrekt
✅ Speicher nicht angewachsen
```

---

## 🔍 Test 8: Debug-Modus verwenden

### Log-Level auf DEBUG setzen

```
Einstellungen → Devices & Services
→ vcontrold → Configure
→ Log-Level: 🟣 DEBUG
→ Submit
```

### Detaillierte Logs beobachten

```
Einstellungen → System → Logs

Filter: "vcontrold"

Sollte zeigen (bei DEBUG):
✅ "Attempting connection to localhost:3002"
✅ "Sending command: getTempKessel"
✅ "Received response: 45.3"
✅ "Sensor updated: 45.3°C"
```

### Logs exportieren (für Support)

```bash
docker exec homeassistant cat /config/home-assistant.log | grep vcontrold > vcontrold_logs.txt

# Datei hochladen falls Hilfe nötig
```

---

## 🧩 Test 9: Integration mit anderen Add-ons

### Test mit Node-RED (optional)

```javascript
// Node-RED Function
msg.payload = {
    "service": "vcontrold.set_temp_ww_soll",
    "data": {
        "temperature": 60
    }
};
return msg;
```

### Test mit Automations

```yaml
automation:
  - alias: "Externe Trigger"
    trigger:
      platform: webhook
      webhook_id: "my_webhook"
    action:
      service: vcontrold.set_betriebsart
      data:
        mode: "{{ trigger.json.mode }}"
```

---

## ✅ Checkliste: Vollständiger Test

- [ ] **Installation**
  - [ ] Dateien im richtigen Ordner
  - [ ] Home Assistant neugestartet
  - [ ] Keine Fehler im Startup-Log

- [ ] **Hardware**
  - [ ] USB-Adapter angeschlossen
  - [ ] Gerät erkannt (/dev/ttyUSB0)
  - [ ] Pyserial Connection funktioniert

- [ ] **Sensoren**
  - [ ] 5 Sensoren erscheinen
  - [ ] Alle haben Werte
  - [ ] Template-Auswertung funktioniert
  - [ ] Logs zeigen keine Fehler

- [ ] **Services**
  - [ ] set_temp_ww_soll funktioniert
  - [ ] set_betriebsart funktioniert
  - [ ] Keine Fehler

- [ ] **Automations**
  - [ ] Einfache Automation triggert
  - [ ] Service wird aufgerufen
  - [ ] Logs zeigen Erfolg

- [ ] **Fehlerbehandlung**
  - [ ] USB abziehen → Fehler, dann Recovery
  - [ ] Falscher Port → Timeout OK
  - [ ] Daemon Stop → Auto-Restart

- [ ] **Performance**
  - [ ] CPU-Last normal
  - [ ] RAM nicht anwachsend
  - [ ] Updates zuverlässig

- [ ] **Langzeit (24h+)**
  - [ ] Keine gehäuften Fehler
  - [ ] Sensoren stabil
  - [ ] Speicher OK

---

## 🐛 Probleme diagnostizieren

### Symptom: "unavailable" Sensoren

```bash
# 1. Prüfe Verbindung
nc -zv localhost 3002

# 2. Prüfe vcontrold Process
ps aux | grep vcontrold

# 3. Setze Log-Level auf DEBUG
# 4. Prüfe Logs: Settings → System → Logs
# 5. Versuche Protokoll zu wechseln (KW → Raw)
```

### Symptom: Timeout-Fehler

```bash
# 1. Prüfe USB-Kabel
# 2. Erhöhe Update-Intervall (60s → 120s)
# 3. Prüfe Baudrate
# 4. Versuche Protokoll-Wechsel
```

### Symptom: Services funktionieren nicht

```bash
# 1. Prüfe Service-Definition in services.yaml
# 2. Prüfe dass Service existiert:
#    Developer Tools → Services
# 3. Versuche Service manuell zu callen
# 4. Prüfe Logs auf Fehler
```

---

## 📝 Test-Protokoll-Vorlage

Verwende diese Vorlage für deine Tests:

```
=== VCONTROLD TEST-PROTOKOLL ===

Datum: ___________
Heizungsmodell: Vitotronic 300
Setup: All-in-One

INSTALLATION
[ ] Integration richtig installiert
[ ] Keine Fehler beim Start
[ ] Home Assistant neu gestartet

HARDWARE
[ ] USB-Gerät erkannt: ___________
[ ] Baudrate OK
[ ] Pyserial Test: PASSED/FAILED

SENSOREN
[ ] 5 Sensoren sichtbar
[ ] Alle haben Werte:
    Kessel: ________°C
    Außen: ________°C
    WW-Soll: ________°C
    WW-Ist: ________°C
    Vorlauf: ________°C

SERVICES
[ ] set_temp_ww_soll: PASSED/FAILED
[ ] set_betriebsart: PASSED/FAILED

AUTOMATIONS
[ ] Test-Automation triggert: YES/NO
[ ] Service wird aufgerufen: YES/NO

FEHLERBEHANDLUNG
[ ] USB abziehen: Fehler auslöst: YES/NO
[ ] Auto-Recovery nach Fehler: YES/NO
[ ] Timeout-Handling OK: YES/NO

PERFORMANCE
[ ] CPU-Last normal: YES/NO (Wert: ___%)
[ ] RAM OK: YES/NO (Wert: ___ MB)

ERGEBNIS: ✅ BESTANDEN / ❌ FEHLGESCHLAGEN

Probleme:
_________________________________
_________________________________

Notizen:
_________________________________
_________________________________
```

---

## 🎯 Beste Vorgehensweise zum Testen

### Phase 1: Grundlagen (30 Min)
1. Installation prüfen
2. USB-Gerät testen
3. 5 Sensoren überprüfen
4. Einen Service testen

### Phase 2: Tiefere Tests (1-2 Std)
1. Beide Services testen
2. Einfache Automation schreiben & testen
3. Log-Level erhöhen & Debug-Output beobachten
4. Fehlerbehandlung testen

### Phase 3: Produktion (24+ Std)
1. Log-Level auf ERROR
2. Normale Nutzung für 24+ Stunden
3. Stabilitätsprüfung
4. Nichts sollte crashen!

---

## 📞 Support bei Problemen

Falls Tests fehlschlagen:

1. **Logs sammeln**
   ```bash
   docker exec homeassistant cat /config/home-assistant.log | grep vcontrold > logs.txt
   ```

2. **Informationen sammeln**
   - vcontrold Version
   - Home Assistant Version
   - Heizungsmodell (Vitotronic 300)
   - Fehler-Meldung (genau)

3. **Issue auf GitHub öffnen**
   - Mit Logs
   - Mit Test-Ergebnissen
   - Mit Beschreibung des Problems

---

## ✅ Fertig!

Du hast alle Test-Ebenen durchgearbeitet und weißt nun genau, ob die Integration funktioniert! 🎉

**Viel Erfolg beim Testen!** 🧪✨

---

*vcontrold Integration - Test-Anleitung für Vitotronic 300 | November 2025*
