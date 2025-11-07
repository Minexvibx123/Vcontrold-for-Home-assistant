"""vcontrold Daemon Manager - Verwaltet vcontrold Prozess."""
import asyncio
import logging
import os
import platform
import subprocess
import time
from pathlib import Path
from typing import Optional

_LOGGER = logging.getLogger(__name__)


class VcontroledDaemonManager:
    """Manager für vcontrold Daemon Prozess."""

    def __init__(self, config_dir: str):
        """Initialisiere Daemon Manager.
        
        Args:
            config_dir: Home Assistant config directory path
        """
        self.config_dir = Path(config_dir)
        self.daemon_dir = self.config_dir / "vcontrold_daemon"
        self.daemon_log = self.daemon_dir / "vcontrold.log"
        
        # Daemon Binary Pfade je nach Betriebssystem
        self.is_windows = platform.system() == "Windows"
        self.is_macos = platform.system() == "Darwin"
        self.is_linux = platform.system() == "Linux"
        
        self.daemon_binary = self._get_daemon_binary_path()
        self._process: Optional[subprocess.Popen] = None
        self._running = False

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
        host: str = "localhost",
        port: int = 3002,
        device: str = "/dev/ttyUSB0",
        log_level: str = "ERROR",
    ) -> bool:
        """Starte vcontrold Daemon.
        
        Args:
            host: Listen Host
            port: Listen Port
            device: Serielles Gerät (z.B. /dev/ttyUSB0)
            log_level: Log Level (ERROR, WARN, INFO, DEBUG)
            
        Returns:
            True wenn erfolgreich gestartet, False sonst
        """
        if self._running:
            _LOGGER.warning("vcontrold Daemon läuft bereits")
            return True

        if not self._ensure_daemon_dir():
            return False

        try:
            # Logfile öffnen
            log_file = open(self.daemon_log, "a", encoding="utf-8")
            
            # Command zusammenstellen
            cmd = [
                str(self.daemon_binary),
                "-l", str(host),
                "-p", str(port),
                "-d", device,
                "--loglevel", log_level,
            ]
            
            _LOGGER.info(f"Starte vcontrold Daemon: {' '.join(cmd)}")
            
            # Prozess starten
            self._process = subprocess.Popen(
                cmd,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                cwd=str(self.daemon_dir),
            )
            
            # Kurz warten um zu prüfen ob es erfolgreich gestartet ist
            await asyncio.sleep(1)
            
            if self._process.poll() is not None:
                # Prozess ist bereits beendet (Fehler)
                _LOGGER.error(f"vcontrold Daemon konnte nicht gestartet werden")
                return False
            
            self._running = True
            _LOGGER.info(f"vcontrold Daemon gestartet (PID: {self._process.pid})")
            return True
            
        except FileNotFoundError:
            _LOGGER.error(f"vcontrold Binary nicht gefunden: {self.daemon_binary}")
            return False
        except Exception as e:
            _LOGGER.error(f"Fehler beim Starten des vcontrold Daemons: {e}")
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
        """Hole Daemon Status."""
        return {
            "running": self.is_running(),
            "pid": self._process.pid if self._process else None,
            "binary": str(self.daemon_binary),
            "log_file": str(self.daemon_log),
            "exists": self.daemon_binary.exists(),
        }

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
ExecStart={self.daemon_binary} -l localhost -p 3002 -d /dev/ttyUSB0 --loglevel ERROR
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
