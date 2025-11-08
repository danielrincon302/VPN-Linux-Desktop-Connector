![VPN Linux Desktop Connector](img/header.png)

# VPN Linux Desktop Connector

Una aplicación de escritorio moderna para gestionar conexiones VPN en Linux usando OpenVPN con interfaz gráfica GTK3.

## Autores

Urreste García, L. A., Capote Casas, F. E., Castellanos Muriel, J. A., & Rincón Brito, C. D. (2025). VPN Linux Desktop Connector (v1.0.0) [Software]. Zenodo. https://doi.org/10.5281/zenodo.10293847

## Características

- ✅ Interfaz gráfica intuitiva con GTK3
- ✅ **Íconos personalizados** en ventana y bandeja del sistema
- ✅ Soporte para múltiples idiomas (Español 🇨🇴, Inglés 🇬🇧, Chino 🇨🇳, Portugués 🇧🇷, Francés 🇫🇷, Alemán 🇩🇪, Japonés 🇯🇵)
- ✅ 4 temas visuales (Gerencial, Minimalista, Moderno, Sistema Solar)
- ✅ Almacenamiento seguro de credenciales (encriptación)
- ✅ Logs en tiempo real de conexión
- ✅ **Ícono de bandeja del sistema** con menú contextual
- ✅ Información de red en tiempo real:
  - Estado de conexión VPN
  - IP del túnel VPN
  - IP local
  - IP pública
  - Tipo de conexión (WiFi/Ethernet)

## Instalación Rápida

### Opción 1: Script Automático (Recomendado)

```bash
sudo ./instalar_dependencias.sh
```

### Opción 2: Instalación Manual

#### Dependencias del Sistema (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install -y \
    python3-gi \
    python3-gi-cairo \
    gir1.2-gtk-3.0 \
    openvpn \
    network-manager
```

**Nota**: Esta aplicación **NO requiere permisos de root** para ejecutarse (solo para la instalación de dependencias). El ícono de bandeja usa `Gtk.StatusIcon` que viene incluido con GTK3.

#### Dependencias de Python

```bash
pip3 install -r requirements.txt
```

O manualmente:

```bash
pip3 install cryptography requests
```

## Uso

### Iniciar la aplicación

```bash
python3 VPN-Desktop-Linux-Conector.py
```

### Configuración Inicial

1. Selecciona tu archivo OVPN (proporcionado por tu administrador)
2. Ingresa tu usuario y contraseña
3. Las credenciales se guardarán de forma segura y encriptada
4. Haz clic en "Conectar VPN"

### Cambiar Idioma

1. Ve a Menú → Configuración → Lenguaje
2. Selecciona el idioma deseado
3. La interfaz se actualizará automáticamente

### Cambiar Tema

1. Ve a Menú → Configuración → Temas
2. Selecciona entre:
   - **Gerencial**: Estilo corporativo con azules y blancos
   - **Minimalista**: Diseño limpio y simple
   - **Moderno**: Tema moderno con gradientes vibrantes
   - **Sistema Solar**: Tema oscuro inspirado en el espacio con colores del sistema solar

## Indicador de Bandeja del Sistema

La aplicación incluye un **ícono de bandeja del sistema** que aparece automáticamente en la barra de tareas:

- **Minimizar a bandeja**: Al cerrar la ventana, la aplicación se minimiza en lugar de cerrarse
- **Clic izquierdo**: Alterna mostrar/ocultar ventana principal
- **Clic derecho**: Abre menú contextual con:
  - Abrir/Restaurar ventana
  - Ver estado de conexión (Conectado ✓ / Desconectado)
  - Ver IP VPN
  - Ver IP Local
  - Ver IP Pública
  - Ver tipo de conexión (WiFi con nombre / Ethernet)
  - Salir de la aplicación

El ícono cambia automáticamente según el estado de la conexión VPN.

### Ventajas del Ícono de Bandeja

- ✅ **Sin dependencias adicionales**: Usa `Gtk.StatusIcon` incluido en GTK3
- ✅ **Sin permisos de root**: Funciona para cualquier usuario
- ✅ **Universal**: Compatible con todos los entornos de escritorio GTK3
- ✅ **Actualización automática**: Información en tiempo real cada 5 segundos

## Dependencias Opcionales

### requests (Python)

El módulo requests es necesario para obtener la IP pública. Si no está instalado:
- La aplicación funcionará normalmente
- La IP pública mostrará "No disponible (instalar requests)"

Para instalar:
```bash
pip3 install requests
```

## Estructura del Proyecto

```
VPN-Desktop-Linux-Connector/
├── VPN-Desktop-Linux-Conector.py    # Aplicación principal
├── requirements.txt                  # Dependencias de Python
├── instalar_dependencias.sh         # Script de instalación
├── INSTALL_DEPENDENCIES.md          # Documentación de dependencias
├── IMPLEMENTACION_ICONOS.md         # Guía de íconos implementados
├── README.md                        # Este archivo
├── icons/                           # Íconos de la aplicación
│   ├── VPN-LDC_16x16.svg           # Ícono 16x16 (reservado)
│   ├── VPN-LDC_22x22.svg           # Ícono 22x22 (reservado)
│   ├── VPN-LDC_24x24.svg           # ⭐ Bandeja del sistema
│   ├── VPN-LDC_32x32.svg           # ⭐ Ventana principal y About
│   └── README_ICONS.md             # Documentación de íconos
├── config.txt                       # Credenciales (generado automáticamente)
├── idioma.txt                       # Idioma seleccionado
├── tema.txt                         # Tema seleccionado
└── .vpn_key                         # Clave de encriptación (oculto)
```

## Íconos Personalizados

La aplicación usa íconos personalizados en formato SVG:

- **Ventana principal**: Muestra el ícono `VPN-LDC_32x32.svg` en la barra de título
- **Bandeja del sistema**: Usa `VPN-LDC_24x24.svg` para el ícono de la bandeja
- **Diálogo About**: Logo escalado a 128x128 píxeles
- **Título**: "VPN Linux Desktop Connector" visible en la barra de título

Ver `icons/README_ICONS.md` para más detalles sobre la implementación.

## Seguridad

- Las contraseñas se almacenan **encriptadas** usando Fernet (criptografía simétrica)
- Los archivos de configuración tienen permisos restrictivos (600)
- La clave de encriptación es única por usuario y máquina
- No se almacenan contraseñas en texto plano

## Solución de Problemas

### El ícono de bandeja no aparece

**Causas posibles**:
- El entorno de escritorio no soporta bandejas del sistema (algunos entornos modernos las han eliminado)
- Extensiones del sistema que bloquean íconos de bandeja

**Solución**: La ventana principal funciona normalmente. Puedes minimizarla manualmente o configurar tu entorno de escritorio para mostrar íconos de bandeja.

### Error de autenticación

Verifica:
- Usuario y contraseña correctos
- Archivo OVPN válido
- Conexión a internet activa

### No se puede conectar

Asegúrate de tener permisos de sudo para ejecutar OpenVPN:
```bash
sudo openvpn --version
```

### La IP pública no se muestra

Instala el módulo requests:
```bash
pip3 install requests
```

## Licencia

GPL 3.0

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o pull request.

## Soporte

Para reportar problemas o solicitar características:
- Abre un issue en GitHub
- Incluye los logs de la aplicación
- Especifica tu versión de Ubuntu/Debian
- Indica la versión de OpenVPN instalada

---

**Desarrollado con ❤️ para la comunidad Linux**
