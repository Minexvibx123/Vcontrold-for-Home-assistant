"""Konstanten für vcontrold Integration - All-in-One."""

DOMAIN = "vcontrold"

# Konfigurationsschlüssel (All-in-One)
CONF_DEVICE = "device"
CONF_FRAMING = "framing"
CONF_UPDATE_INTERVAL = "update_interval"

# Standardwerte
DEFAULT_DEVICE = "/dev/ttyUSB0"
DEFAULT_FRAMING = "kw"
DEFAULT_UPDATE_INTERVAL = 60
DEFAULT_CACHE_TTL = 30
DEFAULT_TIMEOUT = 10

# Service-Namen
SERVICE_SET_TEMP_WW_SOLL = "set_temp_ww_soll"
SERVICE_SET_BETRIEBSART = "set_betriebsart"

# Service-Datenfelder
ATTR_TEMPERATURE = "temperature"
ATTR_MODE = "mode"

# Betriebsarten
MODE_AUTO = "auto"
MODE_STANDBY = "standby"
MODE_PARTY = "party"
MODE_ECO = "eco"

VALID_MODES = [MODE_AUTO, MODE_STANDBY, MODE_PARTY, MODE_ECO]

# Temperaturgrenzen
MIN_TEMP = 20
MAX_TEMP = 80

# Update-Intervall
SCAN_INTERVAL = 60

# Service-Namen
SERVICE_SET_TEMP_WW_SOLL = "set_temp_ww_soll"
SERVICE_SET_BETRIEBSART = "set_betriebsart"

# Service-Datenfelder
ATTR_TEMPERATURE = "temperature"
ATTR_MODE = "mode"

# Betriebsarten
MODE_AUTO = "auto"
MODE_STANDBY = "standby"
MODE_PARTY = "party"
MODE_ECO = "eco"

VALID_MODES = [MODE_AUTO, MODE_STANDBY, MODE_PARTY, MODE_ECO]

# Temperaturgrenzen
MIN_TEMP = 20
MAX_TEMP = 80

# Update-Intervall
SCAN_INTERVAL = 60
