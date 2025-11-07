"""
vcontrold Binary Download Manager
Lädt die notwendigen Binaries beim ersten Setup herunter
"""

import logging
import urllib.request
import zipfile
from pathlib import Path
from typing import Optional

_LOGGER = logging.getLogger(__name__)

# GitHub Release URLs für vcontrold v0.98.12
# Source: https://github.com/openv/vcontrold/releases/tag/v0.98.12
RELEASES = {
    "linux": "https://github.com/openv/vcontrold/releases/download/v0.98.12/vcontrold_0.98.12-16_amd64.zip",
    "linux_arm64": "https://github.com/openv/vcontrold/releases/download/v0.98.12/vcontrold_0.98.12-16_arm64.zip",
    "linux_armhf": "https://github.com/openv/vcontrold/releases/download/v0.98.12/vcontrold_0.98.12-16_armhf.zip",
    "windows": "https://github.com/openv/vcontrold/releases/download/v0.98.12/vcontrold_0.98.12-16-cygwin_x86_64.zip",
}


async def download_binary(install_dir: Path, platform: str) -> Optional[Path]:
    """Lade vcontrold Binary herunter und extrahiere sie"""
    
    _LOGGER.info(f"📥 Downloading vcontrold binary for {platform}...")
    
    if platform not in RELEASES:
        _LOGGER.error(f"❌ Platform not supported: {platform}")
        return None
    
    url = RELEASES[platform]
    binary_dir = install_dir / "vcontrold"
    binary_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        import tempfile
        import shutil
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Download
            archive = tmpdir / "vcontrold.zip"
            _LOGGER.debug(f"Downloading from: {url}")
            urllib.request.urlretrieve(url, archive)
            
            size_mb = archive.stat().st_size / 1024 / 1024
            _LOGGER.info(f"✅ Downloaded ({size_mb:.1f} MB)")
            
            # Extract ZIP
            _LOGGER.info("📦 Extracting...")
            with zipfile.ZipFile(archive, "r") as zip_ref:
                zip_ref.extractall(tmpdir)
            
            # Find binary (look for "vcontrold" or "vcontrold.exe")
            binary = None
            for candidate in tmpdir.glob("**/vcontrold*"):
                if candidate.is_file() and (candidate.name == "vcontrold" or candidate.name.endswith(".exe")):
                    binary = candidate
                    break
            
            if not binary:
                _LOGGER.error("❌ Binary not found in archive")
                return None
            
            # Copy to destination
            dest = binary_dir / "vcontrold"
            shutil.copy2(binary, dest)
            
            # Make executable
            import os
            os.chmod(dest, 0o755)
            
            _LOGGER.info(f"✅ Binary installed: {dest}")
            return dest
    
    except Exception as e:
        _LOGGER.error(f"❌ Download failed: {e}")
        return None
