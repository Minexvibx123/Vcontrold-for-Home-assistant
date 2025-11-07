# Vcontrold Custom Integration für Home Assistant

Dieses Repository enthält eine Custom Integration für Viessmann Heizsysteme mit vcontrold Daemon.

## Installation (Custom Integration)

Dies ist **NICHT** im offiziellen Add-on Store, weil es eine **Custom Integration** ist.

### Methode 1: HACS (empfohlen)

1. Installiere [HACS](https://hacs.xyz/) wenn noch nicht geschehen
2. Gehe zu HACS → Integrationen
3. Klicke "Neue Quelle hinzufügen"
4. Gib ein: `https://github.com/Minexvibx123/Vcontrold-for-Home-assistant`
5. Kategorie: **Integration** wählen
6. Klicke "Durchsuchen & installieren"
7. Suche "Viessmann vcontrold" und installiere

### Methode 2: Manuelle Installation

1. Lade [die neueste Release herunter](https://github.com/Minexvibx123/Vcontrold-for-Home-assistant/releases)
2. Entpacke die `vcontrold` Ordner
3. Kopiere ihn nach `config/custom_components/vcontrold/`
4. Starte Home Assistant neu
5. Gehe zu Einstellungen → Geräte & Dienste → "Neue Integration erstellen"
6. Suche "Viessmann vcontrold" und konfiguriere

## Nach der Installation

Siehe [Konfigurationsanleitung](VITOTRONIC_300_CONFIG.md) für Vitotronic 300 oder [Integration Guide](INTEGRATION_GUIDE.md) für Detailinfos.
