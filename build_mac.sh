#!/bin/bash
# Script para empaquetar GalletitaClicks para Mac (Intel y ARM)

echo "Construyendo GalletitaClicks para Mac..."

# Verificar que PyInstaller está instalado
if ! command -v pyinstaller &> /dev/null; then
    echo "Instalando PyInstaller..."
    pip install pyinstaller
fi

# Limpiar builds anteriores
rm -rf build dist

# Verificar que existe el archivo .spec
if [ ! -f "galletitaclicks.spec" ]; then
    echo "Error: No se encontró el archivo galletitaclicks.spec"
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

# Crear el ejecutable usando el archivo .spec
echo "Usando archivo galletitaclicks.spec..."
pyinstaller galletitaclicks.spec

# Firmar la aplicación con identidad ad-hoc (evita algunos problemas de Gatekeeper)
if [ -d "dist/GalletitaClicks.app" ]; then
    echo ""
    echo "Firmando la aplicación..."
    codesign --force --deep --sign - dist/GalletitaClicks.app 2>/dev/null || {
        echo "Advertencia: No se pudo firmar la aplicación. Esto es normal si no tienes un certificado de desarrollador."
        echo "La aplicación funcionará, pero macOS puede mostrar una advertencia la primera vez."
    }
    echo "✓ Aplicación firmada"
fi

echo ""
echo "¡Build completado! El ejecutable está en la carpeta 'dist/GalletitaClicks.app'"
echo ""
echo "Para instalar, simplemente arrastra 'dist/GalletitaClicks.app' a la carpeta Applications"
echo ""
echo "Para crear un instalador .dmg con icono personalizado, ejecuta:"
echo "  ./create_dmg.sh"
echo ""
echo "NOTA: Después de la primera ejecución, necesitarás dar permisos de accesibilidad"
echo "en Preferencias del Sistema > Seguridad y Privacidad > Privacidad > Accesibilidad"

