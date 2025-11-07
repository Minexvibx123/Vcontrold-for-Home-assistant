"""vcontrold TCP Socket Manager."""
import asyncio
import logging
import socket
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

_LOGGER = logging.getLogger(__name__)

# vcontrold Befehle
VCONTROLD_COMMANDS = {
    "getTempKessel": "getTempKessel",
    "getTempAussen": "getTempAussen",
    "getTempWWsoll": "getTempWWsoll",
    "getTempWWist": "getTempWWist",
    "getTempVorlaufHK1": "getTempVorlaufHK1",
    "setBetriebsart": "setBetriebsart",
    "setTempWWsoll": "setTempWWsoll",
}


class VcontroledManager:
    """Manager für vcontrold Daemon Kommunikation."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 3002,
        timeout: int = 10,
        cache_ttl: int = 30,
    ):
        """Initialisiere Manager."""
        self.host = host
        self.port = port
        self.timeout = timeout
        self.cache_ttl = cache_ttl
        
        # Cache
        self._cache: Dict[str, Any] = {}
        self._cache_time: Dict[str, datetime] = {}
        
        # Verbindungsstatus
        self._connected = False
        self._socket: Optional[socket.socket] = None

    def _is_cache_valid(self, key: str) -> bool:
        """Prüfe ob Cache noch gültig ist."""
        if key not in self._cache_time:
            return False
        
        time_diff = datetime.now() - self._cache_time[key]
        return time_diff < timedelta(seconds=self.cache_ttl)

    def _send_command(self, command: str) -> str:
        """Sende Befehl an vcontrold via TCP Socket."""
        try:
            if self._socket is None:
                self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._socket.settimeout(self.timeout)
            
            # Verbindung aufbauen
            if not self._connected:
                self._socket.connect((self.host, self.port))
                self._connected = True
                _LOGGER.debug(f"Verbunden zu vcontrold auf {self.host}:{self.port}")
            
            # Befehl senden
            self._socket.sendall(f"{command}\n".encode("utf-8"))
            
            # Antwort empfangen
            response = self._socket.recv(1024).decode("utf-8").strip()
            
            _LOGGER.debug(f"vcontrold Antwort auf '{command}': {response}")
            return response
            
        except socket.timeout:
            _LOGGER.error(f"Timeout beim Senden von '{command}' an vcontrold")
            self._disconnect()
            raise RuntimeError(f"vcontrold Timeout: {command}")
            
        except ConnectionRefusedError:
            _LOGGER.error(f"Verbindung zu vcontrold ({self.host}:{self.port}) verweigert")
            self._disconnect()
            raise RuntimeError("vcontrold nicht erreichbar")
            
        except Exception as e:
            _LOGGER.error(f"Fehler beim Kommunizieren mit vcontrold: {e}")
            self._disconnect()
            raise RuntimeError(f"vcontrold Fehler: {str(e)}")

    def _disconnect(self):
        """Trenne Verbindung."""
        self._connected = False
        if self._socket:
            try:
                self._socket.close()
            except Exception:
                pass
            self._socket = None

    def get_temperature(self, sensor_type: str) -> Optional[float]:
        """Lese Temperatur mit Caching."""
        if self._is_cache_valid(sensor_type):
            return self._cache.get(sensor_type)
        
        try:
            command = VCONTROLD_COMMANDS.get(sensor_type)
            if not command:
                _LOGGER.error(f"Unbekannter Sensor: {sensor_type}")
                return None
            
            response = self._send_command(command)
            
            # Parsen der Antwort (erwarten: "OK\n23.5" oder ähnlich)
            lines = response.split("\n")
            if len(lines) >= 2 and lines[0] == "OK":
                try:
                    temp = float(lines[1])
                    # Cache aktualisieren
                    self._cache[sensor_type] = temp
                    self._cache_time[sensor_type] = datetime.now()
                    return temp
                except ValueError:
                    _LOGGER.error(f"Konnte Temperatur nicht parsen: {response}")
                    return None
            else:
                _LOGGER.error(f"Unerwartete Antwort von vcontrold: {response}")
                return None
                
        except RuntimeError as e:
            _LOGGER.error(f"Fehler beim Auslesen von {sensor_type}: {e}")
            return None

    def set_temperature(self, command: str, value: float) -> bool:
        """Setze Temperatur."""
        try:
            full_command = f"{command} {value}"
            response = self._send_command(full_command)
            
            # Cache invalidieren
            if command == "setTempWWsoll":
                self._cache.pop("getTempWWsoll", None)
            
            if response.startswith("OK"):
                _LOGGER.info(f"Erfolgreich: {full_command}")
                return True
            else:
                _LOGGER.error(f"vcontrold Fehler: {response}")
                return False
                
        except RuntimeError as e:
            _LOGGER.error(f"Fehler beim Setzen: {e}")
            return False

    def set_operating_mode(self, mode: str) -> bool:
        """Setze Betriebsart."""
        try:
            command = f"setBetriebsart {mode}"
            response = self._send_command(command)
            
            if response.startswith("OK"):
                _LOGGER.info(f"Betriebsart geändert auf: {mode}")
                return True
            else:
                _LOGGER.error(f"vcontrold Fehler: {response}")
                return False
                
        except RuntimeError as e:
            _LOGGER.error(f"Fehler beim Setzen der Betriebsart: {e}")
            return False

    def is_available(self) -> bool:
        """Prüfe Verfügbarkeit von vcontrold."""
        try:
            response = self._send_command("ping")
            return response.startswith("OK")
        except Exception:
            return False

    def cleanup(self):
        """Räume auf."""
        self._disconnect()
