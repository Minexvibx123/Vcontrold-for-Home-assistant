"""vcontrold Daemon Manager - Verwaltet vcontrold Prozess (All-in-One)."""
import asyncio
import logging
import os
import platform
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import signal

_LOGGER = logging.getLogger(__name__)


class VcontroledDaemonManager:
    """Manager für vcontrold Daemon Prozess - All-in-One Integration."""

    def __init__(self, config_dir: str, device: str = "/dev/ttyUSB0", host: str = "localhost", port: int = 3002):
        """Initialisiere Daemon Manager.
        
        Args:
            config_dir: Home Assistant config directory path
            device: Serielles Gerät (z.B. /dev/ttyUSB0)
            host: Listen Host (default: localhost)
            port: Listen Port (default: 3002)
        """
        self.config_dir = Path(config_dir)
        self.daemon_dir = self.config_dir / "vcontrold_daemon"
        self.daemon_log = self.daemon_dir / "vcontrold.log"
        self.daemon_config = self.daemon_dir / "vcontrold.conf"
        
        # Konfiguration
        self.device = device
        self.host = host
        self.port = port
        
        # Daemon Binary Pfade je nach Betriebssystem
        self.is_windows = platform.system() == "Windows"
        self.is_macos = platform.system() == "Darwin"
        self.is_linux = platform.system() == "Linux"
        
        self.daemon_binary = self._get_daemon_binary_path()
        self._process: Optional[subprocess.Popen] = None
        self._running = False
        self._start_time: Optional[datetime] = None
        self._health_check_count = 0
        self._last_health_check: Optional[datetime] = None

    def _get_daemon_binary_path(self) -> Path:
        """Bestimme Pfad zum vcontrold Binary."""
        if self.is_windows:
            return self.daemon_dir / "vcontrold.exe"
        elif self.is_macos:
            return self.daemon_dir / "vcontrold_macos"
        else:  # Linux
            return self.daemon_dir / "vcontrold_linux"

    def _ensure_daemon_dir(self) -> bool:
        """Stelle sicher dass Daemon Verzeichnis existiert."""
        try:
            self.daemon_dir.mkdir(parents=True, exist_ok=True)
            self.daemon_log.parent.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            _LOGGER.error(f"Fehler beim Erstellen des Daemon Verzeichnisses: {e}")
            return False

    async def start_daemon(
        self,
        device: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        log_level: str = "ERROR",
    ) -> bool:
        """Starte vcontrold Daemon.
        
        Args:
            device: Serielles Gerät (default: aus config)
            host: Listen Host (default: aus config)
            port: Listen Port (default: aus config)
            log_level: Log Level (ERROR, WARN, INFO, DEBUG)
            
        Returns:
            True wenn erfolgreich gestartet, False sonst
        """
        if self._running:
            _LOGGER.warning("vcontrold Daemon läuft bereits")
            return True

        # Nutze Parameter oder Config-Werte
        device = device or self.device
        host = host or self.host
        port = port or self.port
        
        if not self._ensure_daemon_dir():
            return False

        try:
            # Logfile öffnen
            log_file = open(self.daemon_log, "a", encoding="utf-8")
            
            # Command zusammenstellen - direkter Befehl oder via Konfigurationsdatei
            if self.is_linux or self.is_macos:
                # Unix: direkter vcontrold Befehl
                cmd = [
                    str(self.daemon_binary),
                    "-l", str(host),
                    "-p", str(port),
                    "-d", device,
                    "--loglevel", log_level,
                ]
            else:
                # Windows: Binary mit Parametern
                cmd = [
                    str(self.daemon_binary),
                    "-l", str(host),
                    "-p", str(port),
                    "-d", device,
                    "--loglevel", log_level,
                ]
            
            _LOGGER.info(f"🚀 Starte vcontrold Daemon auf {host}:{port} (Gerät: {device})")
            _LOGGER.debug(f"Kommando: {' '.join(cmd)}")
            
            # Prozess starten
            self._process = subprocess.Popen(
                cmd,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                cwd=str(self.daemon_dir) if self.daemon_dir.exists() else None,
                preexec_fn=os.setsid if not self.is_windows else None,  # Process group (Unix)
            )
            
            # Kurz warten um zu prüfen ob es erfolgreich gestartet ist
            await asyncio.sleep(2)
            
            if self._process.poll() is not None:
                # Prozess ist bereits beendet (Fehler)
                error_msg = f"vcontrold Daemon konnte nicht gestartet werden (Exit Code: {self._process.returncode})"
                _LOGGER.error(error_msg)
                log_file.close()
                return False
            
            self._running = True
            self._start_time = datetime.now()
            _LOGGER.info(f"✅ vcontrold Daemon erfolgreich gestartet (PID: {self._process.pid})")
            return True
            
        except FileNotFoundError as e:
            _LOGGER.error(f"❌ vcontrold Binary nicht gefunden: {self.daemon_binary}")
            _LOGGER.error(f"   Bitte lade vcontrold Binary herunter von: https://github.com/openv/vcontrold/releases")
            return False
        except Exception as e:
            _LOGGER.error(f"❌ Fehler beim Starten des vcontrold Daemons: {e}")
            self._running = False
            return False

    async def stop_daemon(self) -> bool:
        """Stoppe vcontrold Daemon.
        
        Returns:
            True wenn erfolgreich gestoppt
        """
        if not self._running or self._process is None:
            return True

        try:
            _LOGGER.info(f"Stoppe vcontrold Daemon (PID: {self._process.pid})")
            
            # SIGTERM senden
            self._process.terminate()
            
            # Warten auf Beendigung (max 5 Sekunden)
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Erzwinge Beendigung
                _LOGGER.warning("vcontrold Daemon antwortet nicht, erzwinge Beendigung")
                self._process.kill()
                self._process.wait()
            
            self._running = False
            self._process = None
            _LOGGER.info("vcontrold Daemon beendet")
            return True
            
        except Exception as e:
            _LOGGER.error(f"Fehler beim Stoppen des vcontrold Daemons: {e}")
            self._running = False
            return False

    def is_running(self) -> bool:
        """Prüfe ob Daemon läuft."""
        if self._process is None:
            return False
        
        return self._process.poll() is None

    def get_daemon_status(self) -> dict:
        """Hole detaillierten Daemon Status."""
        import socket
        
        uptime = None
        if self._start_time:
            uptime = (datetime.now() - self._start_time).total_seconds()
        
        return {
            "running": self.is_running(),
            "pid": self._process.pid if self._process else None,
            "binary": str(self.daemon_binary),
            "binary_exists": self.daemon_binary.exists(),
            "log_file": str(self.daemon_log),
            "config": {
                "device": self.device,
                "host": self.host,
                "port": self.port,
            },
            "uptime_seconds": uptime,
            "start_time": self._start_time.isoformat() if self._start_time else None,
            "health_checks": self._health_check_count,
            "last_health_check": self._last_health_check.isoformat() if self._last_health_check else None,
        }
    
    async def health_check(self) -> bool:
        """Prüfe Daemon Gesundheitsstatus via TCP."""
        import socket
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.host, self.port))
            sock.close()
            
            self._health_check_count += 1
            self._last_health_check = datetime.now()
            
            if result == 0:
                _LOGGER.debug(f"✅ vcontrold Health Check OK ({self.host}:{self.port})")
                return True
            else:
                _LOGGER.warning(f"⚠️ vcontrold Health Check FAILED ({self.host}:{self.port})")
                return False
        except Exception as e:
            _LOGGER.error(f"❌ vcontrold Health Check Error: {e}")
            return False
    
    async def ensure_running(self, device: Optional[str] = None) -> bool:
        """Stelle sicher dass Daemon läuft - starte falls nötig."""
        if self.is_running():
            return await self.health_check()
        
        _LOGGER.warning("vcontrold Daemon nicht aktiv - versuche neu zu starten")
        device = device or self.device
        return await self.start_daemon(device=device)

    async def setup_native_service(self, user: str = "homeassistant") -> str:
        """Erstelle systemd Service für vcontrold.
        
        Args:
            user: Benutzer unter dem vcontrold laufen soll
            
        Returns:
            Systemd Service File Content
        """
        service_content = f"""[Unit]
Description=vcontrold Daemon - Viessmann Heating Control
After=network.target
Wants=homeassistant.service

[Service]
Type=simple
User={user}
ExecStart={self.daemon_binary} -l {self.host} -p {self.port} -d {self.device} --loglevel ERROR
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""
        return service_content

    async def check_binary_exists(self) -> bool:
        """Prüfe ob Binary existiert."""
        return self.daemon_binary.exists()

    async def get_binary_info(self) -> dict:
        """Hole Informationen über Binary."""
        if not await self.check_binary_exists():
            return {"exists": False, "message": "vcontrold Binary nicht gefunden"}
        
        try:
            result = subprocess.run(
                [str(self.daemon_binary), "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            
            return {
                "exists": True,
                "path": str(self.daemon_binary),
                "version": result.stdout.strip() if result.returncode == 0 else "Unbekannt",
            }
        except Exception as e:
            return {
                "exists": True,
                "path": str(self.daemon_binary),
                "error": str(e),
            }

    async def cleanup(self):
        """Räume auf."""
        await self.stop_daemon()
