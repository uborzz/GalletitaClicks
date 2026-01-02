# GalletitaClicks

Auto-clicker para macOS con interfaz gráfica intuitiva.

## Características

- ✅ Clicks automáticos configurables
- ✅ Intervalos aleatorios entre clicks
- ✅ Clicks en posición aleatoria dentro de un radio configurable
- ✅ Movimientos suaves del cursor
- ✅ Pausa automática al mover el mouse
- ✅ Interfaz gráfica moderna y fácil de usar

## Instalación

1. Descarga el archivo `GalletitaClicks.dmg` desde la sección [Releases](https://github.com/uborzz/galletitaclicks/releases)
2. Abre el archivo `.dmg` descargado
3. Arrastra `GalletitaClicks.app` a la carpeta Applications

### Si aparece un mensaje de seguridad al abrir:

**Primera vez (solo una vez):** 
- Haz clic derecho (o Control+clic) en `GalletitaClicks.app` en Applications
- Selecciona **"Abrir"**
- macOS te preguntará si estás seguro, haz clic en **"Abrir"**

**Después de esto:** Ya podrás abrir la aplicación normalmente con **doble clic** como cualquier otra app. macOS la recordará como segura.

**Alternativa (si prefieres usar Terminal):**
```bash
xattr -d com.apple.quarantine /Applications/GalletitaClicks.app
```

Después de cualquiera de estas opciones, la aplicación funcionará normalmente con doble clic.

## Permisos requeridos

**Importante:** La aplicación debe ejecutarse desde el archivo `.app` empaquetado, no desde la terminal.

Cuando ejecutes `GalletitaClicks.app` (no `python galletitaclicks.py`), macOS mostrará el icono de la aplicación en las Preferencias del Sistema y pedirá permisos específicamente para **GalletitaClicks**, no para iTerm o Python.

1. Ejecuta la aplicación desde Applications o desde el DMG
2. La primera vez, aparecerá un diálogo pidiendo permisos de accesibilidad
3. Ve a **Preferencias del Sistema** > **Seguridad y Privacidad** > **Privacidad** > **Accesibilidad**
4. Verás **GalletitaClicks** con su icono en la lista
5. Marca la casilla junto a **GalletitaClicks**
6. Reinicia la aplicación

## Uso

1. Abre **GalletitaClicks** desde Applications
2. Configura el tiempo entre clicks (en segundos)
3. Opcionalmente activa:
   - **Intervalo aleatorio**: Los clicks ocurrirán en un tiempo aleatorio entre el mínimo y máximo
   - **Clicks en posición aleatoria**: Los clicks ocurrirán dentro de un círculo alrededor del cursor
   - **Movimiento sexy**: El cursor se moverá suavemente entre clicks
4. Haz clic en **Start** para comenzar
5. Haz clic en **Stop** para detener

## Requisitos

- macOS 10.13 o superior
- Permisos de accesibilidad (se solicitan automáticamente)

## Desarrollo

### Construir la aplicación

```bash
./build_mac.sh
```

### Crear DMG

```bash
./create_dmg.sh
```

## Licencia

-

## Autor

uborZz
