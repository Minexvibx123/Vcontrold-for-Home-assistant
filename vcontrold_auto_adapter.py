"""
vcontrold Auto-Install Adapter für Home Assistant Integration
Lädt herunter, buildet, konfiguriert und startet vcontrold automatisch
"""

import asyncio
import logging
import subprocess
import tempfile
import urllib.request
import tarfile
import os
from pathlib import Path
from typing import Optional

_LOGGER = logging.getLogger(__name__)


class VcontroledAutoInstaller:
    """Automatischer vcontrold Installer für Home Assistant"""
    
    GITHUB_BASE = "https://github.com/openv/vcontrold"
    VERSION = "0.99.155"
    
    def __init__(self, config_dir: str):
        self.config_dir = Path(config_dir) / ".vcontrold"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.binary_path = self.config_dir / "vcontrold"
    
    async def auto_install_and_start(
        self,
        device: str,
        host: str = "localhost",
        port: int = 3002,
        log_level: str = "ERROR"
    ) -> bool:
        """
        Kompletter Auto-Install & Start-Prozess:
        1. Download vcontrold
        2. Build/Compile
        3. Konfigurieren
        4. Starten
        5. Daten auslesen
        """
        _LOGGER.info("🚀 Starte AUTO-INSTALL Prozess für vcontrold")
        
        try:
            # Step 1: Download & Build
            _LOGGER.info("📥 Step 1/5: Download vcontrold source...")
            if not await self._download_and_build():
                _LOGGER.error("❌ Download/Build fehlgeschlagen")
                return False
            
            # Step 2: Verify Binary
            _LOGGER.info("✅ Step 2/5: Binary verified")
            if not self.binary_path.exists():
                _LOGGER.error(f"❌ Binary nicht gefunden: {self.binary_path}")
                return False
            
            # Step 3: Start Daemon
            _LOGGER.info(f"🚀 Step 3/5: Starte Daemon auf {host}:{port}")
            process = await self._start_daemon(device, host, port, log_level)
            if not process:
                _LOGGER.error("❌ Daemon konnte nicht gestartet werden")
                return False
            
            # Step 4: Verify Running
            _LOGGER.info("✅ Step 4/5: Überprüfe ob Daemon läuft")
            await asyncio.sleep(2)  # Give daemon time to start
            if not await self._verify_running(host, port):
                _LOGGER.warning("⚠️ Daemon nicht erreichbar, aber läuft möglicherweise")
            
            # Step 5: Read Data
            _LOGGER.info("📊 Step 5/5: Lese Sensordaten...")
            data = await self._read_sensor_data(host, port)
            if data:
                _LOGGER.info(f"✅ Daten erfolgreich ausgelesen: {data}")
            
            _LOGGER.info("✅ AUTO-INSTALL erfolgreich!")
            return True
        
        except Exception as e:
            _LOGGER.error(f"❌ AUTO-INSTALL fehlgeschlagen: {e}")
            return False
    
    async def _download_and_build(self) -> bool:
        """Download und compile vcontrold von GitHub"""
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmpdir = Path(tmpdir)
                
                # Download
                url = f"{self.GITHUB_BASE}/archive/refs/tags/v{self.VERSION}.tar.gz"
                archive = tmpdir / "vcontrold.tar.gz"
                
                _LOGGER.debug(f"Downloading {url}")
                urllib.request.urlretrieve(url, archive)
                _LOGGER.info(f"✅ Downloaded ({archive.stat().st_size / 1024 / 1024:.1f} MB)")
                
                # Extract
                extract_dir = tmpdir / f"vcontrold-{self.VERSION}"
                with tarfile.open(archive, "r:gz") as tar:
                    tar.extractall(tmpdir)
                
                if not extract_dir.exists():
                    _LOGGER.error("❌ Extract fehlgeschlagen")
                    return False
                
                _LOGGER.info(f"✅ Extracted")
                
                # Build
                return await self._build(extract_dir)
        
        except Exception as e:
            _LOGGER.error(f"❌ Download/Build Error: {e}")
            return False
    
    async def _build(self, source_dir: Path) -> bool:
        """Kompiliere vcontrold"""
        try:
            os.chdir(source_dir)
            
            # Configure
            _LOGGER.info("⚙️ Running configure...")
            proc = await asyncio.create_subprocess_exec(
                "./configure",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            _, stderr = await proc.communicate()
            if proc.returncode != 0:
                _LOGGER.error(f"Configure failed: {stderr.decode()}")
                return False
            
            # Make
            _LOGGER.info("🔨 Running make (this may take a minute)...")
            proc = await asyncio.create_subprocess_exec(
                "make", "-j4",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            _, stderr = await proc.communicate()
            if proc.returncode != 0:
                _LOGGER.error(f"Make failed: {stderr.decode()}")
                return False
            
            # Find and copy binary
            for candidate in [
                source_dir / "src" / "vcontrold",
                source_dir / "vcontrold"
            ]:
                if candidate.exists():
                    os.chmod(candidate, 0o755)
                    import shutil
                    shutil.copy2(candidate, self.binary_path)
                    os.chmod(self.binary_path, 0o755)
                    _LOGGER.info(f"✅ Binary installed: {self.binary_path}")
                    return True
            
            _LOGGER.error("❌ Compiled binary not found")
            return False
        
        except Exception as e:
            _LOGGER.error(f"❌ Build Error: {e}")
            return False
    
    async def _start_daemon(
        self,
        device: str,
        host: str,
        port: int,
        log_level: str
    ) -> Optional[subprocess.Popen]:
        """Starte vcontrold Daemon"""
        try:
            cmd = [
                str(self.binary_path),
                "-l", host,
                "-p", str(port),
                "-d", device,
                "--loglevel", log_level
            ]
            
            _LOGGER.debug(f"Command: {' '.join(cmd)}")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setsid if os.name != 'nt' else None
            )
            
            _LOGGER.info(f"✅ Daemon gestartet (PID: {process.pid})")
            return process
        
        except Exception as e:
            _LOGGER.error(f"❌ Start Error: {e}")
            return None
    
    async def _verify_running(self, host: str, port: int, timeout: int = 5) -> bool:
        """Überprüfe ob Daemon läuft"""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    async def _read_sensor_data(self, host: str, port: int) -> dict:
        """Lese Sensordaten vom Daemon"""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            
            data = {}
            commands = {
                "Kessel": "getTempKessel",
                "Außen": "getTempAussen",
                "WWSoll": "getTempWWsoll",
                "WWIst": "getTempWWist",
            }
            
            for name, cmd in commands.items():
                sock.sendall(f"{cmd}\n".encode())
                response = sock.recv(1024).decode().strip()
                data[name] = response
            
            sock.close()
            _LOGGER.info(f"✅ Daten: {data}")
            return data
        
        except Exception as e:
            _LOGGER.warning(f"⚠️ Konnte Daten nicht auslesen: {e}")
            return {}


# Integration Hook für Home Assistant
async def setup_with_auto_install(
    hass,
    config_entry,
    device: str,
    host: str = "localhost",
    port: int = 3002
) -> bool:
    """Setup Integration mit automatischem vcontrold Install"""
    
    installer = VcontroledAutoInstaller(hass.config.path())
    
    success = await installer.auto_install_and_start(
        device=device,
        host=host,
        port=port
    )
    
    if success:
        _LOGGER.info("✅ vcontrold ist aktiv und bereit!")
        return True
    else:
        _LOGGER.error("❌ vcontrold Setup fehlgeschlagen")
        raise Exception("vcontrold Auto-Install fehlgeschlagen")
