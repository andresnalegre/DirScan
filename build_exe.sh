#!/bin/bash

APP_NAME="DirScan"
MAIN_SCRIPT="main.py"
DIST_DIR="dist"
BUILD_DIR="build"
ICON_PATH="dirscan/assets/logo.ico"
EXE_NAME="${APP_NAME}.exe"

echo "========================================"
echo "Building Windows EXE for ${APP_NAME}..."
echo "========================================"

# Verifica se PyInstaller está instalado
if ! command -v pyinstaller &> /dev/null
then
    echo "PyInstaller not found. Install with: pip install pyinstaller"
    exit 1
fi

# Remove builds antigos
echo "Cleaning previous builds..."
rm -rf "$DIST_DIR" "$BUILD_DIR" "${APP_NAME}.spec"

# Rodar PyInstaller
pyinstaller \
    --onefile \
    --windowed \
    --name "$APP_NAME" \
    --icon="$ICON_PATH" \
    --add-data "dirscan/assets:dirscan/assets" \
    "$MAIN_SCRIPT"

# Verifica se gerou o EXE corretamente
EXE_PATH="${DIST_DIR}/${EXE_NAME}"
if [ -f "$EXE_PATH" ]; then
    echo "========================================"
    echo "SUCCESS: EXE generated at $EXE_PATH"
    echo "========================================"
else
    echo "ERROR: EXE not created. Check PyInstaller output above."
    exit 1
fi