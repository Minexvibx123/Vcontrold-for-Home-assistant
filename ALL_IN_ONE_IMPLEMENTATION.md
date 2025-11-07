# ALL-IN-ONE Integration - vcontrold Bundled with Home Assistant Integration

Die Integration bringt vcontrold mit (All-in-One = alles in einem Paket).

## 📦 Repository Struktur für ALL-IN-ONE

```
custom_components/vcontrold/
├── __init__.py                    # Integration Einstiegspunkt
├── config_flow.py                 # Setup GUI
├── manifest.json                  # Integration Metadaten
├── sensor.py                      # 5 Sensoren
├── services.yaml                  # Service Definitionen
├── strings.json                   # Translations
├── const.py                       # Konstanten
├── heating_controller.py          # Controller Logik
├── vcontrold_manager.py          # TCP Manager für vcontrold
├── daemon_manager.py             # Startet/Überwacht vcontrold
├── translations/
│   └── en.json
├── vcontrold/                     # 🆕 vcontrold Binaries!
│   ├── linux/
│   │   ├── vcontrold             # 64-bit Linux Binary
│   │   └── vcontrold-arm         # 32-bit ARM (Raspberry Pi)
│   ├── windows/
│   │   └── vcontrold.exe         # Windows Binary
│   └── macos/
│       └── vcontrold             # macOS Binary
└── vcontrold_configs/            # 🆕 Config Templates
    └── vcontrold.conf.template
```

## 🚀 Wie es funktioniert (ALL-IN-ONE)

### Installation
```
User installiert Integration via HACS
  ↓
Integration wird installiert mit allen vcontrold Binaries
  ↓
Integration startet automatisch vcontrold im Hintergrund
  ↓
vcontrold läuft auf localhost:3002
  ↓
Integration verbindet sich automatisch
  ↓
5 Sensoren erscheinen in Home Assistant
```

### Automatischer Start
```python
# In __init__.py oder daemon_manager.py:

async def async_setup_entry(hass, entry):
    # Starte vcontrold Daemon automatisch
    daemon = VcontroledDaemonManager()
    
    # Wähle richtige Binary je nach OS
    if platform == "linux":
        vcontrold_binary = "custom_components/vcontrold/vcontrold/linux/vcontrold"
    elif platform == "windows":
        vcontrold_binary = "custom_components/vcontrold/vcontrold/windows/vcontrold.exe"
    elif platform == "macos":
        vcontrold_binary = "custom_components/vcontrold/vcontrold/macos/vcontrold"
    
    # Starte vcontrold mit USB-Port
    await daemon.start_daemon(
        binary_path=vcontrold_binary,
        device="/dev/ttyUSB0"  # oder COM3 auf Windows
    )
```

## ⚙️ Anforderungen für ALL-IN-ONE

### vcontrold Binaries
- Linux x86_64
- Linux ARM (Raspberry Pi)
- Windows x86_64
- macOS x86_64 + ARM64

### Dateigrößen
- Linux Binary: ~500KB - 2MB
- Windows Binary: ~500KB - 2MB
- macOS Binary: ~500KB - 2MB
- **Total**: ~5-10MB (ganz akzeptabel)

## 🔧 Implementierung

### Schritt 1: vcontrold Binaries beschaffen
```bash
# Kompilieren oder herunterladen von vcontrold Projekt
# https://github.com/openv/vcontrold

# Linux
mkdir -p custom_components/vcontrold/vcontrold/linux
cp /usr/bin/vcontrold custom_components/vcontrold/vcontrold/linux/vcontrold
chmod +x custom_components/vcontrold/vcontrold/linux/vcontrold

# Windows
mkdir -p custom_components/vcontrold/vcontrold/windows
cp vcontrold.exe custom_components/vcontrold/vcontrold/windows/vcontrold.exe

# macOS
mkdir -p custom_components/vcontrold/vcontrold/macos
cp vcontrold custom_components/vcontrold/vcontrold/macos/vcontrold
chmod +x custom_components/vcontrold/vcontrold/macos/vcontrold
```

### Schritt 2: daemon_manager.py updaten
```python
class VcontroledDaemonManager:
    
    def _get_daemon_binary_path(self):
        """Finde vcontrold Binary (bundled mit Integration)."""
        integration_dir = Path(__file__).parent
        
        if platform.system() == "Linux":
            if platform.machine() == "armv7l":
                return integration_dir / "vcontrold" / "linux" / "vcontrold-arm"
            else:
                return integration_dir / "vcontrold" / "linux" / "vcontrold"
        elif platform.system() == "Windows":
            return integration_dir / "vcontrold" / "windows" / "vcontrold.exe"
        elif platform.system() == "Darwin":  # macOS
            return integration_dir / "vcontrold" / "macos" / "vcontrold"
```

### Schritt 3: __init__.py updaten
```python
async def async_setup_entry(hass, entry):
    """Setup mit automatischem vcontrold Start."""
    
    # Daemon Manager mit bundled Binary
    daemon_manager = VcontroledDaemonManager(
        config_dir=hass.config.path()
    )
    
    # Starte vcontrold automatisch
    await daemon_manager.start_daemon(
        device=entry.data.get(CONF_DEVICE),
        auto_deploy=True  # Nutze bundled Binary
    )
    
    # Warte bis vcontrold aktiv ist
    await asyncio.sleep(2)
    
    # Verbinde Integration
    manager = VcontroledManager(...)
    await manager.check_connection()
```

## ✅ Vorteil: ALL-IN-ONE

**Für User:**
- Installiert über HACS
- Alles lädt automatisch
- Keine separate vcontrold Installation
- Funktioniert sofort nach Setup

**Für Developer:**
- Integration ist komplett
- Keine externen Dependencies
- Einfacher zu debuggen
- Standardisierte vcontrold Version

## ⚠️ Lizenz & Copyright

vcontrold ist OpenSource (GPL):
- Muss Lizenz kopieren
- Muss Source Code verfügbar machen
- Muss angemessen attribuieren

```
LICENSE: GPL-2.0
vcontrold Source: https://github.com/openv/vcontrold
```

## 🎯 Implementierungs-Checkliste

- [ ] vcontrold Binaries für alle Plattformen beschaffen
- [ ] vcontrold/linux/, windows/, macos/ Ordner erstellen
- [ ] Binaries in Repository einfügen
- [ ] daemon_manager.py updaten (bundled Binary Pfade)
- [ ] __init__.py updaten (auto-deploy)
- [ ] LICENSE für vcontrold hinzufügen
- [ ] CHANGELOG updaten
- [ ] Tests schreiben
- [ ] Release v2.1.0
