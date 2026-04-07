<div align="center">
  <img src="dirscan/assets/logo.png" alt="DirScan" width="120" />

  # DirScan

  A desktop directory mapper built with Python and PyQt5, available for macOS.

  ![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
  ![PyQt5](https://img.shields.io/badge/PyQt5-5.15-green?logo=qt)
  ![Platform](https://img.shields.io/badge/Platform-macOS-black?logo=apple)
  
  [![Download DMG](https://img.shields.io/badge/Download-DMG-blue?style=flat-square)](https://github.com/andresnalegre/DirScan/releases)
  [![GitHub](https://img.shields.io/badge/Made%20by-Andres%20Nicolas%20Alegre-brightgreen?style=flat-square)](https://github.com/andresnalegre)
</div>

---

## About

**DirScan** is a desktop app that scans any folder and generates a visual tree of its structure. You can filter out temporary files and save the result as a `.txt` file.

## Features

- Visual directory tree with icons
- Filter temporary files (node_modules, .git, venv, __pycache__, etc.)
- Save map to `.txt`
- Progress bar with live status
- macOS DMG available

---

## Installation (macOS)

### 1. Download
Download `DirScan.dmg` from the [Releases](https://github.com/andresnalegre/DirScan/releases) page.

### 2. Install
Open the DMG and drag DirScan.app to your Applications folder.

### 3. First Launch
macOS will block the app on first launch because it's not signed. Run this once in Terminal:

```bash
xattr -cr /Applications/DirScan.app
```

Then open DirScan from Applications or Launchpad normally.

---

## Run locally

### Requirements
- Python 3.10+

### Setup

```bash
git clone https://github.com/andresnalegre/DirScan.git
cd DirScan
pip install -r requirements.txt
python main.py
```

---

## Build DMG

```bash
pyinstaller --windowed --name "DirScan" \
  --icon dirscan/assets/logo.icns \
  --add-data "dirscan/assets:dirscan/assets" \
  main.py

mkdir -p dmg_staging
cp -r dist/DirScan.app dmg_staging/

create-dmg \
  --volname "DirScan" \
  --volicon "dirscan/assets/logo.icns" \
  --window-pos 200 120 \
  --window-size 600 400 \
  --icon-size 100 \
  --icon "DirScan.app" 175 190 \
  --hide-extension "DirScan.app" \
  --app-drop-link 425 190 \
  "DirScan.dmg" \
  "dmg_staging"

rm -rf dmg_staging
```

Output: `DirScan.dmg`

---

## Tech stack

| Layer     | Technology     |
|-----------|----------------|
| Language  | Python 3.12    |
| UI        | PyQt5 5.15     |
| Platform  | macOS          |

---

## License

This project is licensed under the [MIT License](LICENSE).

## Contributing

Contributions are welcome! Feel free to fork the repository and submit a pull request. Please ensure your code follows the existing style and structure.
