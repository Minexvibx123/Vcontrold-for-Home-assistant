# 🔧 vcontrold Daemon Setup Guide

Detaillierte Anleitung zum Aufsetzen des vcontrold Daemons für verschiedene Szenarien.

## 📋 Inhaltsverzeichnis

1. [Option 1: HA verwaltet Daemon (Empfohlen)](#option-1-ha-verwaltet-daemon)
2. [Option 2: Externer Daemon (Systemd)](#option-2-externer-daemon-systemd)
3. [Option 3: Docker-Compose](#option-3-docker-compose)
4. [Fehlerbehebung](#fehlerbehebung)

---

## Option 1: HA verwaltet Daemon ⭐ (Empfohlen)

Home Assistant startet und verwaltet den vcontrold Daemon automatisch.

### Voraussetzungen
- vcontrold Binary im Integration-Verzeichnis vorhanden
- Home Assistant hat Zugriff auf serielle Schnittstelle
- Linux/macOS (Windows unterstützt vcontrold nicht nativ)

### 1.1 vcontrold Binary bereitstellen

```bash
# Verzeichnis für Daemon binär
mkdir -p ~/.homeassistant/custom_components/vcontrold/daemon

# Binary herunterladen (Linux x64 Beispiel)
wget https://github.com/openv/vcontrold/releases/download/v8.103/vcontrold_linux_amd64 \
  -O ~/.homeassistant/custom_components/vcontrold/daemon/vcontrold_linux

chmod +x ~/.homeassistant/custom_components/vcontrold/daemon/vcontrold_linux
```

**Für macOS:**
```bash
wget https://github.com/openv/vcontrold/releases/download/v8.103/vcontrold_macos \
  -O ~/.homeassistant/custom_components/vcontrold/daemon/vcontrold_macos

chmod +x ~/.homeassistant/custom_components/vcontrold/daemon/vcontrold_macos
```

### 1.2 Berechtigungen für serielle Schnittstelle

Wenn Home Assistant als Service läuft, muss der User Zugriff auf das serielle Gerät haben:

```bash
# Der HA User (Standard: homeassistant)
sudo usermod -a -G dialout homeassistant

# Neue Berechtigungen aktivieren
su - homeassistant
```

### 1.3 Konfiguration in Home Assistant

**Via WebUI:**
1. Settings → Devices & Services → Create Integration
2. Suche: vcontrold
3. Konfiguriere:
   - Host: `localhost`
   - Port: `3002`
   - Daemon Enabled: ✅ (aktiviert)
   - Daemon Device: `/dev/ttyUSB0` (anpassen!)
   - Daemon Log Level: `ERROR`
4. Create

**Via YAML:**
```yaml
vcontrold:
  host: localhost
  port: 3002
  daemon_enabled: true
  daemon_device: /dev/ttyUSB0
  daemon_log_level: ERROR
```

### 1.4 Verfügbarkeit der Geräte prüfen

```bash
# USB-Seriell Adapter finden
ls -la /dev/ttyUSB*
ls -la /dev/ttyACM*

# Oder mit lsusb
lsusb
```

Beispielausgabe:
```
/dev/ttyUSB0 - Prolific USB to Serial Adapter
```

### 1.5 Daemon Logs

Logs werden in `~/.homeassistant/vcontrold_daemon/vcontrold.log` gespeichert:

```bash
tail -f ~/.homeassistant/vcontrold_daemon/vcontrold.log
```

---

## Option 2: Externer Daemon (Systemd)

vcontrold läuft separat als systemd Service. Home Assistant verbindet sich darüber TCP.

### 2.1 vcontrold installieren

**Debian/Ubuntu:**
```bash
sudo apt update
sudo apt install vcontrold
```

**Von Source:**
```bash
git clone https://github.com/openv/vcontrold.git
cd vcontrold
./configure
make
sudo make install
```

### 2.2 Konfigurationsdatei

```bash
sudo nano /etc/vcontrold/vcontrold.conf
```

Beispielkonfiguration:
```conf
# vcontrold Konfigurationsdatei

# Listen auf TCP Port 3002
listen localhost 3002

# Serielles Gerät
device /dev/ttyUSB0

# Logging
loglevel ERROR

# Protokoll (egal ob raw, Framing oder KW)
# device /dev/ttyUSB0:raw
```

**Für KW-Protokoll (Standard bei meisten Viessmann):**
```conf
listen localhost 3002
device /dev/ttyUSB0
loglevel ERROR
# Keine zusätzliche Konfiguration nötig für Standard-Setup
```

### 2.3 Systemd Service erstellen

```bash
sudo nano /etc/systemd/system/vcontrold.service
```

Inhalt:
```ini
[Unit]
Description=vcontrold Daemon - Viessmann Heating Control
After=network.target
Wants=multi-user.target

[Service]
Type=simple
User=vcontrold
Group=vcontrold
ExecStart=/usr/bin/vcontrold -d /dev/ttyUSB0 -l localhost -p 3002 --loglevel ERROR
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 2.4 Service aktivieren und starten

```bash
# Service neuladen
sudo systemctl daemon-reload

# Aktivieren beim Booten
sudo systemctl enable vcontrold

# Starten
sudo systemctl start vcontrold

# Status prüfen
sudo systemctl status vcontrold

# Logs anschauen
journalctl -u vcontrold -f
```

### 2.5 Verfindung testen

```bash
# Lokale Verbindung testen
telnet localhost 3002

# Befehl senden
getTempKessel

# Sollte "OK" + Temperatur zurückgeben
```

### 2.6 Home Assistant konfigurieren

**Via WebUI:**
1. Settings → Devices & Services → Create Integration
2. Suche: vcontrold
3. Konfiguriere:
   - Host: `localhost` (oder Server-IP)
   - Port: `3002`
   - Daemon Enabled: ❌ (deaktiviert - läuft extern)
4. Create

**Via YAML:**
```yaml
vcontrold:
  host: localhost
  port: 3002
  daemon_enabled: false  # Daemon läuft extern
```

---

## Option 3: Docker-Compose

Vollständiges Setup mit Home Assistant + vcontrold in Docker.

### 3.1 docker-compose.yml

```yaml
version: '3.8'

services:
  homeassistant:
    image: homeassistant/home-assistant:latest
    container_name: homeassistant
    restart: unless-stopped
    privileged: true
    ports:
      - "8123:8123"
    volumes:
      - ./homeassistant_config:/config
      - /run/dbus:/run/dbus:ro
    environment:
      - TZ=Europe/Berlin
    depends_on:
      - vcontrold
    networks:
      - ha_network

  vcontrold:
    image: openv/vcontrold:latest
    container_name: vcontrold
    restart: unless-stopped
    devices:
      - /dev/ttyUSB0:/dev/ttyUSB0  # 🔴 Anpassen zum korrekten Gerät!
    environment:
      - VCONTROLD_DEVICE=/dev/ttyUSB0
      - VCONTROLD_PORT=3002
      - VCONTROLD_LOGLEVEL=ERROR
    ports:
      - "3002:3002"
    networks:
      - ha_network

networks:
  ha_network:
    driver: bridge
```

### 3.2 Geräte-Mapping prüfen

```bash
# Auf dem Host: Serielles Gerät finden
ls -la /dev/ttyUSB*

# In docker-compose konfigurieren
devices:
  - /dev/ttyUSB0:/dev/ttyUSB0
```

### 3.3 Starten

```bash
docker-compose up -d

# Logs prüfen
docker-compose logs -f vcontrold
docker-compose logs -f homeassistant
```

### 3.4 Home Assistant konfigurieren

```yaml
vcontrold:
  host: vcontrold  # Service-Name im Docker-Netz
  port: 3002
  daemon_enabled: false
```

---

## Fehlerbehebung

### Problem: "vcontrold nicht erreichbar"

**Lösung 1: Verbindung testen**
```bash
# TCP-Port prüfen
telnet localhost 3002

# Oder mit nc
nc -zv localhost 3002
```

**Lösung 2: Firewall prüfen**
```bash
# UFW Firewall
sudo ufw allow 3002/tcp

# Oder iptables
sudo iptables -A INPUT -p tcp --dport 3002 -j ACCEPT
```

**Lösung 3: Daemon Logs anschauen**
```bash
# Systemd Service
journalctl -u vcontrold -n 50

# Oder Home Assistant Logs
docker logs homeassistant | grep -i vcontrold
```

### Problem: Serielle Schnittstelle nicht erkannt

**Lösung 1: Gerät finden**
```bash
# Alle seriellen Geräte auflisten
ls -la /dev/ttyUSB*
ls -la /dev/ttyACM*

# Mit dmesg
dmesg | grep -i usb
```

**Lösung 2: Berechtigungen prüfen**
```bash
# Berechtigungen auf Gerät
ls -la /dev/ttyUSB0
# Sollte: crw-rw---- root dialout

# Home Assistant User zur dialout Gruppe hinzufügen
sudo usermod -a -G dialout homeassistant

# User wechsel erforderlich für neue Gruppe
# Entweder: Neustart oder
su - homeassistant
```

**Lösung 3: Gerät in Docker**
```bash
# docker-compose: Gerät-Mapping prüfen
devices:
  - /dev/ttyUSB0:/dev/ttyUSB0

# Oder mit --device Flag
docker run --device /dev/ttyUSB0:/dev/ttyUSB0 ...
```

### Problem: Timeout beim Kommando-Senden

**Ursachen:**
1. Heizung nicht erreichbar
2. Falsches Protokoll (raw vs KW)
3. Serielle Schnittstelle blockiert

**Lösungen:**
```bash
# 1. Heizung testen
# Mit vcontrold CLI Tool
vcontrold-cli

# 2. Logs auf DEBUG stellen
# In vcontrold.conf oder via Parameter
--loglevel DEBUG

# 3. Serielle Schnittstelle prüfen
strace vcontrold -d /dev/ttyUSB0 -l localhost -p 3002
```

### Problem: "Binary nicht gefunden"

**Für Option 1 (HA verwaltet):**
```bash
# Binary prüfen
ls -la ~/.homeassistant/custom_components/vcontrold/daemon/

# Sollte z.B. vcontrold_linux enthalten
# Mit execute Bit: -rwxr-xr-x
```

**Lösung: Binary herunterladen**
```bash
mkdir -p ~/.homeassistant/custom_components/vcontrold/daemon

# Für Linux
wget https://github.com/openv/vcontrold/releases/download/v8.103/vcontrold_linux_amd64 \
  -O ~/.homeassistant/custom_components/vcontrold/daemon/vcontrold_linux
chmod +x ~/.homeassistant/custom_components/vcontrold/daemon/vcontrold_linux
```

### Problem: "Permission denied" beim Starten

**Lösung 1: Execute-Berechtigung**
```bash
chmod +x ~/.homeassistant/custom_components/vcontrold/daemon/vcontrold_linux
```

**Lösung 2: Benutzer-Berechtigung**
```bash
# vcontrold Binary als homeassistant User ausführbar
sudo chown homeassistant:homeassistant \
  ~/.homeassistant/custom_components/vcontrold/daemon/vcontrold_linux

sudo chmod 755 ~/.homeassistant/custom_components/vcontrold/daemon/vcontrold_linux
```

---

## 🔍 Debugging

### Logs sammeln

```bash
# Home Assistant Logs mit vcontrold Filter
docker logs homeassistant 2>&1 | grep -i vcontrold

# Systemd vcontrold Service
sudo journalctl -u vcontrold -n 100 --no-pager

# Integration Logs
tail -f ~/.homeassistant/logs/vcontrold.log
```

### Verbindungstest

```bash
# Mit Python
python3 << 'EOF'
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(5)
try:
    s.connect(("localhost", 3002))
    s.sendall(b"getTempKessel\n")
    response = s.recv(1024).decode()
    print(f"Response: {response}")
finally:
    s.close()
EOF
```

### vcontrold Kommandos testen

```bash
# Interaktiv mit vcontrold verbinden
nc localhost 3002

# Kommandos
getTempKessel
getTempAussen
getTempWWsoll
getTempWWist
getTempVorlaufHK1

# Ergebnis sollte sein:
# OK
# 23.5
```

---

## 📝 Best Practices

1. **Update-Intervall**: Nicht unter 30 Sekunden setzen (zu häufige Anfragen)
2. **Caching**: Nutzen, um TCP-Last zu reduzieren (standard: 30 Sekunden)
3. **Logging**: In Production auf ERROR setzen, nur für Debugging auf INFO/DEBUG
4. **Firewall**: Port 3002 nur lokal erlauben, wenn nicht extern nötig
5. **Monitoring**: Home Assistant Status prüfen (DevTools → States)

---

## 🔗 Weiterführende Ressourcen

- [vcontrold GitHub](https://github.com/openv/vcontrold)
- [vcontrold Dokumentation](https://github.com/openv/vcontrold/wiki)
- [Home Assistant Debugging](https://www.home-assistant.io/docs/configuration/troubleshooting/)
- [Systemd Service Tutorial](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
