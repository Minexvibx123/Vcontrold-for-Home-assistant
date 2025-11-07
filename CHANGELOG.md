# Changelog

Alle wichtigen Änderungen in diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
und dieses Projekt folgt [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-01

### Added
- ✨ Initiale Release der vcontrold Integration für Home Assistant
- 🌡️ 5 Temperatur-Sensoren:
  - Kesseltemperatur (getTempKessel)
  - Außentemperatur (getTempAussen)
  - Warmwasser-Solltemperatur (getTempWWsoll)
  - Warmwasser-Isttemperatur (getTempWWist)
  - Heizkreis-Vorlauftemperatur (getTempVorlaufHK1)
- 🎮 Service-Aufrufe:
  - `vcontrold.set_temp_ww_soll` - Warmwasser-Solltemperatur setzen
  - `vcontrold.set_betriebsart` - Betriebsart ändern (auto, standby, party, eco)
- 🔌 TCP-Socket Kommunikation mit vcontrold Daemon
- ⚡ Regelmäßige Datenabfrage (konfigurierbar, Default: 60 Sekunden)
- 💾 Intelligentes Caching (30 Sekunden TTL) zur Reduktion von Socket-Anfragen
- 🛡️ Robuste Fehlerbehandlung mit:
  - Timeout-Erkennung (10 Sekunden)
  - Connection-Handling
  - Logging auf DEBUG-Ebene
- 🌍 Mehrsprachige Unterstützung:
  - Deutsch (de)
  - Englisch (en)
- 📚 Umfassende Dokumentation:
  - README.md mit Features, Installation und Beispiele
  - INSTALL.md mit detaillierten Setup-Anweisungen
  - TROUBLESHOOTING.md mit Fehlerdiagnose
  - ARCHITECTURE.md mit technischen Details
- 📋 Beispiel-Konfigurationen:
  - configuration.example.yaml
  - automations.example.yaml
  - scripts.example.yaml
- ✅ 10+ Automation-Vorlagen
- ✅ 10+ Script-Vorlagen

### Technical Details
- Python 3.8+ Kompatibilität
- Home Assistant 2024.1.0+ erforderlich
- Asynchrone Datenabfrage mit DataUpdateCoordinator
- Entity Platform Integration
- Custom Services mit Validierung

### Components
- `__init__.py` - Integration Setup & Service-Registrierung
- `sensor.py` - Sensor-Entities & Update Coordinator
- `vcontrold_manager.py` - TCP-Socket Manager mit Caching
- `manifest.json` - Integration Metadaten
- `services.yaml` - Service-Definitionen
- `strings.json` - Deutsche Strings
- `translations/en.json` - Englische Übersetzungen

### Known Limitations
- nur ein vcontrold Daemon pro Integration (zukünftige Multi-Support)
- keine Config Flow UI (manuell konfigurierbar via YAML)
- keine Climate Entity (nur Sensoren + Services)

---

## Versionierungs-Schema

- **Major (X.0.0)**: Breaking Changes oder große Features
- **Minor (0.X.0)**: Neue Features, abwärtskompatibel
- **Patch (0.0.X)**: Bugfixes und kleine Verbesserungen

---

## Roadmap

### Geplant für v1.1.0
- [ ] Config Flow UI für WebUI-Konfiguration
- [ ] Climate Entity (thermostat_v2)
- [ ] Device-Integration für bessere UI
- [ ] History Stats Integration

### Geplant für v1.2.0
- [ ] Multi-Instance Support (mehrere vcontrold Daemons)
- [ ] Diagnostics & Repair-UI
- [ ] Advanced Caching (Redis Support)
- [ ] Prometheus Metrics Export

### Geplant für v2.0.0
- [ ] Async vcontrold Library
- [ ] WebSocket Support
- [ ] Device-spezifische Eigenschaften
- [ ] Erweiterte Automations

---

## Migration von älteren Versionen

### Von v0.x zu v1.0
- Keine Breaking Changes
- Vollständig abwärtskompatibel
- Einfaches Update möglich

---

## Support & Issues

Berichtet Bugs und Features auf GitHub:
https://github.com/Minexvibx123/Vcontrold-for-Home-assistant/issues

---

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert.
Siehe LICENSE Datei für Details.
