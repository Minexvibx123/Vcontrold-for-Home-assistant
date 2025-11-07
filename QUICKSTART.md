# Quick-Start Guide

Schnelle Übersicht für die erste Verwendung der vcontrold Integration.

## ⚡ 5 Minuten Setup

### 1. Integration kopieren

```bash
cp -r vcontrold ~/.homeassistant/custom_components/
```

### 2. Konfiguration hinzufügen

Bearbeite `~/.homeassistant/configuration.yaml`:

```yaml
vcontrold:
  host: localhost
  port: 3002
```

### 3. Home Assistant neustarten

```bash
docker restart homeassistant
```

### 4. Sensoren prüfen

Öffne: http://<IP>:8123/developer-tools/states

Suche nach: `sensor.kesseltemperatur`

✅ Fertig!

---

## 🎯 Häufigste Aufgaben

### Sensoren zum Dashboard hinzufügen

1. Öffne: http://<IP>:8123/admin/lovelace
2. Klick: "Create Card" → "Entities"
3. Wähle:
   - `sensor.kesseltemperatur`
   - `sensor.aussentemperatur`
   - `sensor.warmwasser_solltemperatur`

### Warmwasser-Temperatur setzen

**Über Developer Tools:**

1. Öffne: http://<IP>:8123/developer-tools/service
2. Service: `vcontrold.set_temp_ww_soll`
3. Data: `temperature: 55`
4. Klick: "Call Service"

**Über Automation:**

```yaml
automation:
  - alias: "Warmwasser morgens"
    trigger:
      at: "06:00:00"
      platform: time
    action:
      service: vcontrold.set_temp_ww_soll
      data:
        temperature: 60
```

### Betriebsart ändern

**Über Developer Tools:**

1. Service: `vcontrold.set_betriebsart`
2. Data: `mode: eco`
3. Klick: "Call Service"

**Verfügbare Modi:**
- `auto` - Automatisch
- `standby` - Aus
- `party` - Party Mode
- `eco` - Sparmodus

---

## 🔍 Debugging

### Sind die Sensoren aktiv?

```bash
docker logs homeassistant | grep -i vcontrold
```

Sollte zeigen:
```
INFO: vcontrold Integration erfolgreich eingerichtet
DEBUG: Aktualisiere Daten von vcontrold
```

### Funktioniert vcontrold?

```bash
echo "getTempKessel" | nc localhost 3002
```

Sollte antworten:
```
OK
23.5
```

### Integration manuell laden

Developer Tools → Services:
1. Service: `homeassistant.reload_custom_components`
2. "Call Service"

---

## 📚 Weitere Ressourcen

- [Vollständige README](README.md)
- [Installationsanleitung](INSTALL.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [Technische Architektur](ARCHITECTURE.md)
- [Automations Beispiele](automations.example.yaml)
- [Scripts Beispiele](scripts.example.yaml)

---

## ✅ Checkliste

- [ ] vcontrold läuft auf Port 3002
- [ ] Integration kopiert zu `custom_components/vcontrold/`
- [ ] `configuration.yaml` aktualisiert
- [ ] Home Assistant restarted
- [ ] Sensoren in Developer Tools sichtbar
- [ ] Teste Service-Aufruf

🎉 Viel Spaß mit deiner Viessmann-Heizung!
