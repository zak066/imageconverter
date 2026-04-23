# Build script for ImageConverter (Windows PowerShell)

Write-Host "=== Build ImageConverter ===" -ForegroundColor Cyan

# Install dependencies if needed
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt pyinstaller

# Clean previous build
Write-Host "Cleaning build..." -ForegroundColor Yellow
if (Test-Path build) { Remove-Item -Recurse -Force build }
if (Test-Path dist) { Remove-Item -Recurse -Force dist }

# Build
Write-Host "Building executable..." -ForegroundColor Yellow
pyinstaller --onefile `
    --name "ImageConverter" `
    --add-data "version.py;." `
    --add-data "config.py;." `
    --add-data "gui.py;." `
    --add-data "converter.py;." `
    --hidden-import "PIL._tkinter_finder" `
    --hidden-import "tkinterdnd2" `
    --hidden-import "pillow_avif_plugin" `
    main.py

Write-Host ""
Write-Host "=== Build complete! ===" -ForegroundColor Green
Write-Host "Executable: dist\ImageConverter.exe" -ForegroundColor Green
Get-Item dist\ImageConverter.exe | Select-Object Name, @{N='Size(MB)';E={[math]::Round($_.Length/1MB,2)}} | Format-Table