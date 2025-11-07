# 📋 Quick Reference Card

## 🚀 Start Here

### Installation (Choose One)

**Option A: SSH Terminal** (Fastest)
```bash
ssh -l root <HA-IP>
cd /config/custom_components
git clone https://github.com/Minexvibx123/Vcontrold-for-Home-assistant.git
mv Vcontrold-for-Home-assistant/vcontrold .
```

**Option B: SFTP Upload** (Easiest)
1. FileZilla → Custom/Components → Upload vcontrold folder
2. Restart HA

**Option C: Docker Volume**
1. Mount /config/custom_components
2. Put vcontrold folder there

### Setup (3 Steps)
1. **Settings** → **Devices & Services**
2. **Create Integration** → Search **"vcontrold"**
3. **Follow Wizard** (1 minute)

### Done! ✅
- 5 sensors appear automatically
- Services available
- Auto-updates every 60s

---

## 📊 Available Sensors

| Sensor | Type | Unit | Updates |
|--------|------|------|---------|
| `kesseltemperatur` | Status | °C | 60s |
| `aussentemperatur` | Status | °C | 60s |
| `warmwasser_soll` | Setting | °C | 60s |
| `warmwasser_ist` | Status | °C | 60s |
| `vorlauf_hk1` | Status | °C | 60s |

**Full names:** `sensor.vcontrold_<name>`

**Template:**
```yaml
{{ states('sensor.vcontrold_kesseltemperatur') }}
```

---

## 🎮 Available Services

| Service | Purpose | Parameters |
|---------|---------|------------|
| `set_temp_ww_soll` | Set hot water temp | `temperature: 20-80` |
| `set_betriebsart` | Change mode | `mode: auto\|standby\|party\|eco` |
| `start_daemon` | Start service | - |
| `stop_daemon` | Stop service | - |
| `check_status` | Health check | - |

**Example:**
```yaml
service: vcontrold.set_temp_ww_soll
data:
  temperature: 60
```

---

## ⚙️ Configuration

### All-in-One Mode (Default) ✅
```
Setup → 🔧 HA verwaltet
    ↓
Gerät wählen: /dev/ttyUSB0
    ↓
Host: localhost
Port: 3002
    ↓
Fertig!
```

### External Mode
```
Setup → 🌐 Externe vcontrold
    ↓
Host: 192.168.1.100
Port: 3002
    ↓
Fertig!
```

### Settings ändern (ohne Neustart!)
```
Settings → Devices & Services
→ vcontrold
→ Configure
→ Änderung
→ Submit ✅
```

---

## 🤖 Automation Examples

### Nacht: Temperatur senken
```yaml
automation:
  - alias: "Nacht: WW auf 45°C"
    trigger:
      platform: time
      at: "22:00:00"
    action:
      service: vcontrold.set_temp_ww_soll
      data:
        temperature: 45
```

### Morgens: Aufheizen
```yaml
automation:
  - alias: "Morgens: Auto Mode"
    trigger:
      platform: sun
      event: sunrise
    action:
      service: vcontrold.set_betriebsart
      data:
        mode: "auto"
```

### Alarm: Zu heiß
```yaml
automation:
  - alias: "Alarm: Heizung zu heiß"
    trigger:
      platform: numeric_state
      entity_id: sensor.vcontrold_kesseltemperatur
      above: 75
    action:
      service: notify.notify
      data:
        message: "⚠️ Kessel: {{ states('sensor.vcontrold_kesseltemperatur') }}°C"
```

---

## 🎨 Dashboard Template

```yaml
type: vertical-stack
cards:
  - type: heading
    heading: "🔥 Heizungssteuerung"
  
  - type: grid
    columns: 3
    cards:
      - type: gauge
        entity: sensor.vcontrold_kesseltemperatur
        min: 0
        max: 80
        title: "Kessel"
      
      - type: gauge
        entity: sensor.vcontrold_aussentemperatur
        min: -20
        max: 40
        title: "Außen"
      
      - type: gauge
        entity: sensor.vcontrold_warmwasser_ist
        min: 0
        max: 80
        title: "WW Ist"
  
  - type: entities
    title: "Einstellungen"
    entities:
      - entity: sensor.vcontrold_warmwasser_soll
      - entity: sensor.vcontrold_vorlauf_hk1
```

---

## 🔧 Troubleshooting

### Sensor nicht verfügbar?
```bash
# 1. Check Integration loaded
Settings → Devices & Services → vcontrold

# 2. Check Logs
Settings → System → Logs
(Filter: "vcontrold")

# 3. Restart Integration
Settings → Devices & Services → vcontrold → Reload
```

### "Cannot connect"?
```bash
# 1. Test TCP Connection
nc -zv localhost 3002

# 2. Check Daemon
ps aux | grep vcontrold

# 3. Check Serial Port
ls -la /dev/ttyUSB* /dev/ttyACM*
```

### Updates stopped?
```bash
# 1. Increase Log Level
Settings → Devices & Services → vcontrold → Configure
→ Log-Level: DEBUG → Submit

# 2. Check Logs
Settings → System → Logs

# 3. Reload
Settings → Devices & Services → vcontrold → Reload
```

---

## 📚 Documentation Map

| Document | Best For | Time |
|----------|----------|------|
| **QUICKSTART.md** | First setup | 5 min |
| **INTEGRATION_GUIDE.md** | Complete guide | 20 min |
| **GUI_DOCUMENTATION.md** | WebUI help | 10 min |
| **TROUBLESHOOTING.md** | Debugging | 15 min |
| **ARCHITECTURE.md** | Tech details | 30 min |
| **README.md** | Overview | 10 min |

---

## 🎯 Common Tasks

### Add Sensor to Dashboard
1. Settings → Dashboards
2. Edit Dashboard
3. Add Card → "Gauge" / "Entity" / "History"
4. Choose: `sensor.vcontrold_*`

### Create Automation
1. Settings → Automations → Create Automation
2. Trigger: Time / Sun / Sensor
3. Action: Call Service → `vcontrold.set_temp_ww_soll`
4. Data: `temperature: 60`
5. Save

### Change Update Interval
1. Settings → Devices & Services → vcontrold → Configure
2. Update-Intervall: 30-300 Sekunden
3. Submit

### Enable Debug Logging
1. Settings → Devices & Services → vcontrold → Configure
2. Log-Level: DEBUG
3. Submit
4. Check: Settings → System → Logs

---

## 🔑 Key Commands

### SSH Terminal
```bash
# Connect to HA
ssh -l root <HA-IP>

# Check integration installed
ls /config/custom_components/vcontrold/

# View logs
tail -f /config/home-assistant.log | grep vcontrold

# Restart HA
docker restart homeassistant
```

### Configuration
```yaml
# Disable (configuration.yaml)
homeassistant:
  customize:
    sensor.vcontrold_kesseltemperatur:
      hidden: true

# Enable Logging
logger:
  default: info
  logs:
    custom_components.vcontrold: debug
```

---

## ❓ Quick FAQ

**Q: Brauche ich vcontrold extern?**
A: Nein! All-in-One macht das automatisch.

**Q: Wie oft werden Sensoren aktualisiert?**
A: Standard 60s (einstellbar: 30-300s).

**Q: Kann ich das remote nutzen?**
A: Lokal ja, remote nur mit SSH-Tunnel.

**Q: Funktioniert auf Raspberry Pi?**
A: Ja! Raspberry Pi 4 or Pi 5 empfohlen.

**Q: Kann ich mehrere Heizungen steuern?**
A: Aktuell eine pro HA (v3.0 geplant).

**Q: Brauche ich Coding-Kenntnisse?**
A: Nein! Setup-Wizard reicht.

---

## 📞 Support

- **Issues:** GitHub Issues
- **Questions:** GitHub Discussions
- **Docs:** Read first! (usually answers 90% of questions)
- **Logs:** Settings → System → Logs

---

## ✨ That's It!

**You're ready to go!** 🚀

→ Start: [QUICKSTART.md](QUICKSTART.md)
→ More: [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)
→ Help: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

**Happy heating! 🔥❄️**

*vcontrold Integration v2.0.0-alpha*
