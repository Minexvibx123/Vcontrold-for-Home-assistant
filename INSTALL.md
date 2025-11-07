# Installationsanleitung: vcontrold Integration für Home Assistant

Diese Anleitung führt dich Schritt für Schritt durch die Installation und Konfiguration der vcontrold Integration für Home Assistant.

## Voraussetzungen

Bevor du beginnst, stelle sicher, dass folgende Komponenten installiert und läuft:

### 1. Home Assistant
- **Version**: Mindestens 2024.1.0
- **Installation**: Docker, HAOS oder manuell auf Linux/Raspberry Pi
- **Zugriff**: WebUI unter `http://<HOME_ASSISTANT_IP>:8123`

### 2. vcontrold Daemon
- **Installation**: Muss auf dem gleichen Netzwerk laufen
- **Standard Port**: 3002 (TCP)
- **Check**: `telnet localhost 3002` oder `nc -zv localhost 3002`

### 3. Viessmann Heizungsanlage
- **Kompatibilität**: Muss von vcontrold unterstützt werden
- **Verbindung**: RS232 oder ähnlich zu vcontrold Damon

## Schritt 1: Integration herunterladen

### Option A: Git Clone (empfohlen)

```bash
cd /tmp
git clone https://github.com/Minexvibx123/Vcontrold-for-Home-assistant.git
```

### Option B: Manueller Download

1. Gehe zu https://github.com/Minexvibx123/Vcontrold-for-Home-assistant
2. Klick auf "Code" → "Download ZIP"
3. Entpacke die ZIP-Datei

## Schritt 2: Integration in Home Assistant einbinden

### Auf dem Host mit Home Assistant

```bash
# Navigiere zum Home Assistant Config-Verzeichnis
cd ~/.homeassistant
# oder bei Docker:
cd /path/to/homeassistant/config

# Erstelle das custom_components Verzeichnis (falls nicht vorhanden)
mkdir -p custom_components

# Kopiere die Integration
cp -r /path/to/Vcontrold-for-Home-assistant/vcontrold custom_components/
```

### Verzeichnisstruktur überprüfen

Nach dem Kopieren sollte folgende Struktur existieren:

```
~/.homeassistant/
├── custom_components/
│   └── vcontrold/
│       ├── __init__.py
│       ├── manifest.json
│       ├── config_flow.py
│       ├── const.py
│       ├── sensor.py
│       ├── vcontrold_manager.py
│       ├── services.yaml
│       ├── strings.json
│       ├── translations/
│       │   └── en.json
│       └── [weitere Dateien]
├── configuration.yaml
└── [weitere Dateien]
```

## Schritt 3: Home Assistant Konfiguration

### Methode 1: YAML-Konfiguration (empfohlen)

Bearbeite deine `configuration.yaml`:

```bash
nano ~/.homeassistant/configuration.yaml
```

Füge folgende Zeilen am Ende hinzu:

```yaml
# vcontrold Integration
vcontrold:
  host: localhost
  port: 3002
  update_interval: 60
```

**Konfigurationsoptionen:**

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|-------------|
| `host` | string | `localhost` | Hostname oder IP des vcontrold Daemons |
| `port` | integer | `3002` | TCP-Port des vcontrold Daemons |
| `update_interval` | integer | `60` | Update-Intervall in Sekunden (min. 30) |

**Beispiele:**

*Lokaler vcontrold (auf gleicher Maschine):*
```yaml
vcontrold:
  host: localhost
  port: 3002
```

*Remote vcontrold (andere IP):*
```yaml
vcontrold:
  host: 192.168.1.100
  port: 3002
  update_interval: 120
```

### Methode 2: Konfiguration via WebUI (zukünftig)

(Wird in zukünftigen Versionen unterstützt)

## Schritt 4: Home Assistant neu starten

### Methode A: Docker

```bash
docker restart homeassistant
```

### Methode B: HAOS/systemd

```bash
sudo systemctl restart homeassistant
```

### Methode C: WebUI

1. Öffne http://<HOME_ASSISTANT_IP>:8123
2. Gehe zu "Settings" → "System" → "Restart" → "Restart Home Assistant"

### Methode D: Terminal in Home Assistant

```bash
# SSH zu Home Assistant
ssh root@<HOME_ASSISTANT_IP>

# Neustarten
systemctl restart home-assistant@homeassistant
```

## Schritt 5: Integration überprüfen

Nach dem Neustart:

1. **WebUI öffnen**: http://<HOME_ASSISTANT_IP>:8123
2. **Developer Tools öffnen**: http://<HOME_ASSISTANT_IP>:8123/developer-tools/states
3. **Nach Sensoren suchen**: Suche nach `sensor.kesseltemperatur`

Wenn alles funktioniert, solltest du folgende Sensoren sehen:
- `sensor.kesseltemperatur`
- `sensor.aussentemperatur`
- `sensor.warmwasser_solltemperatur`
- `sensor.warmwasser_isttemperatur`
- `sensor.heizkreis_vorlauftemperatur`

## Schritt 6: Services testen

### Via Developer Tools

1. Gehe zu: http://<HOME_ASSISTANT_IP>:8123/developer-tools/service
2. Wähle Service: `vcontrold.set_temp_ww_soll`
3. Gib Daten ein:
   ```yaml
   temperature: 55
   ```
4. Klick "Call Service"

### Via YAML-Automation

Erstelle eine einfache Test-Automation in `automations.yaml`:

```yaml
- id: test_vcontrold
  alias: Test vcontrold
  trigger:
    platform: time
    at: "12:00:00"
  action:
    service: vcontrold.set_temp_ww_soll
    data:
      temperature: 55
```

## Troubleshooting

### Problem 1: Integration wird nicht geladen

**Symptome:**
- Keine Sensoren erscheinen
- Fehler in den Logs

**Lösungen:**

1. **Logs überprüfen:**
   ```bash
   docker logs homeassistant | grep vcontrold
   ```

2. **Konfiguration validieren:**
   - YAML-Syntax überprüfen (keine Tabs, richtige Indentation)
   - Konfiguration im Editor neu laden

3. **Integration manuell laden:**
   - HomeAssistant WebUI
   - Developer Tools → Services
   - `homeassistant.reload_custom_components`

### Problem 2: "vcontrold nicht erreichbar"

**Symptome:**
- Integration startet nicht
- Fehler: "vcontrold not reachable"

**Debugging:**

```bash
# Prüfe ob vcontrold läuft
ps aux | grep vcontrold

# Prüfe Port
netstat -tlnp | grep 3002

# Test Verbindung
telnet localhost 3002
# oder
nc -zv localhost 3002

# Test mit Ping-Befehl (von vcontrold host)
echo "ping" | nc localhost 3002
```

**Lösungen:**
1. Starte vcontrold neu
2. Prüfe Firewall-Regeln
3. Prüfe Host- und Port-Konfiguration
4. Prüfe Netzwerkkonnektivität zwischen Home Assistant und vcontrold

### Problem 3: Sensoren zeigen `unknown`

**Symptome:**
- Sensoren existieren, zeigen aber keine Werte

**Lösungen:**

1. **Debug-Logging aktivieren:**
   ```yaml
   logger:
     logs:
      custom_components.vcontrold: debug
   ```

2. **Logs prüfen:**
   ```bash
   docker logs homeassistant | grep vcontrold
   ```

3. **vcontrold-Befehle manuell testen:**
   ```bash
   echo "getTempKessel" | nc localhost 3002
   ```

### Problem 4: Timeouts

**Symptome:**
- Fehler: "vcontrold Timeout"
- Sensoren intermittierend

**Lösungen:**

1. **Update-Intervall erhöhen:**
   ```yaml
   vcontrold:
     update_interval: 120
   ```

2. **Netzwerk prüfen:**
   - Ping zur vcontrold-Maschine
   - Latenz überprüfen

3. **vcontrold-Load prüfen:**
   ```bash
   top # auf vcontrold-Host
   ```

## Nächste Schritte

Nach erfolgreicher Installation:

1. **Dashboard erstellen**: Sensoren zum Lovelace Dashboard hinzufügen
2. **Automationen schreiben**: Heizung automatisch steuern
3. **Scripts erstellen**: Komplexe Szenarien implementieren
4. **Logging konfigurieren**: Optional auf DEBUG setzen

Siehe `README.md` für weitere Beispiele und Konfigurationen!

## Weitere Hilfe

- **Logs anschauen**: `docker logs -f homeassistant`
- **SSH zugreifen**: `ssh root@<HOME_ASSISTANT_IP>`
- **Config validieren**: WebUI → Settings → System → Check configuration
- **GitHub Issues**: https://github.com/Minexvibx123/Vcontrold-for-Home-assistant/issues
