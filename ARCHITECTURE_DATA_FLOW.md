# Datenfluss & USB-Port Integration - Vcontrold für Home Assistant

## 🎯 Übersicht: Wie Daten fließen

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          HOME ASSISTANT                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ VCONTROLD INTEGRATION (custom_components/vcontrold/)            │   │
│  │                                                                  │   │
│  │  1. __init__.py                                                │   │
│  │     └─ Lädt Integration                                        │   │
│  │     └─ Startet Daemon Manager                                 │   │
│  │     └─ Registriert Services                                   │   │
│  │                                                                  │   │
│  │  2. sensor.py (Datensammlung)                                  │   │
│  │     ├─ DataUpdateCoordinator (60s Update)                      │   │
│  │     ├─ 5 Sensor Entities                                       │   │
│  │     │  ├─ Kesseltemperatur                                     │   │
│  │     │  ├─ Außentemperatur                                      │   │
│  │     │  ├─ Warmwasser-Solltemp                                  │   │
│  │     │  ├─ Warmwasser-Isttemp                                   │   │
│  │     │  └─ Heizkreis Vorlauftemp                                │   │
│  │     └─ Cache (30s TTL)                                         │   │
│  │                                                                  │   │
│  │  3. vcontrold_manager.py (TCP Kommunikation)                  │   │
│  │     ├─ Verbindet zu vcontrold Daemon                          │   │
│  │     ├─ Sendet Befehle (getTempKessel, etc.)                   │   │
│  │     ├─ Empfängt Daten                                          │   │
│  │     └─ 30s Cache (Daten nicht zu oft abfragen)                │   │
│  │                                                                  │   │
│  │  4. daemon_manager.py (Daemon Verwaltung)                     │   │
│  │     ├─ Startet/Stoppt vcontrold Daemon                        │   │
│  │     ├─ Überwacht Daemon-Status                                │   │
│  │     └─ Health Checks                                           │   │
│  │                                                                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                     ↓                                    │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ TCP SOCKET VERBINDUNG (localhost:3002)                         │   │
│  │  - asynchrone Kommunikation                                    │   │
│  │  - Timeout Protection (10 Sekunden)                            │   │
│  │  - Fehlerbehandlung & Reconnect                                │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                     ↓                                    │
└─────────────────────────────────────────────────────────────────────────┘
                                     ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                      VCONTROLD DAEMON                                    │
│                  (externe Software, nicht HA)                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  TCP Server Port 3002 (localhost)                                       │
│      ↓                                                                   │
│  Befehle verarbeiten:                                                   │
│      - getTempKessel                                                    │
│      - getTempAussen                                                    │
│      - getTempWWsoll                                                    │
│      - setBetriebsart                                                   │
│      - setTempWWsoll                                                    │
│      ↓                                                                   │
│  VCONTROLD KERNEL MODUL (RS232/Serien-Daten)                          │
│      ↓                                                                   │
└─────────────────────────────────────────────────────────────────────────┘
                                     ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                    USB ↔ RS232 ADAPTER                                   │
│                                                                           │
│  /dev/ttyUSB0  (Linux)                                                  │
│  COM3           (Windows)                                               │
│  /dev/cu.usbserial (macOS)                                             │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
                                     ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                  VIESSMANN HEIZANLAGE                                    │
│                                                                           │
│  Vitotronic 300 (oder 200, Vitola 300)                                │
│                                                                           │
│  ├─ Kesseltemperatur Sensor                                            │
│  ├─ Außentemperatur Sensor                                             │
│  ├─ Warmwasser Solltemperatur                                          │
│  ├─ Warmwasser Isttemperatur                                           │
│  └─ Heizkreis Vorlauftemperatur                                        │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Wo werden die Daten gesammelt?

### 1. **sensor.py** - Hauptsammelpunkt

Die Sensoren werden in `sensor.py` definiert:

```python
# 5 Sensoren für Temperaturmessung
sensors = [
    VcontroledTemperatureSensor(coordinator, "getTempKessel", "Kesseltemperatur"),
    VcontroledTemperatureSensor(coordinator, "getTempAussen", "Außentemperatur"),
    VcontroledTemperatureSensor(coordinator, "getTempWWsoll", "Warmwasser-Soll"),
    VcontroledTemperatureSensor(coordinator, "getTempWWist", "Warmwasser-Ist"),
    VcontroledTemperatureSensor(coordinator, "getTempVorlaufHK1", "Vorlauf"),
]
```

**Speicherort:** `hass.data['vcontrold']['<entry_id>']`

### 2. **DataUpdateCoordinator** - Automatisches Polling

```python
class VcontroledDataUpdateCoordinator(DataUpdateCoordinator):
    """Koordiniert Datenupdates alle 60 Sekunden."""
    
    SCAN_INTERVAL = timedelta(seconds=60)  # Neue Daten alle 60 Sekunden
    
    async def _async_update_data(self):
        """Hole Daten vom Controller."""
        return await self.controller.get_all_temps()  # 5 Sensoren
```

**Update-Intervall:** 60 Sekunden (konfigurierbar)

### 3. **Cache-System** - Performance

```python
# 30 Sekunden Cache TTL
self._cache_ttl = 30

# Wenn 30s nicht abgelaufen sind, nutze Cache
if self._is_cache_valid("getTempKessel"):
    return self._cache["getTempKessel"]  # Schnell!
else:
    # Sonst neue Daten vom vcontrold Daemon
    response = await self._send_command("getTempKessel")
```

**Speicherort:** RAM im Controller-Objekt (temporär)

---

## 🔌 Wie bezieht das System den USB-Port?

### Schritt 1: Daemon Manager findet den Port

**Datei:** `daemon_manager.py`

```python
class VcontroledDaemonManager:
    """Verwaltet vcontrold Daemon und USB-Gerät."""
    
    def __init__(self, device="/dev/ttyUSB0"):
        self.device = device  # USB-Port
        self.port = 3002      # TCP Port für HA
```

### Schritt 2: User konfiguriert den Port

**Datei:** `config_flow.py`

```python
async def async_step_user(self, user_input=None):
    """Setup Wizard."""
    
    if user_input is not None:
        device = user_input["device"]  # z.B. "/dev/ttyUSB0"
        host = user_input["host"]      # z.B. "localhost"
        port = user_input["port"]      # z.B. 3002
        
        return self.async_create_entry(
            title="vcontrold",
            data={
                "device": device,       # USB-Port speichern
                "host": host,           # Host speichern
                "port": port,           # TCP Port speichern
            }
        )
```

### Schritt 3: Daemon wird gestartet

**Datei:** `__init__.py`

```python
async def async_setup_entry(hass, entry):
    device = entry.data.get(CONF_DEVICE)  # "/dev/ttyUSB0"
    host = entry.data.get("host", "localhost")
    port = entry.data.get("port", 3002)
    
    # Daemon Manager mit USB-Port
    daemon_manager = VcontroledDaemonManager(device=device)
    
    # Starte Daemon
    await daemon_manager.start_daemon()
    # → vcontrold -p /dev/ttyUSB0
    
    # vcontrold läuft nun auf localhost:3002
```

### Schritt 4: TCP Verbindung nutzen

**Datei:** `vcontrold_manager.py`

```python
async def _send_command(self, command: str):
    """Sende Befehl zu vcontrold."""
    
    # Verbinde zu vcontrold auf localhost:3002
    self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self._socket.connect((self.host, self.port))  # localhost:3002
    
    # Sende Befehl
    self._socket.sendall(f"{command}\n".encode())
    
    # Empfange Antwort
    response = self._socket.recv(1024).decode()
    
    return response
```

---

## 🔄 Datenfluss Beispiel: "getTempKessel"

```
1. Home Assistant startet Integration
   ↓
2. sensor.py erstellt Sensor "Kesseltemperatur"
   ↓
3. DataUpdateCoordinator alle 60s:
   ↓
4. Ruft vcontrold_manager.getTempKessel() auf
   ↓
5. Prüft Cache (30s TTL):
   ├─ Cache valid? → Return Cache (schnell)
   └─ Cache expired? → Continue
   ↓
6. TCP Socket verbindet zu vcontrold (localhost:3002)
   ↓
7. Sendet: "getTempKessel\n"
   ↓
8. vcontrold empfängt Befehl
   ↓
9. vcontrold nutzt USB /dev/ttyUSB0 zur Heizanlage
   ↓
10. vcontrold liest Kesseltemperatur von Heizanlage
    ↓
11. vcontrold antwortet: "42.5\n"
    ↓
12. TCP Socket empfängt "42.5"
    ↓
13. Speichere in Cache (TTL 30s)
    ↓
14. Rückgabe an sensor.py: 42.5°C
    ↓
15. Sensor wird aktualisiert in Home Assistant
    ↓
16. Nächste Update in 60 Sekunden
```

---

## 📋 Zusammenfassung: Datenfluss

| Komponente | Funktion | Speicher | Update |
|-----------|----------|---------|--------|
| **sensor.py** | Sammelt 5 Sensoren | hass.data | 60s |
| **vcontrold_manager.py** | TCP-Befehle an Daemon | Cache (30s) | On-Demand |
| **daemon_manager.py** | Startet vcontrold Daemon | Linux Prozess | Boot-Zeit |
| **vcontrold Daemon** | Umwandlung USB ↔ Befehle | Extern | Echtzeit |
| **/dev/ttyUSB0** | USB-Seriell-Verbindung | Hardware | Echtzeit |
| **Heizanlage** | Sensoren & Stellglieder | Heizanlage | Echtzeit |

---

## 🔧 USB-Port Konfiguration

### Linux
```bash
# Finde USB-Adapter
ls -la /dev/ttyUSB*
# Ergebnis: /dev/ttyUSB0

# In Home Assistant konfigurieren: /dev/ttyUSB0
```

### Windows
```bash
# Geräte-Manager prüfen
# Serielle Anschlüsse: COM3 (oder höher)

# In Home Assistant konfigurieren: COM3
```

### macOS
```bash
# Finde Adapter
ls /dev/cu.usb*
# Ergebnis: /dev/cu.usbserial-0000

# In Home Assistant konfigurieren: /dev/cu.usbserial-0000
```

---

## ⚡ Performance-Tipps

### Cache-System optimieren
```python
# Standard: 30s Cache
cache_ttl = 30

# Weniger Requests an Daemon
# → Bessere Performance
# → Weniger USB-Zugiffe
```

### Update-Intervall anpassen
```python
# Standard: 60 Sekunden
UPDATE_INTERVAL = 60

# Für schnellere Reaktion: 30s
# Für bessere Performance: 120s
```

### Services sind sofort
```python
# Services warten NICHT auf Coordinator
# "Warmwasser auf 50°C setzen" erfolgt SOFORT
# (Nicht erst beim nächsten 60s Update)
```

---

## 📊 Live-Daten in Home Assistant

Alle Sensoren werden in Home Assistant verfügbar:

```yaml
# Automatisch verfügbar nach Installation:
sensor.vcontrold_kesseltemperatur           # 42.5°C
sensor.vcontrold_aussentemperatur            # 12.3°C
sensor.vcontrold_warmwasser_solltemperatur   # 55.0°C
sensor.vcontrold_warmwasser_isttemperatur    # 54.2°C
sensor.vcontrold_heizkreis_vorlauftemperatur # 48.1°C

# Nutze in Automationen:
{{ states('sensor.vcontrold_kesseltemperatur') }}
```

---

## 🎯 Zusammenfassung

**Wo werden Daten gesammelt:**
- `sensor.py` - 5 Sensor-Entities
- `hass.data['vcontrold']` - Speicherung
- RAM Cache (30s TTL) - Optimierung
- DataUpdateCoordinator (60s) - Polling

**Wie nutzt das System den USB-Port:**
1. User konfiguriert Port (`/dev/ttyUSB0`, `COM3`, etc.)
2. daemon_manager.py startet vcontrold mit dem Port
3. vcontrold nutzt den Port zur Kommunikation mit Heizanlage
4. vcontrold läuft auf TCP Port 3002 (localhost)
5. Home Assistant verbindet sich via TCP (nicht direkt USB)
6. Alle Kommunikation läuft über TCP-Sockets

**Vorteil:** USB-Kommunikation ist isoliert im vcontrold Daemon!
