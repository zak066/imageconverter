#!/bin/bash
# Build script per ImageConverter

cd "$(dirname "$0")"

echo "=== Build ImageConverter ==="

# Attiva virtual environment se esiste
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Installa dipendenze
echo "Installo dipendenze..."
pip install -r requirements.txt pyinstaller

# Pulisci build precedenti
echo "Pulisco build..."
rm -rf build dist

# Build eseguibile
echo "Compilo eseguibile..."
pyinstaller --onefile \
    --name "ImageConverter" \
    --add-data "version.py:." \
    --add-data "config.py:." \
    --add-data "gui.py:." \
    --add-data "converter.py:." \
    --hidden-import "PIL._tkinter_finder" \
    --hidden-import "tkinterdnd2" \
    --hidden-import "pillow_avif_plugin" \
    main.py

echo ""
echo "=== Build completato! ==="
echo "Eseguibile: dist/ImageConverter"
ls -lh dist/ImageConverter