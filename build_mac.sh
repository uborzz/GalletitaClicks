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
    echo "Firmando la aplicación y todos sus componentes..."
    
    # Eliminar atributos de cuarentena y atributos extendidos
    echo "Limpiando atributos de cuarentena..."
    xattr -cr dist/GalletitaClicks.app 2>/dev/null || true
    
    # Asegurar permisos de ejecución
    echo "Ajustando permisos de ejecución..."
    find dist/GalletitaClicks.app -type f -perm +111 -exec chmod 755 {} \; 2>/dev/null || true
    chmod 755 dist/GalletitaClicks.app/Contents/MacOS/GalletitaClicks 2>/dev/null || true
    
    # Eliminar firmas anteriores si existen
    codesign --remove-signature dist/GalletitaClicks.app 2>/dev/null || true
    
    # Primero firmar todos los binarios dentro del .app (en orden correcto)
    find dist/GalletitaClicks.app/Contents -type f \( -name "*.so" -o -name "*.dylib" -o -perm +111 \) -exec codesign --force --sign - --timestamp=none {} \; 2>/dev/null || true
    
    # Luego firmar el bundle completo con opciones runtime
    codesign --force --deep --sign - --timestamp=none --options runtime dist/GalletitaClicks.app 2>/dev/null || {
        echo "Advertencia: No se pudo firmar la aplicación completamente."
    }
    
    # Verificar la firma
    codesign --verify --verbose=1 dist/GalletitaClicks.app 2>/dev/null && echo "✓ Aplicación firmada y verificada" || echo "⚠ Firma no verificada (normal sin certificado de desarrollador)"
    
    # Verificar que no hay atributos de cuarentena
    if xattr -l dist/GalletitaClicks.app 2>/dev/null | grep -q "com.apple.quarantine"; then
        echo "Advertencia: Se detectaron atributos de cuarentena, eliminándolos..."
        xattr -rd com.apple.quarantine dist/GalletitaClicks.app 2>/dev/null || true
    else
        echo "✓ Sin atributos de cuarentena"
    fi
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

