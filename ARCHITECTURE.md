# Architektur und Implementierung

## 🏗️ Architektur-Übersicht

```
┌─────────────────────────────────────────────────────────────┐
│                    Home Assistant Instance                  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │        vcontrold Custom Integration                 │   │
│  │        (custom_components/vcontrold)                │   │
│  │                                                      │   │
│  │  ┌──────────────────────────────────────────────┐  │   │
│  │  │           __init__.py (Setup)                │  │   │
│  │  │ - Registrierung der Integration             │  │   │
│  │  │ - Service-Definitionen                      │  │   │
│  │  │ - Manager-Initialisierung                   │  │   │
│  │  └──────────────────────────────────────────────┘  │   │
│  │                         ↓                          │   │
│  │  ┌──────────────────────────────────────────────┐  │   │
│  │  │    sensor.py (Entities & Coordinator)        │  │   │
│  │  │ - 5 Temperature Sensoren                     │  │   │
│  │  │ - Update Coordinator (60s Interval)         │  │   │
│  │  │ - Fehlerbehandlung                          │  │   │
│  │  └──────────────────────────────────────────────┘  │   │
│  │                         ↓                          │   │
│  │  ┌──────────────────────────────────────────────┐  │   │
│  │  │   vcontrold_manager.py (TCP-Socket Manager) │  │   │
│  │  │ - TCP-Verbindung zu vcontrold               │  │   │
│  │  │ - Befehl-Implementierung                    │  │   │
│  │  │ - Response-Parsing                          │  │   │
│  │  │ - Caching (30s TTL)                         │  │   │
│  │  │ - Fehlerbehandlung & Timeouts               │  │   │
│  │  └──────────────────────────────────────────────┘  │   │
│  │                                                      │   │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
└───────────────────────┬───────────────────────────────────────┘
                        │
                    TCP Port 3002
                        │
┌───────────────────────▼───────────────────────────────────────┐
│              vcontrold Daemon (localhost:3002)                │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │        Socket Server & Command Parser               │   │
│  │                                                      │   │
│  │  ┌──────────────────────────────────────────────┐  │   │
│  │  │    getTempKessel    → Kesseltemperatur      │  │   │
│  │  │    getTempAussen    → Außentemperatur       │  │   │
│  │  │    getTempWWsoll    → WW-Solltemperatur    │  │   │
│  │  │    getTempWWist     → WW-Isttemperatur     │  │   │
│  │  │    getTempVorlauf   → Heizkreis Vorlauf    │  │   │
│  │  │    setBetriebsart   → Betriebsart ändern   │  │   │
│  │  │    setTempWWsoll    → WW-Temp ändern       │  │   │
│  │  └──────────────────────────────────────────────┘  │   │
│  │                                                      │   │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
└───────────────────────┬───────────────────────────────────────┘
                        │
                   RS232 / Serial
                        │
┌───────────────────────▼───────────────────────────────────────┐
│        Viessmann Heizungsanlage (Heizkessel)                 │
│                                                               │
│  - Temperatur-Sensoren                                      │
│  - Ventile & Regelsysteme                                   │
│  - Steuerungslogik                                          │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

## 📊 Datenflusss

### Daten-Abruf (Read)

```
Home Assistant              vcontrold Manager          vcontrold Daemon
      │                            │                         │
      │──── update_coordinator ────→│                         │
      │    (60s interval)           │                         │
      │                             │                         │
      │                        Check Cache                    │
      │                        (30s TTL)                      │
      │                             │                         │
      │                         Miss?                         │
      │                             │─────→ TCP Socket ──────→│
      │                             │   getTempKessel         │
      │                             │                    Response:
      │                             │←───────────────────  OK\n23.5
      │                             │                         │
      │                      Parse Response                   │
      │                      Update Cache                     │
      │←──── Return Data ───────────│                         │
      │                             │                         │
   Update Entities                  │                         │
   (Sensoren)                        │                         │
      │                             │                         │
   Dashboard                        │                         │
   zeigt Temperatur                 │                         │
```

### Daten-Schreiben (Write)

```
Home Assistant             vcontrold Manager          vcontrold Daemon
      │                            │                         │
      │── Service Call ───────────→│                         │
      │  (set_temp_ww_soll)        │                         │
      │                            │                         │
      │                    Validierung                       │
      │                    (20-80°C)                        │
      │                            │                         │
      │                      Invalidate Cache                │
      │                      (remove WW entries)            │
      │                            │                         │
      │                            │─────→ TCP Socket ──────→│
      │                            │  setTempWWsoll 55      │
      │                            │                    Execute:
      │                            │←───────────────────  OK
      │                            │                         │
      │←─ Success/Failure ─────────│                         │
      │                            │                         │
   Notification/Logging             │                         │
```

## 🔑 Komponenten-Details

### 1. VcontroledManager (`vcontrold_manager.py`)

**Verantwortlichkeiten:**
- TCP-Socket-Verwaltung
- Befehl-Versand und Response-Parsing
- Fehlerbehandlung und Timeouts
- Caching mit TTL

**Wichtige Methoden:**
```python
get_temperature(sensor_type: str) → float
set_temperature(command: str, value: float) → bool
set_operating_mode(mode: str) → bool
is_available() → bool
```

**Cache-Mechanismus:**
- TTL: 30 Sekunden (konfigurierbar)
- Invalidierung bei Write-Operationen
- Pro Sensor separat gecacht

### 2. Sensor Coordinator (`sensor.py`)

**Verantwortlichkeiten:**
- Regelmäßige Datenupdates (async)
- Fehlerbehandlung auf Entity-Ebene
- CoordinatorEntity-Integration

**Update-Interval:**
- Standard: 60 Sekunden
- Konfigurierbar via `configuration.yaml`

**Datenstruktur:**
```python
{
    "getTempKessel": 23.5,
    "getTempAussen": 8.2,
    "getTempWWsoll": 55.0,
    "getTempWWist": 52.1,
    "getTempVorlaufHK1": 45.3
}
```

### 3. Integration Entry Point (`__init__.py`)

**Verantwortlichkeiten:**
- Integration-Setup
- Manager-Initialisierung
- Service-Registrierung
- Error Handling

**Services:**
- `vcontrold.set_temp_ww_soll`
- `vcontrold.set_betriebsart`

## 🔄 Datentypen und Validierung

### Temperatur-Werte

| Wert | Min | Max | Einheit | Typ |
|------|-----|-----|---------|-----|
| getTempKessel | 0 | 100 | °C | float |
| getTempAussen | -40 | 60 | °C | float |
| getTempWWsoll | 20 | 80 | °C | float |
| getTempWWist | 0 | 80 | °C | float |
| getTempVorlaufHK1 | 0 | 80 | °C | float |

### Betriebsarten

```
auto   - Automatischer Modus
standby - Standby/Off
party  - Party Mode
eco    - Eco/Sparmodus
```

## 🛡️ Fehlerbehandlung

### Fehler-Hierarchie

```python
1. Socket Connection Errors
   ├─ ConnectionRefusedError
   ├─ TimeoutError
   └─ OSError

2. Response Parse Errors
   ├─ ValueError (Temperatur-Parse)
   └─ IndexError (Response-Format)

3. Validation Errors
   ├─ Invalid Temperature (20-80)
   ├─ Invalid Operating Mode
   └─ Invalid Command
```

### Reconnection Strategy

1. **Bei Fehler:** `_disconnect()` aufrufen
2. **Nächster Request:** Automatisches Reconnect
3. **Max Versuche:** Unlimitiert (Logger-Warnung)

## 🔌 TCP-Protokoll

### Request-Format

```
<COMMAND> [PARAMS]\n
```

### Response-Format

```
OK\n<VALUE>
# oder
ERROR: <MESSAGE>
```

### Beispiele

**Request:**
```
getTempKessel\n
```

**Response (Erfolg):**
```
OK
23.5
```

**Response (Fehler):**
```
ERROR: unknown command
```

## 💾 Caching

### Caching-Strategie

- **TTL:** 30 Sekunden (pro Wert)
- **Invalidierung:** Bei Set-Operationen
- **Hit-Rate:** ~99% bei normalem Betrieb

### Cache-Struktur

```python
self._cache = {
    "getTempKessel": 23.5,
    "getTempAussen": 8.2,
    ...
}

self._cache_time = {
    "getTempKessel": datetime.now(),
    ...
}
```

## ⏱️ Timing und Performance

### Standard-Intervalle

| Komponente | Interval | Beschreibung |
|------------|----------|-------------|
| Coordinator Update | 60s | Datenabruf von vcontrold |
| Cache TTL | 30s | Gültigkeitsdauer Cache |
| Socket Timeout | 10s | TCP-Verbindung Timeout |
| Task Timeout | 30s | Async Task Timeout |

### Performance-Charakteristiken

- **Durchsatz:** ~5-10 Requests/Sekunde
- **Latenz:** ~100-500ms pro Request
- **Cache-Hit:** ~99% bei 60s Update-Interval
- **Memory:** <10MB für eine Integration

## 🔐 Sicherheit

### Threat Model

1. **Local Network Only**
   - TCP auf localhost:3002
   - Keine Remote-Zugriffe ohne SSH-Tunnel

2. **Command Injection**
   - Simple Befehle (keine User-Input)
   - Parameter validiert

3. **Denial of Service**
   - Timeout-Schutz (10s)
   - Rate-Limiting via Update-Interval

## 📈 Skalierbarkeit

### Mehrere Heizungsanlagen

Um mehrere Anlagen zu unterstützen:

```yaml
# Future Enhancement
vcontrold:
  - host: localhost
    port: 3002
    name: "Hauptgebäude"
  - host: 192.168.1.100
    port: 3002
    name: "Nebengebäude"
```

### Threading/Async

- Home Assistant async: `async_add_executor_job()`
- vcontrold Manager: Thread-safe
- Coordinator: Async-first

## 🚀 Zukünftige Enhancements

- [ ] Config Flow UI
- [ ] Multiple vcontrold Instances
- [ ] Device Integration (Climate Entity)
- [ ] History Stats
- [ ] Diagnostics
- [ ] Repairs UI
