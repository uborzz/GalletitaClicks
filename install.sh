#!/bin/bash
# Script de instalación que elimina la cuarentena de Gatekeeper

APP_PATH="/Applications/GalletitaClicks.app"

if [ ! -d "$APP_PATH" ]; then
    echo "Error: No se encontró GalletitaClicks.app en /Applications"
    echo "Por favor, arrastra la aplicación a la carpeta Applications primero."
    exit 1
fi

echo "Eliminando cuarentena de Gatekeeper..."
xattr -d com.apple.quarantine "$APP_PATH" 2>/dev/null || {
    echo "Advertencia: No se pudo eliminar la cuarentena automáticamente."
    echo "Puedes hacerlo manualmente ejecutando:"
    echo "  xattr -d com.apple.quarantine /Applications/GalletitaClicks.app"
}

echo "✓ Instalación completada"
echo ""
echo "Ahora puedes abrir GalletitaClicks desde Applications sin problemas."

