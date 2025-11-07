# ⚙️ Vitotronic 300 Konfiguration - Detaillierte Anleitung

## 🎯 Setup-Assistenten Schritte für Vitotronic 300

Der neue **Setup-Assistent** der Integration erkennt automatisch, dass du eine Vitotronic 300 hast und konfiguriert optimal:

### Schritt-für-Schritt

```
┌─────────────────────────────────────────┐
│ Schritt 1: Setup-Modus                  │
├─────────────────────────────────────────┤
│ Wähle: 🔧 HA verwaltet Daemon (STANDARD)│
│        oder                             │
│        🌐 Externe vcontrold             │
└─────────────────────────────────────────┘
       ↓ (Wähle "HA verwaltet")
       
┌─────────────────────────────────────────┐
│ Schritt 2: Heizungsmodell               │
├─────────────────────────────────────────┤
│ Wähle:                                  │
│ 🔥 Vitotronic 300 (EMPFOHLEN) ← DU BIS│
│ 🔥 Vitotronic 200                      │
│ 🔥 Vitola 300                          │
└─────────────────────────────────────────┘
       ↓
       
┌─────────────────────────────────────────┐
│ Schritt 3: Serielles Gerät              │
├─────────────────────────────────────────┤
│ Gerät: /dev/ttyUSB0                    │
│        (oder erkannter Port)            │
│                                         │
│ 💡 Tipps:                              │
│ - USB-Adapter prüfen                   │
│ - Kabel korrekt angeschlossen?         │
│ - Falls nicht erkannt: Manuell eingeben│
└─────────────────────────────────────────┘
       ↓
       
┌─────────────────────────────────────────┐
│ Schritt 4: Netzwerk                     │
├─────────────────────────────────────────┤
│ Host: localhost                         │
│ Port: 3002                              │
│                                         │
│ 💡 Für Vitotronic 300:                 │
│ - Lokal: localhost (standard)          │
│ - Remote: IP-Adresse oder SSH-Tunnel   │
└─────────────────────────────────────────┘
       ↓
       
┌─────────────────────────────────────────┐
│ Schritt 5: Erweiterte Einstellungen    │
├─────────────────────────────────────────┤
│ Update-Intervall: 60 Sekunden          │
│ Log-Level: 🔵 INFO                     │
│ Protokoll: 📡 KW (Komfortsignal)      │
│                                         │
│ ✅ Diese Werte sind für Vitotronic    │
│    300 optimiert!                      │
└─────────────────────────────────────────┘
       ↓
       
┌─────────────────────────────────────────┐
│ FERTIG! ✅                              │
├─────────────────────────────────────────┤
│ 5 Sensoren erscheinen:                 │
│ ├─ Kesseltemperatur                   │
│ ├─ Außentemperatur                    │
│ ├─ Warmwasser Soll                    │
│ ├─ Warmwasser Ist                     │
│ └─ Vorlauf HK1                        │
└─────────────────────────────────────────┘
```

---

## 🔧 Detaillierte Erklärung der Vitotronic 300 Einstellungen

### Update-Intervall (60 Sekunden)

**Für Vitotronic 300 optimal: 60 Sekunden**

```
30s  → Zu häufig (CPU-Last, Netzwerk-Last)
60s  → PERFEKT für Vitotronic 300 ✅
120s → Sparsam, aber Daten 2 Min alt
300s → Minimal-Betrieb
```

**Warum 60s für Vitotronic 300?**
- ✅ Ausreichend aktuell für Heizungsregelung
- ✅ Balanciert: Nicht zu oft, nicht zu selten
- ✅ Vitotronic 300 braucht nicht schneller zu aktualisieren
- ✅ Energieeffizient

### Log-Level

**Standard für Vitotronic 300: INFO**

```
🔴 ERROR
   └─ Nur Fehler-Meldungen
   └─ Für Produktion
   └─ Minimal Speicher

🟡 WARN
   └─ Warnungen + Fehler
   └─ Für stabile Systeme
   └─ Recommended für längerfristigen Betrieb

🔵 INFO  ← FÜR VITOTRONIC 300 GUT!
   └─ Informationen, Warnungen, Fehler
   └─ Zeigt was passiert
   └─ Gute für Initial-Setup

🟣 DEBUG
   └─ ALLES Details
   └─ Für Fehlersuche
   └─ NICHT für Produktion!
   └─ Großer Speicherverbrauch
```

### Protokoll (KW - Komfortsignal)

**Für Vitotronic 300: KW ist Standard!**

```
📡 KW (Komfortsignal) ← FÜR VITOTRONIC 300!
   ├─ Das Standard-Protokoll
   ├─ Beste Kompatibilität
   ├─ Das sichert du nutzen solltest
   └─ Falls nicht: Fehler-Handling

📡 Raw (Binär)
   ├─ Nur wenn KW nicht funktioniert
   ├─ Direkte Binär-Kommunikation
   └─ Seltener nötig

📡 Framing (Spezial)
   ├─ Nur für spezielle Modelle
   ├─ Nicht Standard
   └─ Probiere nur if KW fehlschlägt!
```

---

## 🎨 Nach der Installation

### Sensoren nutzen
```yaml
# In Automations/Scripts
{{ states('sensor.vcontrold_kesseltemperatur') }}
→ "45.3"

# In Templates
{% if states('sensor.vcontrold_kesseltemperatur') | float > 50 %}
  Kessel ist warm
{% endif %}
```

### Services aufrufen
```yaml
# Warmwasser setzen
service: vcontrold.set_temp_ww_soll
data:
  temperature: 60

# Betriebsart ändern
service: vcontrold.set_betriebsart
data:
  mode: "auto"
```

### Dashboard einrichten
```yaml
# Einfaches Gauge-Beispiel
type: gauge
entity: sensor.vcontrold_kesseltemperatur
min: 0
max: 80
```

---

## 🚨 Häufige Probleme & Lösungen (Vitotronic 300)

### Problem 1: "Gerät nicht erkannt"

```
Fehler: USB-Gerät erscheint nicht in Liste
Lösung:
1. USB-Adapter angeschlossen?
2. USB-Kabel OK?
3. Heizung eingeschaltet?
4. Prüfe Gerät:
   ssh user@homeassistant
   ls -la /dev/ttyUSB*
5. Falls nicht vorhanden: USB-Adapter testen
```

### Problem 2: "Sensoren zeigen unavailable"

```
Fehler: 5 Sensoren - alle "unavailable"
Ursache: vcontrold verbindung fehlgeschlagen

Lösung (der Reihe nach):
1. Prüfe Port:
   nc -zv localhost 3002

2. Prüfe Protokoll (Change Log-Level zu DEBUG):
   Settings → Devices & Services
   → vcontrold → Configure
   → Log-Level: DEBUG
   → Submit

3. Check Logs:
   Settings → System → Logs
   Filter: "vcontrold"

4. Prüfe vcontrold Daemon:
   ps aux | grep vcontrold

5. Starten Sie den Daemon manuell:
   docker exec homeassistant /config/vcontrold/vcontrold
```

### Problem 3: "Verbindung wird immer wieder unterbrochen"

```
Fehler: Sensors OK, aber dann sporadic "unavailable"
Ursache: RS232-Verbindung instabil

Lösung:
1. Erhöhe Update-Intervall (60s → 120s)
   Settings → Devices & Services
   → vcontrold → Configure
   → Update-Intervall: 120
   → Submit

2. Wechsel USB-Kabel (evtl. schadhaft)

3. Probiere USB-Hub (direkt am PC besser)

4. Prüfe Vitotronic 300 Einstellungen:
   - Serieller Port korrekt konfiguriert?
   - Baud Rate Standard?
```

### Problem 4: "Nur 1-2 Sensoren laden, Rest unavailable"

```
Fehler: Nicht alle 5 Sensoren sichtbar
Ursache: vcontrold antwortet teilweise

Lösung:
1. Versuche andere Protokoll:
   Raw statt KW
   
2. Prüfe Vitotronic 300 Konfiguration

3. Contact vcontrold support
```

---

## 💡 Tipps für optimalen Betrieb

### 1. Update-Intervall richtig wählen
```
Standard (60s): Gut für Heizungsregelung
Schneller (30s): Nur für Debugging nötig
Langsamer (120s): Wenn Probleme mit Stabiliät
```

### 2. Log-Level für Produktion
```
INFO → Gut zum Verfolgen
ERROR → Spart RAM/Speicher
```

### 3. Regelmäßige Wartung
```
1x pro Monat:
- Prüfe Logs auf Fehler
- Prüfe Sensorwerte (plausibel?)
- Prüfe Verbindung (nc -zv localhost 3002)
```

### 4. Energieeffizienz mit Vitotronic 300
```yaml
# Smart Scheduling
automation:
  - alias: "Vitotronic 300: Tag (7:00)"
    trigger:
      platform: time
      at: "07:00:00"
    action:
      service: vcontrold.set_temp_ww_soll
      data:
        temperature: 60
  
  - alias: "Vitotronic 300: Nacht (23:00)"
    trigger:
      platform: time
      at: "23:00:00"
    action:
      service: vcontrold.set_temp_ww_soll
      data:
        temperature: 45
```

---

## 📊 Vitotronic 300 Sensor-Werte verstehen

### Kesseltemperatur
```
Normal: 40-60°C
Zu hoch (>75°C): Problem?
Zu niedrig (<20°C): Heizung aus?
Optimal für Vitotronic 300: 45-55°C
```

### Außentemperatur
```
Sollte mit echtem Wetter übereinstimmen
Wenn falsch: Außensensor prüfen
Vitotronic 300 nutzt für Regelung
```

### Warmwasser-Soll
```
Typischerweise: 50-60°C
Nachts sparend: 45°C
Komfort: 60°C
Maximum: 80°C
```

### Warmwasser-Ist
```
Sollte dem Soll folgen
Wenn viel langsamer: Heizung OK, dauert
```

### Vorlauf HK1
```
Heizwasser für Heizkörper
Normal: 30-50°C je nach Außentemp
Vitotronic 300 regelt automatisch
```

---

## 🔗 Weitere Ressourcen

- 📖 [VITOTRONIC_300.md](VITOTRONIC_300.md) - Vollständiger Vitotronic 300 Guide
- 📖 [README.md](README.md) - Allgemeine Integration Guide
- 📖 [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) - Kompletter Guide
- 🔧 [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Fehlersuche

---

## ✅ Checkliste zur Vitotronic 300 Einrichtung

- [ ] USB-Adapter gekauft & angeschlossen
- [ ] vcontrold installiert
- [ ] Integration kopiert
- [ ] Home Assistant neu gestartet
- [ ] Setup Wizard durchlaufen
- [ ] Heizungsmodell: "Vitotronic 300" ausgewählt
- [ ] Serielles Gerät erkannt
- [ ] 5 Sensoren erscheinen
- [ ] Services funktionieren
- [ ] Dashboard erstellt
- [ ] Erste Automation getestet
- [ ] Log-Level auf "INFO" oder "ERROR" gesetzt

---

## 🎉 Fertig!

Deine **Viessmann Vitotronic 300** ist nun optimal mit Home Assistant konfiguriert!

**Nächste Schritte:**
1. ✅ Energieverbrauch monitoren
2. ✅ Automations erstellen
3. ✅ Komfortable Smart Home genießen
4. ✅ Kosten sparen

---

**Viel Erfolg mit deiner intelligenten Heizungssteuerung!** 🔥❄️

*Viessmann Vitotronic 300 Konfigurationsguide - November 2025*
