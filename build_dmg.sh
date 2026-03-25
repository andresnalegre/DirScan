#!/bin/bash
set -e

APP_NAME="DirScan"
APP_BUNDLE="dist/${APP_NAME}.app"
DMG_PATH="dist/${APP_NAME}.dmg"
TEMP_DIR="./.dmg_temp"

echo "========================================"
echo "Building professional DMG for $APP_NAME..."
echo "========================================"

# 0️⃣ Validate app exists
if [ ! -d "$APP_BUNDLE" ]; then
  echo "❌ ERROR: $APP_BUNDLE not found. Build the app first."
  exit 1
fi

# 1️⃣ Clean temp dir (stable path avoids macOS permission bugs)
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"

# 2️⃣ Copy app
cp -R "$APP_BUNDLE" "$TEMP_DIR/"

# 3️⃣ Remove old DMG if exists
rm -f "$DMG_PATH"

echo "📦 Creating DMG..."

# 4️⃣ Try full featured DMG (with layout)
if create-dmg \
  --volname "$APP_NAME" \
  --window-size 640 240 \
  --icon-size 128 \
  --icon "$APP_NAME" 160 80 \
  --app-drop-link 480 80 \
  --no-internet-enable \
  --hide-extension "$APP_NAME" \
  "$DMG_PATH" \
  "$TEMP_DIR"; then

  echo "✅ DMG created with styled layout"

else
  echo "⚠️ AppleScript failed. Retrying without layout..."

  # fallback (no Finder automation, always works)
  hdiutil create -volname "$APP_NAME" \
    -srcfolder "$TEMP_DIR" \
    -ov -format UDZO "$DMG_PATH"

  echo "✅ DMG created (basic layout)"
fi

# 5️⃣ Cleanup
rm -rf "$TEMP_DIR"

echo "========================================"
echo "🎉 DONE: $DMG_PATH"
echo "========================================"