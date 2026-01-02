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

La primera vez que ejecutes la aplicación, macOS te pedirá permisos de accesibilidad:

1. Ve a **Preferencias del Sistema** > **Seguridad y Privacidad** > **Privacidad** > **Accesibilidad**
2. Marca la casilla junto a **GalletitaClicks**
3. Reinicia la aplicación

## Uso

1. Abre **GalletitaClicks** desde Applications
2. Configura el tiempo entre clicks (en segundos)
3. Opcionalmente activa:
   - **Intervalo aleatorio**: Los clicks ocurrirán en un tiempo aleatorio entre el mínimo y máximo
   - **Clicks en posición aleatoria**: Los clicks ocurrirán dentro de un círculo alrededor del cursor
   - **Movimientos sexy**: El cursor se moverá suavemente entre clicks
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
