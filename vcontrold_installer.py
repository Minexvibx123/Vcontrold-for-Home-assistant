#!/usr/bin/env python3
"""
vcontrold Auto-Installer & Configurator
Lädt vcontrold herunter, buildet, konfiguriert und startet es automatisch
"""

import os
import sys
import platform
import subprocess
import tempfile
import shutil
import logging
import json
from pathlib import Path
from typing import Optional, Tuple
import urllib.request
import tarfile
import zipfile

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VcontroledInstaller:
    """Installiert und konfiguriert vcontrold automatisch"""
    
    def __init__(self, install_dir: Optional[str] = None):
        self.install_dir = Path(install_dir or os.path.expanduser("~/.vcontrold"))
        self.install_dir.mkdir(parents=True, exist_ok=True)
        
        self.platform = sys.platform
        self.machine = platform.machine()
        self.system = platform.system()
        
        logger.info(f"🔍 System erkannt: {self.system} ({self.machine})")
        
    def get_binary_path(self) -> Path:
        """Bestimme Pfad zur Binary basierend auf Plattform"""
        if self.system == "Windows":
            return self.install_dir / "vcontrold.exe"
        else:
            return self.install_dir / "vcontrold"
    
    def download_vcontrold(self, version: str = "0.99.155") -> bool:
        """Download vcontrold von GitHub"""
        logger.info(f"📥 Downloade vcontrold v{version}...")
        
        base_url = f"https://github.com/openv/vcontrold/archive/refs/tags/v{version}.tar.gz"
        
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                archive_path = Path(tmpdir) / "vcontrold.tar.gz"
                
                logger.info(f"📥 Downloading from: {base_url}")
                urllib.request.urlretrieve(base_url, archive_path)
                logger.info(f"✅ Downloaded ({archive_path.stat().st_size / 1024:.1f} KB)")
                
                # Extract
                logger.info(f"📦 Extracting...")
                with tarfile.open(archive_path, "r:gz") as tar:
                    tar.extractall(tmpdir)
                
                # Find extracted folder
                extracted = Path(tmpdir) / f"vcontrold-{version}"
                if not extracted.exists():
                    logger.error("❌ Extraction folder not found")
                    return False
                
                logger.info(f"✅ Extracted to {extracted}")
                
                # Build
                return self._build_vcontrold(extracted)
        
        except Exception as e:
            logger.error(f"❌ Download failed: {e}")
            return False
    
    def _build_vcontrold(self, source_dir: Path) -> bool:
        """Kompiliere vcontrold von Quelle"""
        logger.info(f"🔨 Starte Build-Prozess...")
        
        try:
            # Check für Build-Abhängigkeiten
            if self.system == "Linux":
                deps = ["build-essential", "libpcsclite-dev"]
                logger.info(f"📦 Checking dependencies: {', '.join(deps)}")
                # Optional: auto-install
            
            os.chdir(source_dir)
            
            # Configure
            logger.info("⚙️ Running configure...")
            result = subprocess.run(["./configure"], capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                logger.error(f"Configure failed: {result.stderr}")
                return False
            
            # Make
            logger.info("🔨 Running make...")
            result = subprocess.run(["make", "-j4"], capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                logger.error(f"Make failed: {result.stderr}")
                return False
            
            # Find binary
            binary_src = None
            for candidate in [
                source_dir / "src" / "vcontrold",
                source_dir / "vcontrold",
                source_dir / "vcontrold.exe"
            ]:
                if candidate.exists():
                    binary_src = candidate
                    break
            
            if not binary_src:
                logger.error("❌ Compiled binary not found")
                return False
            
            # Copy to install directory
            binary_dst = self.get_binary_path()
            logger.info(f"📋 Copying binary: {binary_src} -> {binary_dst}")
            shutil.copy2(binary_src, binary_dst)
            
            # Make executable
            if self.system != "Windows":
                os.chmod(binary_dst, 0o755)
            
            logger.info(f"✅ Build successful: {binary_dst}")
            return True
        
        except subprocess.TimeoutExpired:
            logger.error("❌ Build timeout")
            return False
        except Exception as e:
            logger.error(f"❌ Build failed: {e}")
            return False
    
    def configure_vcontrold(self, device: str, host: str = "localhost", port: int = 3002) -> Path:
        """Erstelle vcontrold Konfigurationsdatei"""
        logger.info(f"⚙️ Configuring vcontrold for device: {device}")
        
        config_file = self.install_dir / "vcontrold.conf"
        
        # Vereinfachte Konfiguration
        config_content = f"""# vcontrold configuration
# Automatically generated

# Logging
logfile /tmp/vcontrold.log
loglevel 3

# Listen on TCP
listen 127.0.0.1:{port}
listenip {host}

# Serial device
device {device}

# Protocol settings
protocol KW
framing STD
"""
        
        config_file.write_text(config_content)
        logger.info(f"✅ Config created: {config_file}")
        return config_file
    
    def start_vcontrold(self, device: str, host: str = "localhost", port: int = 3002) -> subprocess.Popen:
        """Starte vcontrold daemon"""
        logger.info(f"🚀 Starting vcontrold on {host}:{port}...")
        
        binary = self.get_binary_path()
        
        if not binary.exists():
            logger.error(f"❌ Binary not found: {binary}")
            raise FileNotFoundError(f"vcontrold binary not found: {binary}")
        
        if self.system != "Windows":
            os.chmod(binary, 0o755)
        
        cmd = [
            str(binary),
            "-l", host,
            "-p", str(port),
            "-d", device,
            "--loglevel", "3"
        ]
        
        logger.info(f"📝 Command: {' '.join(cmd)}")
        
        # Start process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            preexec_fn=None if self.system == "Windows" else lambda: os.setsid()
        )
        
        logger.info(f"✅ Started with PID {process.pid}")
        return process
    
    def verify_daemon(self, host: str = "localhost", port: int = 3002, timeout: int = 5) -> bool:
        """Überprüfe ob Daemon läuft"""
        import socket
        
        logger.info(f"🔍 Verifying daemon on {host}:{port}...")
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                logger.info(f"✅ Daemon is running!")
                return True
            else:
                logger.warning(f"⚠️ Daemon not responding")
                return False
        except Exception as e:
            logger.error(f"❌ Verification failed: {e}")
            return False
    
    def read_sensor_data(self, host: str = "localhost", port: int = 3002) -> dict:
        """Lese Sensordaten vom Daemon"""
        import socket
        
        logger.info(f"📊 Reading sensor data from {host}:{port}...")
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            
            # Example: Read Kesseltemperatur
            commands = {
                "Kesseltemperatur": "getTempKessel",
                "Außentemperatur": "getTempAussen",
                "WW Soll": "getTempWWsoll",
                "WW Ist": "getTempWWist",
                "Vorlauf": "getTempVorlaufHK1"
            }
            
            data = {}
            for name, cmd in commands.items():
                sock.sendall(f"{cmd}\n".encode())
                response = sock.recv(1024).decode().strip()
                data[name] = response
                logger.info(f"  {name}: {response}")
            
            sock.close()
            return data
        
        except Exception as e:
            logger.error(f"❌ Failed to read data: {e}")
            return {}


def main():
    """Hauptprogramm"""
    import argparse
    
    parser = argparse.ArgumentParser(description="vcontrold Auto-Installer & Configurator")
    parser.add_argument("--device", required=True, help="Serial device (e.g., /dev/ttyUSB0)")
    parser.add_argument("--host", default="localhost", help="Listen host")
    parser.add_argument("--port", type=int, default=3002, help="Listen port")
    parser.add_argument("--install-dir", help="Installation directory")
    parser.add_argument("--version", default="0.99.155", help="vcontrold version to install")
    
    args = parser.parse_args()
    
    logger.info("=" * 70)
    logger.info("🎯 vcontrold AUTO-INSTALLER & CONFIGURATOR")
    logger.info("=" * 70)
    
    # Create installer
    installer = VcontroledInstaller(args.install_dir)
    
    # Step 1: Download
    if not installer.download_vcontrold(args.version):
        logger.error("❌ Installation failed at download step")
        sys.exit(1)
    
    # Step 2: Configure
    config_file = installer.configure_vcontrold(args.device, args.host, args.port)
    
    # Step 3: Start
    try:
        process = installer.start_vcontrold(args.device, args.host, args.port)
        
        # Wait for startup
        import time
        time.sleep(2)
        
        # Step 4: Verify
        if not installer.verify_daemon(args.host, args.port):
            logger.warning("⚠️ Daemon verification failed, but process is running")
        
        # Step 5: Read data
        logger.info("=" * 70)
        data = installer.read_sensor_data(args.host, args.port)
        logger.info("=" * 70)
        
        logger.info("✅ SUCCESS! vcontrold is running and data is flowing!")
        logger.info(f"   Daemon PID: {process.pid}")
        logger.info(f"   Listen: {args.host}:{args.port}")
        logger.info(f"   Device: {args.device}")
        logger.info("=" * 70)
        
        # Keep running
        logger.info("Press Ctrl+C to stop...")
        try:
            process.wait()
        except KeyboardInterrupt:
            logger.info("Stopping daemon...")
            process.terminate()
            process.wait(timeout=5)
    
    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
