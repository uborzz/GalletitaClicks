#!/bin/bash
# Script para abrir GalletitaClicks la primera vez eliminando la cuarentena

APP_PATH="/Applications/GalletitaClicks.app"

if [ ! -d "$APP_PATH" ]; then
    echo "❌ No se encontró GalletitaClicks.app en /Applications"
    echo ""
    echo "Por favor:"
    echo "1. Arrastra GalletitaClicks.app desde el DMG a la carpeta Applications"
    echo "2. Luego ejecuta este script de nuevo"
    exit 1
fi

echo "🔓 Eliminando cuarentena de Gatekeeper..."
xattr -cr "$APP_PATH" 2>/dev/null || {
    echo "⚠️  No se pudo eliminar automáticamente."
    echo "Ejecuta manualmente: xattr -cr /Applications/GalletitaClicks.app"
    exit 1
}

echo "✅ Cuarentena eliminada"
echo ""
echo "🚀 Abriendo GalletitaClicks..."
open "$APP_PATH"

echo ""
echo "✅ ¡Listo! La aplicación debería abrirse sin problemas."
echo "   A partir de ahora puedes abrirla normalmente con doble clic."

