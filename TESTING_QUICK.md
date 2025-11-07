# ⚡ Quick Test Checkliste - 15 Minuten

Verwende diese Checkliste für schnelle Tests zwischendurch!

---

## 🟢 Test 1: Status Check (2 Min)

```bash
# SSH in Home Assistant
docker exec -it homeassistant bash

# Ist vcontrold installiert?
ls -la /config/custom_components/vcontrold/ | grep -q __init__.py && echo "✅ Installation OK" || echo "❌ Installation fehlgeschlagen"

# Ist das USB-Gerät da?
ls -la /dev/ttyUSB0 2>/dev/null && echo "✅ USB-Gerät erkannt" || echo "❌ USB-Gerät nicht gefunden"

# Läuft vcontrold?
ps aux | grep vcontrold | grep -v grep && echo "✅ Daemon läuft" || echo "❌ Daemon nicht aktiv"

# Ist Port 3002 offen?
nc -zv localhost 3002 2>&1 && echo "✅ Port erreichbar" || echo "❌ Port nicht erreichbar"
```

---

## 🟡 Test 2: Sensoren (3 Min)

**GUI:**
```
Einstellungen → Devices & Services → vcontrold

☑️ Sollten 5 Sensoren sichtbar sein
☑️ Sollten alle einen Wert haben (nicht "unavailable")
☑️ Kesseltemperatur > 20°C ?
☑️ Außentemperatur plausibel ?
```

**Terminal:**
```bash
# Template-Test
docker exec homeassistant hass --script check_home_assistant

# Oder Developer Tools in HA GUI:
{{ states('sensor.vcontrold_kesseltemperatur') }}
# Sollte eine Zahl zeigen, z.B. "45.3"
```

---

## 🔵 Test 3: Service-Call (3 Min)

**GUI:**
```
Einstellungen → Developer Tools → Services

Service: vcontrold.set_temp_ww_soll
Data: {"temperature": 55}

Klick "Call Service"
→ Sollte kein Fehler auftauchen
```

---

## 🟣 Test 4: Logs (3 Min)

```
Einstellungen → System → Logs

Filter: "vcontrold"
→ Sollte Erfolgs-Meldungen zeigen
→ Keine Fehler sichtbar?
```

---

## ⚫ Test 5: Auto-Recovery (4 Min)

```bash
# USB abziehen
# → Sensoren sollten "unavailable" werden

# USB wieder anstecken
# Warte 60 Sekunden (ein Update-Intervall)
# → Sensoren sollten wieder Werte zeigen

✅ = Integration robust gegen Fehler!
```

---

## 📊 Schnell-Diagnose

Wenn etwas nicht funktioniert:

| Problem | Erste Prüfung |
|---------|---------------|
| Sensoren "unavailable" | `nc -zv localhost 3002` |
| Service antwortet nicht | Developer Tools → Services testen |
| Timeout-Fehler | Log-Level auf DEBUG, Logs prüfen |
| USB nicht erkannt | `ls -la /dev/ttyUSB*` |
| Integration lädt nicht | Installation-Verzeichnis prüfen |

---

## ✅ ALLES OK?

Wenn alle 5 Tests grün sind = **Integration funktioniert!** 🎉

```
Test 1: ✅ Status OK
Test 2: ✅ Sensoren OK  
Test 3: ✅ Services OK
Test 4: ✅ Logs OK
Test 5: ✅ Recovery OK

→ READY FOR PRODUCTION! 🚀
```

---

*Quick Test - 15 Minuten Diagnostik*
