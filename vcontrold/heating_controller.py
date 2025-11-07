"""Viessmann Heizungssteuerung - Native Python Implementation (Embedded)."""
import asyncio
import logging
import struct
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Dict, Any
import serial
import serial.tools.list_ports

_LOGGER = logging.getLogger(__name__)


class Framing(Enum):
    """Protokoll-Varianten für Viessmann Heizungen."""
    RAW = "raw"
    FRAMING = "framing"
    KW = "kw"


class CRCCalculator:
    """CRC-16 Berechnung für Viessmann Protokoll."""
    
    CRC_TABLE = None
    
    @classmethod
    def _init_crc_table(cls):
        """Initialisiere CRC Tabelle."""
        if cls.CRC_TABLE is not None:
            return
        
        cls.CRC_TABLE = []
        for i in range(256):
            crc = i
            for _ in range(8):
                if crc & 1:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
            cls.CRC_TABLE.append(crc)
    
    @staticmethod
    def calculate(data: bytes) -> int:
        """Berechne CRC-16."""
        CRCCalculator._init_crc_table()
        crc = 0
        
        for byte in data:
            crc = (CRCCalculator.CRC_TABLE[byte ^ (crc & 0xFF)]) ^ (crc >> 8)
        
        return crc


class ViessmannProtocol:
    """Viessmann Heizungs-Protokoll Implementierung."""
    
    # Kommandos
    COMMANDS = {
        "getTempKessel": bytes([0x00, 0x01]),
        "getTempAussen": bytes([0x00, 0x0d]),
        "getTempWWsoll": bytes([0x00, 0x40]),
        "getTempWWist": bytes([0x00, 0x41]),
        "getTempVorlaufHK1": bytes([0x00, 0x02]),
        "setTempWWsoll": bytes([0x01, 0x40]),
        "setBetriebsart": bytes([0x01, 0x20]),
    }
    
    # Antwort Prefixes
    RESPONSE_OK = bytes([0x06])
    RESPONSE_ERROR = bytes([0x15])
    
    @staticmethod
    def create_command(cmd_name: str, value: Optional[float] = None) -> bytes:
        """Erstelle Kommando Bytes."""
        if cmd_name not in ViessmannProtocol.COMMANDS:
            raise ValueError(f"Unbekanntes Kommando: {cmd_name}")
        
        cmd = ViessmannProtocol.COMMANDS[cmd_name]
        
        if value is not None:
            # Set-Kommando mit Wert
            # Format: [MSB, LSB] in Viessmann Encoding
            value_int = int(value * 2)  # Auflösung: 0.5°C
            value_bytes = struct.pack(">H", value_int)
            payload = cmd + value_bytes
        else:
            # Get-Kommando
            payload = cmd
        
        # CRC anhängen
        crc = CRCCalculator.calculate(payload)
        crc_bytes = struct.pack("<H", crc)
        
        return payload + crc_bytes
    
    @staticmethod
    def parse_response(data: bytes) -> Optional[float]:
        """Parse Temperaturwert aus Response."""
        if len(data) < 4:
            return None
        
        if data[0:1] == ViessmannProtocol.RESPONSE_ERROR:
            return None
        
        if data[0:1] == ViessmannProtocol.RESPONSE_OK:
            try:
                # Temperatur in Bytes 1-2 (Big Endian)
                temp_raw = struct.unpack(">H", data[1:3])[0]
                # Auflösung: 0.5°C
                temp = temp_raw / 2.0
                return temp
            except struct.error:
                return None
        
        return None


class ViessmannHeatingController:
    """Direkte Kommunikation mit Viessmann Heizung via serielle Schnittstelle."""
    
    def __init__(
        self,
        port: str = "/dev/ttyUSB0",
        baudrate: int = 9600,
        timeout: int = 10,
        framing: Framing = Framing.KW,
        cache_ttl: int = 30,
    ):
        """Initialisiere Controller.
        
        Args:
            port: Serieller Port (z.B. /dev/ttyUSB0, COM3)
            baudrate: Baud-Rate (Standard: 9600)
            timeout: Socket Timeout in Sekunden
            framing: Protokoll-Variante (RAW, FRAMING, KW)
            cache_ttl: Cache TTL in Sekunden
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.framing = framing
        self.cache_ttl = cache_ttl
        
        self._serial: Optional[serial.Serial] = None
        self._connected = False
        
        # Cache
        self._cache: Dict[str, Any] = {}
        self._cache_time: Dict[str, datetime] = {}
    
    def connect(self) -> bool:
        """Verbinde zur Heizung."""
        try:
            self._serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_EVEN,
                stopbits=serial.STOPBITS_TWO,
            )
            self._connected = True
            _LOGGER.info(f"Verbunden zu Heizung auf {self.port}")
            return True
        except serial.SerialException as e:
            _LOGGER.error(f"Fehler beim Verbinden zu {self.port}: {e}")
            self._connected = False
            return False
    
    def disconnect(self) -> None:
        """Trenne Verbindung."""
        if self._serial:
            try:
                self._serial.close()
            except Exception:
                pass
        self._connected = False
        _LOGGER.debug("Verbindung getrennt")
    
    def is_connected(self) -> bool:
        """Prüfe Verbindungsstatus."""
        return self._connected and self._serial is not None and self._serial.is_open
    
    def _send_recv(self, cmd_bytes: bytes, read_bytes: int = 4) -> Optional[bytes]:
        """Sende Kommando und empfange Response."""
        if not self.is_connected():
            if not self.connect():
                return None
        
        try:
            # Leere Buffer
            self._serial.reset_input_buffer()
            self._serial.reset_output_buffer()
            
            # Sende Kommando
            self._serial.write(cmd_bytes)
            
            # Lese Response
            response = self._serial.read(read_bytes)
            
            if not response:
                _LOGGER.warning("Keine Antwort von Heizung")
                return None
            
            _LOGGER.debug(f"Response: {response.hex()}")
            return response
        
        except serial.SerialException as e:
            _LOGGER.error(f"Serielle Fehler: {e}")
            self._connected = False
            return None
        except Exception as e:
            _LOGGER.error(f"Fehler beim Kommando: {e}")
            return None
    
    def _is_cache_valid(self, key: str) -> bool:
        """Prüfe ob Cache noch gültig ist."""
        if key not in self._cache_time:
            return False
        
        time_diff = datetime.now() - self._cache_time[key]
        return time_diff < timedelta(seconds=self.cache_ttl)
    
    def get_temperature(self, sensor_type: str) -> Optional[float]:
        """Lese Temperaturwert mit Caching."""
        # Prüfe Cache
        if self._is_cache_valid(sensor_type):
            return self._cache.get(sensor_type)
        
        try:
            # Erstelle Kommando
            cmd = ViessmannProtocol.create_command(sensor_type)
            
            # Sende & empfange
            response = self._send_recv(cmd)
            
            if response is None:
                return None
            
            # Parse Response
            temp = ViessmannProtocol.parse_response(response)
            
            if temp is not None:
                # Cache aktualisieren
                self._cache[sensor_type] = temp
                self._cache_time[sensor_type] = datetime.now()
                _LOGGER.debug(f"{sensor_type}: {temp}°C")
            
            return temp
        
        except Exception as e:
            _LOGGER.error(f"Fehler beim Auslesen {sensor_type}: {e}")
            return None
    
    def set_temperature(self, command: str, value: float) -> bool:
        """Setze Temperaturwert."""
        if value < 20 or value > 80:
            _LOGGER.error(f"Temperatur {value}°C außerhalb Bereich (20-80°C)")
            return False
        
        try:
            # Erstelle Kommando mit Wert
            cmd = ViessmannProtocol.create_command(command, value)
            
            # Sende & empfange
            response = self._send_recv(cmd)
            
            if response is None:
                return False
            
            # Prüfe OK Response
            is_ok = response[0:1] == ViessmannProtocol.RESPONSE_OK
            
            if is_ok:
                # Cache invalidieren
                self._cache.pop(command.replace("set", "get"), None)
                _LOGGER.info(f"{command} {value}°C erfolgreich gesetzt")
            else:
                _LOGGER.error(f"{command} fehlgeschlagen: {response.hex()}")
            
            return is_ok
        
        except Exception as e:
            _LOGGER.error(f"Fehler beim Setzen: {e}")
            return False
    
    def set_operating_mode(self, mode: str) -> bool:
        """Setze Betriebsart."""
        mode_map = {
            "auto": 0x00,
            "standby": 0x01,
            "party": 0x02,
            "eco": 0x03,
        }
        
        if mode not in mode_map:
            _LOGGER.error(f"Unbekannte Betriebsart: {mode}")
            return False
        
        try:
            mode_value = float(mode_map[mode])
            result = self.set_temperature("setBetriebsart", mode_value)
            
            if result:
                _LOGGER.info(f"Betriebsart auf {mode} gesetzt")
            
            return result
        
        except Exception as e:
            _LOGGER.error(f"Fehler beim Setzen der Betriebsart: {e}")
            return False
    
    @staticmethod
    def find_ports() -> list:
        """Finde verfügbare serielle Ports."""
        ports = []
        for port in serial.tools.list_ports.comports():
            ports.append({
                "device": port.device,
                "description": port.description,
                "hwid": port.hwid,
            })
        return ports
    
    def get_info(self) -> dict:
        """Hole Informationen über die Verbindung."""
        return {
            "port": self.port,
            "baudrate": self.baudrate,
            "framing": self.framing.value,
            "connected": self.is_connected(),
            "cache_size": len(self._cache),
            "cache_ttl": self.cache_ttl,
        }
    
    def cleanup(self) -> None:
        """Räume auf."""
        self.disconnect()
