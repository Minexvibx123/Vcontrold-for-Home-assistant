"""Konstanten für vcontrold Integration - Viessmann Vitotronic 300 optimiert."""

DOMAIN = "vcontrold"

# ======================= HEIZUNGSMODELLE =======================
HEATER_VITOTRONIC_300 = "vitotronic_300"
HEATER_VITOTRONIC_200 = "vitotronic_200"
HEATER_VITOLA_300 = "vitola_300"

HEATER_MODELS = {
    HEATER_VITOTRONIC_300: "🔥 Vitotronic 300 (empfohlen)",
    HEATER_VITOTRONIC_200: "🔥 Vitotronic 200",
    HEATER_VITOLA_300: "🔥 Vitola 300",
}

# ======================= KONFIGURATION =======================
CONF_DEVICE = "device"
CONF_FRAMING = "framing"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_HEATER_MODEL = "heater_model"
CONF_LOG_LEVEL = "log_level"
CONF_HOST = "host"
CONF_PORT = "port"
CONF_MANAGE_DAEMON = "manage_daemon"

# ======================= STANDARDWERTE =======================
# Für Vitotronic 300
DEFAULT_DEVICE = "/dev/ttyUSB0"
DEFAULT_FRAMING = "kw"  # Komfortsignal - Standard für Vitotronic 300
DEFAULT_UPDATE_INTERVAL = 60
DEFAULT_CACHE_TTL = 30
DEFAULT_TIMEOUT = 10
DEFAULT_HEATER_MODEL = HEATER_VITOTRONIC_300
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 3002

# Log-Level Optionen
LOG_LEVELS = {
    "ERROR": "🔴 ERROR (nur Fehler)",
    "WARN": "🟡 WARN (Warnungen)",
    "INFO": "🔵 INFO (Informationen)",
    "DEBUG": "🟣 DEBUG (alles)",
}

# Protokoll-Optionen für Vitotronic 300
FRAMING_OPTIONS = {
    "kw": "📡 KW (Komfortsignal - Standard)",
    "raw": "📡 Raw (Binär)",
    "framing": "📡 Framing (Spezial)",
}

# ======================= SERVICES =======================
SERVICE_SET_TEMP_WW_SOLL = "set_temp_ww_soll"
SERVICE_SET_BETRIEBSART = "set_betriebsart"
SERVICE_START_DAEMON = "start_daemon"
SERVICE_STOP_DAEMON = "stop_daemon"
SERVICE_CHECK_STATUS = "check_status"

# ======================= SERVICE-ATTRIBUTE =======================
ATTR_TEMPERATURE = "temperature"
ATTR_MODE = "mode"

# ======================= BETRIEBSARTEN =======================
MODE_AUTO = "auto"
MODE_STANDBY = "standby"
MODE_PARTY = "party"
MODE_ECO = "eco"

VALID_MODES = [MODE_AUTO, MODE_STANDBY, MODE_PARTY, MODE_ECO]

MODE_NAMES = {
    MODE_AUTO: "🤖 Auto",
    MODE_STANDBY: "⏸️ Standby",
    MODE_PARTY: "🎉 Party",
    MODE_ECO: "♻️ Eco",
}

# ======================= TEMPERATURGRENZEN =======================
MIN_TEMP = 20
MAX_TEMP = 80
MIN_UPDATE_INTERVAL = 30
MAX_UPDATE_INTERVAL = 300
MIN_PORT = 1024
MAX_PORT = 65535

# ======================= UPDATE-INTERVALL =======================
SCAN_INTERVAL = 60

# ======================= VITOTRONIC 300 SPEZIFISCHE SENSOREN =======================
# Diese Sensoren sind typisch für Vitotronic 300
VITOTRONIC_300_SENSORS = {
    "getTempKessel": {
        "name": "Kesseltemperatur",
        "unit": "°C",
        "icon": "mdi:thermometer",
        "key": "kesseltemperatur",
    },
    "getTempAussen": {
        "name": "Außentemperatur",
        "unit": "°C",
        "icon": "mdi:cloud-thermometer",
        "key": "aussentemperatur",
    },
    "getTempWWsoll": {
        "name": "Warmwasser Solltemperatur",
        "unit": "°C",
        "icon": "mdi:water-thermometer",
        "key": "warmwasser_soll",
    },
    "getTempWWist": {
        "name": "Warmwasser Isttemperatur",
        "unit": "°C",
        "icon": "mdi:water-thermometer",
        "key": "warmwasser_ist",
    },
    "getTempVorlaufHK1": {
        "name": "Heizkreis 1 Vorlauftemperatur",
        "unit": "°C",
        "icon": "mdi:pipe-valve",
        "key": "vorlauf_hk1",
    },
}

# ======================= ENTITY-PRÄFIXE =======================
ENTITY_PREFIX = "sensor.vcontrold"
