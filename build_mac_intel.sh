#!/bin/bash
# Script para empaquetar GalletitaClicks para Mac Intel (x86_64)

echo "Construyendo GalletitaClicks para Mac Intel..."

# Verificar que PyInstaller está instalado
if ! command -v pyinstaller &> /dev/null; then
    echo "Instalando PyInstaller..."
    pip install pyinstaller
fi

# Limpiar builds anteriores
rm -rf build dist

# Verificar que existe el archivo .spec
if [ ! -f "galletitaclicks_intel.spec" ]; then
    echo "Error: No se encontró el archivo galletitaclicks_intel.spec"
    exit 1
fi

# Verificar que existe el icono
if [ ! -f "icon.icns" ]; then
    echo "Advertencia: No se encontró el archivo icon.icns"
    echo "Intentando crear icon.icns desde icon.png..."
    if [ -f "icon.png" ]; then
        mkdir -p icon.iconset
        sips -z 16 16 icon.png --out icon.iconset/icon_16x16.png
        sips -z 32 32 icon.png --out icon.iconset/icon_16x16@2x.png
        sips -z 32 32 icon.png --out icon.iconset/icon_32x32.png
        sips -z 64 64 icon.png --out icon.iconset/icon_32x32@2x.png
        sips -z 128 128 icon.png --out icon.iconset/icon_128x128.png
        sips -z 256 256 icon.png --out icon.iconset/icon_128x128@2x.png
        sips -z 256 256 icon.png --out icon.iconset/icon_256x256.png
        sips -z 512 512 icon.png --out icon.iconset/icon_256x256@2x.png
        sips -z 512 512 icon.png --out icon.iconset/icon_512x512.png
        sips -z 1024 1024 icon.png --out icon.iconset/icon_512x512@2x.png
        iconutil -c icns icon.iconset -o icon.icns
        rm -rf icon.iconset
        echo "✓ Icono .icns creado desde icon.png"
    else
        echo "Error: No se encontró icon.png. La aplicación se creará sin icono personalizado."
    fi
fi

# Crear el ejecutable usando el archivo .spec para Intel
# Usar Rosetta 2 (arch -x86_64) para generar binario Intel desde Mac ARM
echo "Usando archivo galletitaclicks_intel.spec (Intel x86_64)..."
echo "Ejecutando PyInstaller bajo Rosetta 2 para generar binario Intel..."

# Usar venv si existe, sino el Python del sistema
if [ -d "venv" ] && [ -f "venv/bin/pyinstaller" ]; then
    PYTHON_CMD="venv/bin/python3"
    echo "Usando Python del venv bajo Rosetta 2: $PYTHON_CMD"
    arch -x86_64 "$PYTHON_CMD" -m PyInstaller galletitaclicks_intel.spec
elif [ -d "venv" ]; then
    PYTHON_CMD="venv/bin/python3"
    echo "Usando Python del venv bajo Rosetta 2: $PYTHON_CMD"
    arch -x86_64 "$PYTHON_CMD" -m PyInstaller galletitaclicks_intel.spec
elif command -v pyinstaller &> /dev/null; then
    echo "Usando pyinstaller del sistema bajo Rosetta 2"
    arch -x86_64 pyinstaller galletitaclicks_intel.spec
elif command -v python3 &> /dev/null; then
    PYTHON_CMD=$(which python3)
    echo "Usando Python del sistema bajo Rosetta 2: $PYTHON_CMD"
    arch -x86_64 "$PYTHON_CMD" -m PyInstaller galletitaclicks_intel.spec
else
    echo "Error: No se encontró python3 ni pyinstaller"
    exit 1
fi

# Firmar la aplicación con identidad ad-hoc (evita algunos problemas de Gatekeeper)
if [ -d "dist/GalletitaClicks.app" ]; then
    echo ""
    echo "Firmando la aplicación y todos sus componentes..."
    
    # Limpiar atributos de cuarentena
    echo "Limpiando atributos de cuarentena..."
    xattr -cr dist/GalletitaClicks.app 2>/dev/null || true
    
    # Firmar la aplicación de forma simple (como antes)
    echo "Firmando la aplicación..."
    codesign --force --deep --sign - dist/GalletitaClicks.app 2>/dev/null || {
        echo "Advertencia: No se pudo firmar la aplicación completamente."
    }
fi

echo ""
echo "¡Build completado para Intel! El ejecutable está en la carpeta 'dist/GalletitaClicks.app'"
echo ""
echo "Para crear un instalador .dmg para Intel, ejecuta:"
echo "  ./create_dmg_intel.sh"
echo ""
echo "NOTA: Después de la primera ejecución, necesitarás dar permisos de accesibilidad"
echo "en Preferencias del Sistema > Seguridad y Privacidad > Privacidad > Accesibilidad"

