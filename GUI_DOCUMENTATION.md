# 🎨 vcontrold Integration - WebUI & GUI Dokumentation

## Übersicht: Setup-Assistent

Die Integration bietet jetzt einen **benutzerfreundlichen Multi-Step Config Flow** mit vollständiger GUI! 

### 🎯 Das neue GUI-Setup:

```
Schritt 1: Setup-Modus wählen
├─ 🔧 All-in-One (HA verwaltet)
└─ 🌐 Externe vcontrold

Schritt 2a (All-in-One): Serielles Gerät
└─ Dropdown mit verfügbaren Ports
   oder manuelle Eingabe

Schritt 2b (All-in-One): Netzwerk
├─ Host (default: localhost)
└─ Port (default: 3002, 1024-65535)

Schritt 2c (All-in-One): Erweitert
├─ Update-Intervall (30-300s)
├─ Log-Level (ERROR/WARN/INFO/DEBUG)
└─ Protokoll (KW/raw/framing)

Schritt 2b (Extern): Verbindung
├─ Host/IP-Adresse
├─ Port
└─ TCP-Test

Schritt 2c (Extern): Erweitert
└─ Update-Intervall
```

## 📋 Detaillierte Felder

### Allgemein (für beide Modi)

#### Update-Intervall
```
Min: 30 Sekunden
Max: 300 Sekunden (5 Minuten)
Default: 60 Sekunden

💡 Wie oft die Sensoren aktualisiert werden
💡 Höher = weniger Netzwerk-Last, aber weniger aktuell
```

#### Log-Level
```
🔴 ERROR    - Nur Fehler (Produktion)
🟡 WARN     - Warnungen + Fehler
🔵 INFO     - Informationen (Normal)
🟣 DEBUG    - Alles (Debugging/Troubleshooting)

💡 DEBUG ist nur für Fehlersuche nötig
💡 In Produktion ERROR verwenden
```

### All-in-One Modus (Zusätzlich)

#### Serielles Gerät
```
Automatische Erkennung:
- /dev/ttyUSB0    (USB-Adapter)
- /dev/ttyACM0    (Arduino-style)
- COM3             (Windows)
- /dev/ttyS0      (Serieller Port)

oder manuell eingeben
```

#### Protokoll
```
KW (Standard)
└─ Für die meisten Viessmann Heizungen
└─ Verwendet Komfortsignal-Protokoll

Raw
└─ Binäres Protokoll ohne Formatierung

Framing
└─ Alternativ für spezielle Heizungsmodelle
```

### Externe vcontrold Modus (Zusätzlich)

#### Host/IP
```
Beispiele:
- localhost        (Gleicher Server)
- 127.0.0.1        (Loopback)
- 192.168.1.100    (Anderer Server im Netz)
- heating.local    (mDNS)
```

#### Port
```
Standard: 3002
Range: 1024-65535
```

## 🎮 Einstellungen nachträglich ändern

Nach der Installation kannst du Einstellungen ändern ohne Neustart:

### Schritt-für-Schritt:

1. **Settings** → **Devices & Services**
2. Suche: `vcontrold`
3. Klick auf deine Integration
4. Klick **"Configure"** (oder Zahnrad-Icon)
5. Passe Einstellungen an:
   - Update-Intervall
   - Log-Level
   - Port (nur All-in-One)
6. Klick **"Submit"**

Die neue Konfiguration wird sofort geladen! ✅

## 📱 Responsive Design

Die GUI passt sich automatisch an:
- ✅ Desktop (volle Breite)
- ✅ Tablet (optimiert)
- ✅ Mobile (kompakt)

## 🌍 Multi-Language Support

Alle Felder haben:
- ✅ Deutsche Labels
- ✅ Deutsche Beschreibungen
- ✅ Englische Fallback-Texte
- ✅ Emoji für visuelle Hilfe

## 🎨 UI-Elemente

### Text-Eingabe
```yaml
Host: "localhost"
Device: "/dev/ttyUSB0"
```

### Schieberegler / Bereich
```yaml
Update-Intervall: ▼────●────▲  (30-300s)
Port: ▼────●────▲  (1024-65535)
```

### Dropdown-Auswahl
```yaml
Log-Level: [🔴 ERROR ▼]
Protokoll: [KW (Standard) ▼]
Modus: [🔧 All-in-One ▼]
```

### Validierung

Die GUI validiert:
- ✅ Port-Nummern (1024-65535)
- ✅ Update-Intervall (30-300s)
- ✅ TCP-Verbindungen
- ✅ Device-Existenz
- ✅ Host-Auflösbarkeit

Fehlerhafte Eingaben werden mit Error-Meldung gekennzeichnet:
```
❌ "cannot_connect" - Verbindung fehlgeschlagen
❌ "connection_error" - Netzwerkfehler
❌ "unknown_error" - Unbekannter Fehler
```

## 💡 Tipps & Tricks

### Erste Installation
1. Wähle "🔧 All-in-One" (Standard empfohlen)
2. Lass alles auf Default, nur Gerät ändern
3. Klick "Submit"
4. Sensoren sollten laden

### Erweiterte Einstellungen
Nach erfolgreichem Setup kannst du noch anpassen:
- Log-Level auf DEBUG für Troubleshooting
- Update-Intervall erhöhen bei Timeout-Problemen
- Port ändern bei Konflikten

### Remote Setup (Extern)
Wenn vcontrold auf anderem Server:
1. Wähle "🌐 Externe vcontrold"
2. Gib Host-IP ein (z.B. 192.168.1.100)
3. Gib Port ein (meist 3002)
4. Test-Verbindung wird automatisch geprüft

## 🔍 Screenshot-Beschreibung

### Schritt 1: Modus
```
┌─────────────────────────────────┐
│ vcontrold Integration           │
│                                 │
│ Wähle Setup-Modus:              │
│ ○ 🔧 HA verwaltet (Standard)    │
│ ○ 🌐 Externe vcontrold          │
│                                 │
│  [Zurück] [Weiter]              │
└─────────────────────────────────┘
```

### Schritt 2a: Gerät (All-in-One)
```
┌─────────────────────────────────┐
│ vcontrold Integration           │
│ (Schritt 1 von 3)               │
│                                 │
│ Serielles Gerät:                │
│ ┌─────────────────────────────┐ │
│ │ /dev/ttyUSB0 (USB Adapter)▼│ │
│ └─────────────────────────────┘ │
│                                 │
│ 💡 Wähle das USB-Gerät          │
│    für deine Heizung            │
│                                 │
│  [Zurück] [Weiter]              │
└─────────────────────────────────┘
```

### Schritt 2b: Netzwerk (All-in-One)
```
┌─────────────────────────────────┐
│ vcontrold Integration           │
│ (Schritt 2 von 3)               │
│                                 │
│ Host:                           │
│ ┌─────────────────────────────┐ │
│ │ localhost                   │ │
│ └─────────────────────────────┘ │
│                                 │
│ Port:                           │
│ ┌─────────────────────────────┐ │
│ │ 3002                        │ │
│ └─────────────────────────────┘ │
│                                 │
│  [Zurück] [Weiter]              │
└─────────────────────────────────┘
```

### Schritt 2c: Erweitert (All-in-One)
```
┌─────────────────────────────────┐
│ vcontrold Integration           │
│ (Schritt 3 von 3)               │
│                                 │
│ Update-Intervall (Sekunden):    │
│ ┌─────────────────────────────┐ │
│ │ 60                          │ │
│ └─────────────────────────────┘ │
│ 30─────────60─────────300       │
│                                 │
│ Log-Level:                      │
│ ┌─────────────────────────────┐ │
│ │ 🔴 ERROR (nur Fehler)      ▼│ │
│ └─────────────────────────────┘ │
│                                 │
│ Protokoll:                      │
│ ┌─────────────────────────────┐ │
│ │ KW (Standard)              ▼│ │
│ └─────────────────────────────┘ │
│                                 │
│  [Zurück] [Fertig]              │
└─────────────────────────────────┘
```

## 🔧 Nachträgliche Einstellungen

```
Settings → Devices & Services
          ↓
vcontrold Integration
├─ Device/Service Instances
│  └─ vcontrold
│     ├─ Sensoren (3 Stück)
│     └─ Services (5 Services)
│
└─ Drei-Punkt-Menu
   └─ [Configure] ← HIER KLICKEN
      ↓
   Einstellungs-Dialog
   ├─ Update-Intervall
   ├─ Log-Level
   └─ Port (nur All-in-One)
      ↓
   [Submit] → Sofort aktiv!
```

## 📊 Geplante UI-Erweiterungen

Für zukünftige Versionen geplant:
- [ ] Echtzeit Daemon-Status im UI
- [ ] Graphische Netzwerk-Topologie
- [ ] Advanced Logging UI
- [ ] Diagnostic Report Button
- [ ] Dark/Light Theme Support

---

**Die GUI ist so einfach, dass selbst Anfänger die Integration in 2 Minuten einrichten können!** 🚀
