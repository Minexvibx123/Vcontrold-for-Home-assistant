# Troubleshooting Guide: vcontrold Integration

Dieser Guide hilft bei der Diagnose und Behebung von Problemen mit der vcontrold Integration.

## 📋 Allgemeine Diagnose

### 1. Logs überprüfen

Erste Anlaufstelle für Fehlersuche:

```bash
# Docker Container Logs
docker logs -f homeassistant 2>&1 | grep -i vcontrold

# Systemd Service
journalctl -u homeassistant -f | grep -i vcontrold

# Datei-basierte Logs (optional)
tail -f ~/.homeassistant/home-assistant.log | grep vcontrold
```

### 2. Debug-Logging aktivieren

Aktiviere erweiterte Logs in `configuration.yaml`:

```yaml
logger:
  logs:
    custom_components.vcontrold: debug
    homeassistant.components.sensor: debug
```

Nach Änderung: Home Assistant neu laden oder neu starten.

### 3. Systemzustand prüfen

Developer Tools → States in WebUI:
- Suche nach `sensor.kesseltemperatur`
- Prüfe `state` und `attributes`

## 🔴 Häufige Probleme & Lösungen

### Problem 1: "vcontrold not reachable"

**Symptome:**
```
ERROR (MainThread) [custom_components.vcontrold] vcontrold nicht erreichbar auf localhost:3002
```

**Diagnose:**

```bash
# 1. Prüfe ob vcontrold läuft
ps aux | grep vcontrold
systemctl status vcontrold

# 2. Prüfe Port
netstat -tlnp | grep 3002
ss -tlnp | grep 3002

# 3. Test Verbindung von Host
telnet localhost 3002
# oder
nc -zv localhost 3002

# 4. Test mit vcontrold Befehl
echo "ping" | nc localhost 3002
```

**Lösungen (nach Priorität):**

1. **vcontrold starten:**
   ```bash
   sudo systemctl start vcontrold
   # oder
   docker start vcontrold_daemon
   ```

2. **Port überprüfen:**
   ```yaml
   vcontrold:
     port: 3002  # Standard ändern falls nötig
   ```

3. **Firewall prüfen:**
   ```bash
   # Port freigeben (UFW)
   sudo ufw allow 3002/tcp
   
   # oder (iptables)
   sudo iptables -A INPUT -p tcp --dport 3002 -j ACCEPT
   ```

4. **Netzwerk prüfen:**
   ```bash
   # Ping zum Host
   ping -c 4 localhost
   
   # DNS Auflösung
   nslookup localhost
   ```

5. **vcontrold neu starten:**
   ```bash
   sudo systemctl restart vcontrold
   # oder
   docker restart vcontrold_daemon
   ```

---

### Problem 2: Sensoren zeigen `unknown`

**Symptome:**
- Sensoren existieren, aber zeigen keine Werte
- `state: unknown` in Developer Tools

**Diagnose:**

```bash
# 1. Manuelle Tests der vcontrold Befehle
echo "getTempKessel" | nc localhost 3002
echo "getTempAussen" | nc localhost 3002

# 2. Logs mit DEBUG-Level prüfen
docker logs homeassistant | grep "vcontrold\|getTempKessel"
```

**Mögliche Antworten von vcontrold:**
```
OK
23.5

# oder bei Fehler:
ERROR: unknown command
```

**Lösungen:**

1. **vcontrold Konfiguration prüfen:**
   ```bash
   cat /etc/vcontrold/vcontrold.conf
   # oder
   cat ~/.vcontrold/vcontrold.conf
   ```

2. **vcontrold Heizungsverbindung prüfen:**
   ```bash
   # Logs von vcontrold
   journalctl -u vcontrold -n 50
   ```

3. **Manuelle Befehle testen:**
   ```bash
   # Verschiedene Befehle ausprobieren
   (echo "getTempKessel"; sleep 1) | telnet localhost 3002
   (echo "getTempAussen"; sleep 1) | telnet localhost 3002
   ```

4. **Cache leeren:**
   ```bash
   # Datei-Cache (falls vorhanden)
   rm -f ~/.homeassistant/.vcontrold_cache
   ```

---

### Problem 3: Timeouts

**Symptome:**
```
ERROR [custom_components.vcontrold] Timeout beim Senden von 'getTempKessel'
```

**Diagnose:**

```bash
# 1. Netzwerk-Latenz prüfen
ping -c 10 localhost
mtr localhost

# 2. vcontrold Auslastung
top -p $(pgrep vcontrold)
vmstat 1 5

# 3. Verbindungsstatus
ss -s
netstat -s
```

**Lösungen:**

1. **Update-Intervall erhöhen:**
   ```yaml
   vcontrold:
     update_interval: 120  # von 60 auf 120 Sekunden
   ```

2. **Timeout erhöhen (bei Bedarf anpassen - in Code):**
   - In `vcontrold_manager.py` Timeout anpassen

3. **Netzwerk optimieren:**
   ```bash
   # MTU Check
   ip link show
   
   # Wenn zu klein: MTU erhöhen
   sudo ip link set dev eth0 mtu 9000
   ```

4. **vcontrold Leistung prüfen:**
   ```bash
   # Ressourcen-Monitor
   htop
   
   # Wenn vcontrold zu viel CPU/RAM nutzt - neu starten
   sudo systemctl restart vcontrold
   ```

---

### Problem 4: Services funktionieren nicht

**Symptome:**
```
Service vcontrold.set_temp_ww_soll nicht gefunden
```

**Diagnose:**

```bash
# 1. Services in Developer Tools prüfen
# http://localhost:8123/developer-tools/service
# → vcontrold sollte in der Liste sein

# 2. Logs prüfen
docker logs homeassistant | grep "register.*service"
```

**Lösungen:**

1. **Integration neu laden:**
   - Developer Tools → Services
   - `homeassistant.restart` aufrufen

2. **Home Assistant neu starten:**
   ```bash
   docker restart homeassistant
   ```

3. **Service-Datei prüfen:**
   ```bash
   cat custom_components/vcontrold/services.yaml
   ```

---

### Problem 5: Automation funktioniert nicht

**Symptome:**
- Automation wird nicht ausgelöst
- Fehler bei Service-Aufruf

**Diagnose:**

```bash
# 1. Automation in WebUI überprüfen
# Settings → Automations → [Automation anklicken]

# 2. YAML-Syntax validieren
# Developer Tools → YAML

# 3. Service-Aufruf manuell testen
# Developer Tools → Services
```

**Lösungen:**

1. **YAML-Syntax überprüfen:**
   ```bash
   # Indentation prüfen (Spaces, keine Tabs!)
   cat -A automations.yaml
   ```

2. **Service manuell aufrufen:**
   - Developer Tools → Services
   - `vcontrold.set_temp_ww_soll` auswählen
   - Daten eingeben: `{"temperature": 55}`
   - "Call Service" klicken

3. **Automation mit Trigger testen:**
   ```yaml
   automation:
     - alias: "Test Automation"
       trigger:
         platform: homeassistant
         event: start
       action:
         service: vcontrold.set_temp_ww_soll
         data:
           temperature: 55
   ```

---

## 🔧 Erweiterte Diagnose

### Performance-Tests

```bash
# 1. Response-Zeit messen
time echo "getTempKessel" | nc localhost 3002

# 2. 100x Anfragen testen
for i in {1..100}; do
  echo "getTempKessel" | nc -w 1 localhost 3002
done

# 3. Gleichzeitige Verbindungen
for i in {1..10}; do
  (echo "getTempKessel"; sleep 5) | telnet localhost 3002 &
done
```

### Netzwerk-Debugging

```bash
# TCP Verbindungen tracen
sudo tcpdump -i lo -n 'tcp port 3002'

# Detaillierte Netzwerk-Statistiken
netstat -an | grep 3002

# Firewall-Regeln checken
sudo iptables -L -n
sudo ufw status
```

### vcontrold Daemon-Debugging

```bash
# vcontrold im Debug-Modus starten
vcontrold -d -c /etc/vcontrold/vcontrold.conf

# oder bei Systemd
sudo systemctl edit vcontrold
# Füge ein: Environment="VCONTROLD_DEBUG=1"

# Heizungsverbindung testen
echo "raw: 00 81 34 37 4c 0a" | nc localhost 3002
```

---

## 📝 Logs sammeln für Support

Falls du Hilfe brauchst, sammle diese Logs:

```bash
#!/bin/bash
echo "=== Home Assistant Logs ===" > vcontrold_support.log
docker logs homeassistant 2>&1 | grep -i vcontrold >> vcontrold_support.log

echo -e "\n=== vcontrold Status ===" >> vcontrold_support.log
systemctl status vcontrold >> vcontrold_support.log 2>&1

echo -e "\n=== vcontrold Process ===" >> vcontrold_support.log
ps aux | grep vcontrold >> vcontrold_support.log

echo -e "\n=== Port Status ===" >> vcontrold_support.log
netstat -tlnp | grep 3002 >> vcontrold_support.log 2>&1

echo -e "\n=== Netzwerk Test ===" >> vcontrold_support.log
echo "getTempKessel" | nc localhost 3002 >> vcontrold_support.log 2>&1

echo "Support-Informationen in: vcontrold_support.log"
```

Teile diese Datei bei GitHub Issues: https://github.com/Minexvibx123/Vcontrold-for-Home-assistant/issues

---

## ✅ Checkliste zur Problemlösung

- [ ] vcontrold läuft: `systemctl status vcontrold`
- [ ] Port ist erreichbar: `telnet localhost 3002`
- [ ] Befehle funktionieren: `echo "getTempKessel" | nc localhost 3002`
- [ ] Home Assistant restarted
- [ ] Integration in `configuration.yaml` konfiguriert
- [ ] Integration im Verzeichnis: `custom_components/vcontrold/`
- [ ] DEBUG-Logging aktiviert
- [ ] Home Assistant Logs überprüft
- [ ] Firewall erlaubt Port 3002
- [ ] Netzwerk OK: `ping -c 4 localhost`

---

## 🆘 Wenn alles fehlschlägt

1. **Neu beginnen:**
   ```bash
   rm -rf custom_components/vcontrold
   cd custom_components
   git clone https://github.com/Minexvibx123/Vcontrold-for-Home-assistant.git
   cd vcontrold
   git checkout main
   ```

2. **Klone neu aufsetzen:**
   ```bash
   docker restart homeassistant
   ```

3. **GitHub Issue erstellen:**
   - Mit vollständigen Logs
   - Mit `vcontrold_support.log`
   - Mit Konfiguration (ohne sensitive Daten)
   - Mit genaue Fehlermeldung
   - Link: https://github.com/Minexvibx123/Vcontrold-for-Home-assistant/issues

---

## 📚 Weitere Ressourcen

- [Home Assistant Logs](https://www.home-assistant.io/docs/configuration/troubleshooting/)
- [vcontrold Dokumentation](https://github.com/openv/vcontrold)
- [Home Assistant Community](https://community.home-assistant.io/)
- [vcontrold Issues](https://github.com/openv/vcontrold/issues)
