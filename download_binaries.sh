#!/bin/bash
# Download vcontrold binaries for ALL-IN-ONE integration
# Usage: ./download_binaries.sh

set -e

echo "📥 Downloading vcontrold binaries for ALL-IN-ONE integration..."

VCONTROLD_VERSION="0.99.155"
BINARIES_DIR="custom_components/vcontrold/vcontrold"

# Ensure directories exist
mkdir -p "$BINARIES_DIR/linux"
mkdir -p "$BINARIES_DIR/windows"
mkdir -p "$BINARIES_DIR/macos"

# Download Linux x86_64 binary
echo "📥 Downloading Linux x86_64 binary..."
curl -L -o "$BINARIES_DIR/linux/vcontrold" \
  "https://github.com/openv/vcontrold/releases/download/v${VCONTROLD_VERSION}/vcontrold-linux" \
  2>/dev/null || echo "⚠️  Könnte Linux Binary nicht herunterladen"

# Download Linux ARM binary (for Raspberry Pi)
echo "📥 Downloading Linux ARM binary..."
curl -L -o "$BINARIES_DIR/linux/vcontrold-arm" \
  "https://github.com/openv/vcontrold/releases/download/v${VCONTROLD_VERSION}/vcontrold-linux-arm" \
  2>/dev/null || echo "⚠️  Könnte Linux ARM Binary nicht herunterladen"

# Windows Binary (optional)
echo "📥 Attempting to download Windows binary (optional)..."
curl -L -o "$BINARIES_DIR/windows/vcontrold.exe" \
  "https://github.com/openv/vcontrold/releases/download/v${VCONTROLD_VERSION}/vcontrold-win32.exe" \
  2>/dev/null || echo "ℹ️  Windows Binary nicht verfügbar (optional)"

# macOS Binary (optional)
echo "📥 Attempting to download macOS binary (optional)..."
curl -L -o "$BINARIES_DIR/macos/vcontrold" \
  "https://github.com/openv/vcontrold/releases/download/v${VCONTROLD_VERSION}/vcontrold-macos" \
  2>/dev/null || echo "ℹ️  macOS Binary nicht verfügbar (optional)"

# Make binaries executable
echo "🔧 Making binaries executable..."
chmod +x "$BINARIES_DIR/linux/vcontrold" 2>/dev/null || true
chmod +x "$BINARIES_DIR/linux/vcontrold-arm" 2>/dev/null || true
chmod +x "$BINARIES_DIR/macos/vcontrold" 2>/dev/null || true

echo "✅ Binaries ready!"
echo ""
echo "📂 Binaries location:"
ls -lh "$BINARIES_DIR"/*/ 2>/dev/null || echo "   (No binaries downloaded)"
echo ""
echo "💡 Next: Push to GitHub or install in Home Assistant"
