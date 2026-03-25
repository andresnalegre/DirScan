#!/bin/bash
set -e

APP_NAME="DirScan"
APP_DIR="dist/${APP_NAME}"
APPIMAGE_PATH="dist/${APP_NAME}.AppImage"
TEMP_DIR="./.appimage_temp"

echo "========================================"
echo "Building AppImage for $APP_NAME..."
echo "========================================"

# 0️⃣ Validate app exists
if [ ! -d "$APP_DIR" ]; then
  echo "❌ ERROR: $APP_DIR not found. Build the app first."
  exit 1
fi

# 1️⃣ Check dependencies
if ! command -v appimagetool &> /dev/null; then
  echo "⚠️ appimagetool not found. Downloading..."
  wget -q https://github.com/AppImage/AppImageKit/releases/latest/download/appimagetool-x86_64.AppImage -O appimagetool
  chmod +x appimagetool
  APPIMAGETOOL="./appimagetool"
else
  APPIMAGETOOL="appimagetool"
fi

# 2️⃣ Clean temp dir
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR/$APP_NAME.AppDir"

APPDIR="$TEMP_DIR/$APP_NAME.AppDir"

# 3️⃣ Copy app files
cp -R "$APP_DIR"/* "$APPDIR/"

# 4️⃣ Create AppRun (entrypoint)
cat > "$APPDIR/AppRun" <<EOF
#!/bin/bash
HERE=\$(dirname "\$(readlink -f "\${0}")")
exec "\$HERE/$APP_NAME" "\$@"
EOF

chmod +x "$APPDIR/AppRun"

# 5️⃣ Create desktop file
cat > "$APPDIR/$APP_NAME.desktop" <<EOF
[Desktop Entry]
Name=$APP_NAME
Exec=$APP_NAME
Icon=$APP_NAME
Type=Application
Categories=Utility;
EOF

# 6️⃣ Add icon (if exists)
if [ -f "$APP_DIR/$APP_NAME.png" ]; then
  cp "$APP_DIR/$APP_NAME.png" "$APPDIR/"
else
  echo "⚠️ Icon not found, skipping..."
fi

# 7️⃣ Remove old AppImage
rm -f "$APPIMAGE_PATH"

echo "📦 Creating AppImage..."

# 8️⃣ Build AppImage
$APPIMAGETOOL "$APPDIR" "$APPIMAGE_PATH"

# 9️⃣ Cleanup
rm -rf "$TEMP_DIR"

echo "========================================"
echo "🎉 DONE: $APPIMAGE_PATH"
echo "========================================"