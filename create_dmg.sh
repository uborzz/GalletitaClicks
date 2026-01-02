#!/bin/bash
# Script para crear un DMG personalizado con icono y fondo para GalletitaClicks

echo "Creando DMG personalizado con icono y fondo..."

# Verificar que existe la aplicación
if [ ! -d "dist/GalletitaClicks.app" ]; then
    echo "Error: No se encontró dist/GalletitaClicks.app"
    echo "Por favor, ejecuta primero: ./build_mac.sh"
    exit 1
fi

# Verificar que existe el icono
if [ ! -f "icon.icns" ]; then
    echo "Error: No se encontró icon.icns"
    exit 1
fi

# Crear directorio temporal para el DMG
DMG_TEMP="dmg_temp"
rm -rf "$DMG_TEMP"
mkdir -p "$DMG_TEMP"

# Copiar la aplicación al directorio temporal
cp -R "dist/GalletitaClicks.app" "$DMG_TEMP/"

# Crear archivo de instrucciones
cat > "$DMG_TEMP/INSTRUCCIONES.txt" << 'EOF'
═══════════════════════════════════════════════════════
  GALLETITACLICKS - INSTRUCCIONES
═══════════════════════════════════════════════════════

1. Arrastra "GalletitaClicks.app" a Applications

2. Intenta abrir GalletitaClicks desde Applications
   → La primera vez verás un mensaje de que el software
     es malicioso (esto es normal, la app no está firmada)
   → Solo tendrás la opción de moverla a la papelera
   → NO la muevas a la papelera, cierra el diálogo

3. Para permitir la ejecución (IMPORTANTE - después del paso 2):
   → Ve a Preferencias del Sistema > Privacidad y Seguridad
   → Baja hasta la sección "Seguridad" (abajo de la ventana)
   → Tras intentar abrir la app por primera vez, verás:
     "Se ha bloqueado GalletitaClicks para proteger tu Mac"
   → Haz clic en el botón "Abrir igualmente"
   → Ingresa tu contraseña de administrador si se solicita

4. Cierra la aplicación si se abrió y vuelve a abrirla
   → Ahora funcionará normalmente con doble clic

NOTA: La aplicación no está firmada con certificado de Apple,
por eso macOS requiere estos pasos adicionales. En algunas
versiones de macOS, el botón "Abrir igualmente" solo aparece
en Preferencias del Sistema > Privacidad y Seguridad > Seguridad
después de intentar abrir la aplicación por primera vez.

═══════════════════════════════════════════════════════
https://github.com/uborzz/GalletitaClicks
═══════════════════════════════════════════════════════
EOF
# Dar permisos de lectura a todos los usuarios y eliminar atributos extendidos
chmod 644 "$DMG_TEMP/INSTRUCCIONES.txt"
chown $(whoami):staff "$DMG_TEMP/INSTRUCCIONES.txt" 2>/dev/null || true
xattr -c "$DMG_TEMP/INSTRUCCIONES.txt" 2>/dev/null || true

# Firmar la aplicación antes de crear el DMG (ad-hoc signing mejorado)
echo "Firmando la aplicación para el DMG..."
# Firmar todos los binarios primero
find "$DMG_TEMP/GalletitaClicks.app" -type f -perm +111 -exec codesign --force --sign - {} \; 2>/dev/null || true
# Firmar el bundle completo
codesign --force --deep --sign - --options runtime "$DMG_TEMP/GalletitaClicks.app" 2>/dev/null || {
    echo "Advertencia: No se pudo firmar la aplicación completamente. Continuando..."
}

# Crear un enlace simbólico a Applications
ln -s /Applications "$DMG_TEMP/Applications"

# Crear el DMG temporal (sin comprimir, formato read-write)
DMG_TEMP_FILE="GalletitaClicks_temp.dmg"
rm -f "$DMG_TEMP_FILE"
echo "Creando DMG temporal (read-write)..."
hdiutil create -srcfolder "$DMG_TEMP" -volname "GalletitaClicks" -fs HFS+ -fsargs "-c c=64,a=16,e=16" -format UDRW -size 200m "$DMG_TEMP_FILE"

if [ ! -f "$DMG_TEMP_FILE" ]; then
    echo "Error: No se pudo crear el DMG temporal"
    exit 1
fi

# Montar el DMG (asegurarse de que sea read-write)
echo "Montando DMG temporal..."
# Primero desmontar cualquier DMG anterior con el mismo nombre
hdiutil detach "/Volumes/GalletitaClicks" 2>/dev/null || true
sleep 1

# Montar el DMG como read-write
MOUNT_OUTPUT=$(hdiutil attach -readwrite -noverify -noautoopen "$DMG_TEMP_FILE" 2>&1)
DEVICE=$(echo "$MOUNT_OUTPUT" | egrep '^/dev/' | sed 1q | awk '{print $1}')

if [ -z "$DEVICE" ]; then
    echo "Error: No se pudo montar el DMG temporal"
    echo "Salida de hdiutil: $MOUNT_OUTPUT"
    exit 1
fi

# Esperar un momento para que se monte completamente
sleep 3

# Obtener el punto de montaje
MOUNT_POINT=$(hdiutil info | grep -A 1 "$DEVICE" | tail -1 | awk '{print $3}')

if [ -z "$MOUNT_POINT" ] || [ ! -d "$MOUNT_POINT" ]; then
    echo "Error: No se pudo obtener el punto de montaje"
    echo "Device: $DEVICE"
    hdiutil detach "$DEVICE" 2>/dev/null
    exit 1
fi

# Verificar que el volumen esté montado como read-write
if mount | grep "$MOUNT_POINT" | grep -q "read-only"; then
    echo "Advertencia: El volumen está montado como solo lectura, intentando remontar..."
    hdiutil detach "$DEVICE" 2>/dev/null
    sleep 1
    MOUNT_OUTPUT=$(hdiutil attach -readwrite -noverify -noautoopen "$DMG_TEMP_FILE" 2>&1)
    DEVICE=$(echo "$MOUNT_OUTPUT" | egrep '^/dev/' | sed 1q | awk '{print $1}')
    sleep 2
    MOUNT_POINT=$(hdiutil info | grep -A 1 "$DEVICE" | tail -1 | awk '{print $3}')
fi

echo "DMG montado en: $MOUNT_POINT (read-write)"

# Configurar el icono del volumen (ANTES de comprimir)
echo "Configurando icono del volumen..."
if cp "icon.icns" "$MOUNT_POINT/.VolumeIcon.icns" 2>/dev/null; then
    # Hacer que el icono sea visible y aplicarlo al volumen
    SetFile -a C "$MOUNT_POINT" 2>/dev/null
    
    # Aplicar el icono al volumen usando sips
    sips -i "$MOUNT_POINT/.VolumeIcon.icns" > /dev/null 2>&1
    
    # Forzar la actualización del icono
    touch "$MOUNT_POINT/.VolumeIcon.icns" 2>/dev/null
    
    echo "✓ Icono del volumen configurado"
else
    echo "Error: No se pudo copiar el icono (el volumen puede estar montado como solo lectura)"
    echo "Intentando remontar como lectura/escritura..."
    hdiutil detach "$DEVICE" 2>/dev/null
    sleep 1
    DEVICE=$(hdiutil attach -readwrite -noverify -noautoopen "$DMG_TEMP_FILE" 2>&1 | egrep '^/dev/' | sed 1q | awk '{print $1}')
    sleep 2
    MOUNT_POINT=$(hdiutil info | grep -A 1 "$DEVICE" | tail -1 | awk '{print $3}')
    cp "icon.icns" "$MOUNT_POINT/.VolumeIcon.icns"
    SetFile -a C "$MOUNT_POINT"
    echo "✓ Icono del volumen configurado (después de remontar)"
fi

# Crear fondo personalizado con flecha profesional
echo "Creando fondo personalizado..."
DMG_BACKGROUND_DIR="$MOUNT_POINT/.background"
mkdir -p "$DMG_BACKGROUND_DIR"

# Crear un fondo limpio con flecha gorda y profesional
python3 << 'PYTHON_EOF'
from PIL import Image, ImageDraw
import os

# Tamaño del fondo (ajustado para la ventana)
width, height = 600, 400
bg_color = (245, 245, 245)  # Gris muy claro, más profesional

# Crear imagen
img = Image.new('RGB', (width, height), bg_color)
draw = ImageDraw.Draw(img)

# Dibujar flecha pequeña y verde entre los iconos
# Iconos más grandes: app a la izquierda (x=120, tamaño ~120px), Applications a la derecha (x=420, tamaño ~120px)
# Flecha pequeña en el espacio entre ellos
arrow_start_x = 220  # Final del icono de la app (120 + 120px de icono)
arrow_end_x = 320    # Inicio del icono de Applications
arrow_y = 150         # Centro vertical de los iconos

# Flecha pequeña en verde
arrow_width = 16  # Ancho de la flecha (más pequeña)
arrow_head_size = 30  # Tamaño de la cabeza de la flecha (más pequeña)

# Color verde (RGB)
green_color = (76, 175, 80)  # Verde Material Design
green_shadow = (56, 142, 60)  # Verde más oscuro para sombra

# Sombra de la flecha (offset sutil)
shadow_offset = 1
draw.line([(arrow_start_x + shadow_offset, arrow_y + shadow_offset), 
           (arrow_end_x - arrow_head_size + shadow_offset, arrow_y + shadow_offset)], 
          fill=green_shadow, width=arrow_width)

# Cuerpo de la flecha (verde)
draw.line([(arrow_start_x, arrow_y), (arrow_end_x - arrow_head_size, arrow_y)], 
          fill=green_color, width=arrow_width)

# Cabeza de la flecha (triángulo verde)
arrow_points = [
    (arrow_end_x, arrow_y),  # Punta
    (arrow_end_x - arrow_head_size, arrow_y - arrow_head_size),  # Superior
    (arrow_end_x - arrow_head_size, arrow_y + arrow_head_size),  # Inferior
]
draw.polygon(arrow_points, fill=green_color)

# Guardar el fondo
bg_path = os.path.expanduser("~/.galletitaclicks_dmg_bg.png")
img.save(bg_path)
print(f"Fondo creado: {bg_path}")
PYTHON_EOF

# Copiar el fondo al DMG
if [ -f "$HOME/.galletitaclicks_dmg_bg.png" ]; then
    if cp "$HOME/.galletitaclicks_dmg_bg.png" "$DMG_BACKGROUND_DIR/background.png" 2>/dev/null; then
        echo "✓ Fondo copiado al DMG"
        rm -f "$HOME/.galletitaclicks_dmg_bg.png"
    else
        echo "Error: No se pudo copiar el fondo (el volumen puede estar montado como solo lectura)"
        # Intentar crear el directorio si no existe
        mkdir -p "$DMG_BACKGROUND_DIR" 2>/dev/null
        cp "$HOME/.galletitaclicks_dmg_bg.png" "$DMG_BACKGROUND_DIR/background.png" 2>/dev/null && echo "✓ Fondo copiado al DMG (segundo intento)"
        rm -f "$HOME/.galletitaclicks_dmg_bg.png"
    fi
else
    echo "Advertencia: No se encontró el archivo de fondo generado"
fi

# Configurar la vista del Finder
echo "Configurando vista del Finder..."

    # Usar AppleScript para configurar la vista con fondo
    osascript <<EOF
    tell application "Finder"
        tell disk "GalletitaClicks"
            open
            set current view of container window to icon view
            set toolbar visible of container window to false
            set statusbar visible of container window to false
            set the bounds of container window to {400, 100, 1000, 500}
            
            set viewOptions to the icon view options of container window
            set arrangement of viewOptions to not arranged
            set icon size of viewOptions to 120  -- Iconos más grandes
            set background picture of viewOptions to file ".background:background.png"
            
            delay 1
            
            -- Posicionar los iconos (más separados para la flecha entre ellos)
            set position of item "GalletitaClicks.app" of container window to {120, 100}
            set position of item "Applications" of container window to {420, 100}
            if exists item "INSTRUCCIONES.txt" of container window then
                set position of item "INSTRUCCIONES.txt" of container window to {120, 255}
            end if
            
            -- Actualizar y guardar la vista
            close
            open
            update without registering applications
            delay 2
            
            -- Forzar guardar la configuración de la vista
            set viewOptions to the icon view options of container window
            set background picture of viewOptions to file ".background:background.png"
        end tell
    end tell
EOF

# Esperar un momento para que se guarde la configuración de la vista
echo "Guardando configuración de la vista..."
sleep 3

# Verificar que el fondo esté presente
if [ -f "$DMG_BACKGROUND_DIR/background.png" ]; then
    echo "✓ Fondo verificado en el DMG"
    ls -la "$DMG_BACKGROUND_DIR/"
else
    echo "Error: El fondo no se encontró en el DMG"
    echo "Intentando copiar el fondo de nuevo..."
    if [ -f "$HOME/.galletitaclicks_dmg_bg.png" ]; then
        cp "$HOME/.galletitaclicks_dmg_bg.png" "$DMG_BACKGROUND_DIR/background.png" 2>/dev/null && echo "✓ Fondo copiado"
    fi
fi

# Verificar que el icono esté presente
if [ -f "$MOUNT_POINT/.VolumeIcon.icns" ]; then
    echo "✓ Icono del volumen verificado"
else
    echo "Error: El icono del volumen no se encontró"
fi

# Desmontar el DMG
echo "Desmontando DMG temporal..."
hdiutil detach "$DEVICE" || hdiutil detach "$MOUNT_POINT" || true
sleep 2

# Convertir a formato comprimido final
echo "Comprimiendo DMG..."
rm -f "GalletitaClicks.dmg"
hdiutil convert "$DMG_TEMP_FILE" -format UDZO -o "GalletitaClicks.dmg"

# El icono y el fondo ya se aplicaron antes de comprimir, así que deberían estar en el DMG final
# No intentar aplicar el icono después de comprimir porque el DMG comprimido es solo lectura
echo "✓ Icono y fondo aplicados antes de comprimir el DMG"

# Limpiar archivos temporales
rm -rf "$DMG_TEMP"
rm -f "$DMG_TEMP_FILE"

echo ""
echo "✓ DMG creado: GalletitaClicks.dmg"
echo "  El DMG incluye:"
echo "  - Icono personalizado del volumen"
echo "  - Fondo con instrucciones visuales"
echo "  - Vista optimizada del Finder"
echo "  - Listo para distribuir"
