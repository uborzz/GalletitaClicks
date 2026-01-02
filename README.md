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

1. Descarga el archivo `GalletitaClicks.dmg` desde la sección [Releases](https://github.com/TU_USUARIO/galletitaclicks/releases)
2. Abre el archivo `.dmg` descargado
3. Arrastra `GalletitaClicks.app` a la carpeta Applications
4. Abre la aplicación desde Applications

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

[Especifica tu licencia aquí]

## Autor

[Tu nombre/información]
