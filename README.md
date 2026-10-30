# Imágenes GPT

Aplicación **local para Windows** que genera y edita imágenes con la API de OpenAI. Interfaz en HTML, CSS y JavaScript, backend Python/Flask. **Sin Vercel, Supabase ni base de datos.**

## Descargar ImagenesGPT para Windows

**[⬇ Descargar instalador ImagenesGPT 1.0.0 (.exe)](https://github.com/raulcamaracarreon/ImagenesGPT/releases/download/v1.0.0/ImagenesGPT-Setup-1.0.0.exe)**

Instala la aplicación con unos clics, sin necesidad de Python, Conda o Git. Al abrirla por primera vez, introduce tu propia clave de la API de OpenAI. La aplicación es gratuita; las generaciones se cobran según el consumo de la API.

[Ver todas las versiones publicadas](https://github.com/raulcamaracarreon/ImagenesGPT/releases).

## Instalación desde el código fuente (para desarrollo)

1. Descarga o clona el repositorio y extrae los archivos a una carpeta.
2. Necesitas Python 3.11 o superior. Puedes usar Python instalado desde [python.org](https://www.python.org/downloads/) o una instalación existente, por ejemplo Miniforge. El instalador acepta `py`, `python`, `python3` y Python de un entorno Conda activado. No instales otra copia de Python si ya tienes una versión compatible.
3. Haz doble clic en **`instalar.bat`** para crear el entorno virtual e instalar dependencias.
4. En la interfaz, escribe tu propia clave de [OpenAI API](https://platform.openai.com/api-keys) y pulsa **Guardar clave**. La casilla **Recordar de forma segura en esta PC** está seleccionada por defecto; desactívala para utilizarla solo durante la sesión. Si ya tienes una clave en `.env`, seguirá funcionando sin configurar nada.
5. Haz doble clic en **`Iniciar generador.bat`**. Se abrirá el navegador en `http://127.0.0.1:5000`.
6. Usa las pestañas **Crear imagen** o **Editar imagen**. Para editar una creación anterior, selecciónala en **Creaciones recientes**, pulsa **Editar esta imagen**, escribe qué deseas cambiar y pulsa **Editar imagen**. También puedes editar un archivo de tu PC como hasta ahora. La edición genera un archivo nuevo y conserva el original. Las imágenes se guardan en `imagenes/`. Para descargarlas, selecciona JPG (predeterminado), PNG o WebP en **Guardar como** y pulsa **Descargar**.

Si aparece «No se encontró una instalación accesible de Python», ejecuta `python --version`, `py --version` y `where.exe python` en PowerShell. En Miniforge Prompt puedes activar un entorno de Python 3.11+ y ejecutar `instalar.bat` desde la carpeta del proyecto.

Para cerrar, cierra la ventana de comandos donde se está ejecutando Flask.

## Configuración y costos

La clave se guarda, si lo autorizas, en el Administrador de credenciales de Windows mediante `keyring`, vinculada a la cuenta de Windows. Nunca se incluye en el repositorio ni se devuelve al navegador. También puedes introducirla solo durante la sesión sin guardarla o continuar utilizando tu `.env` local anterior. **Quitar clave guardada** elimina la credencial de Windows y cualquier clave de sesión, pero no elimina una clave existente en `.env`.

El archivo opcional `.env` admite `OPENAI_API_KEY`. También puedes establecer `MAX_DAILY_REQUESTS=20` para imponer un límite local de imágenes por día; `0` significa que la aplicación no impone límite. Este contador se basa en archivos guardados: **no es un límite financiero garantizado** y no contabiliza solicitudes que fallen, se interrumpan o se ejecuten fuera de esta aplicación. Usa además los límites y avisos de tu cuenta de OpenAI.

La API de OpenAI **se factura por separado** de ChatGPT y requiere créditos o facturación habilitada. Los modelos GPT Image pueden exigir verificación de la organización. No se realiza ninguna solicitud de generación hasta que haces clic en el botón correspondiente.

## Seguridad

- El servidor escucha exclusivamente en `127.0.0.1:5000`, no en la red local.
- La clave permanece en el backend y no se envía al navegador.
- Los formularios de generación y edición usan un token local que se renueva al reiniciar.
- `.env`, las imágenes generadas y `.venv` quedan excluidos de Git.
- La app solo acepta archivos PNG, JPG o WebP de hasta 12 MB para edición.

## Desarrollo y pruebas

```powershell
python -m venv .venv  # alternativamente: py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe app.py
```

## Alcance del MVP

Generación, edición de una imagen existente tanto de la PC como del historial, orientación, selección de modelo/calidad, vista previa, descarga en JPG/PNG/WebP y galería local de las últimas 60 imágenes. La galería se reconstruye desde los archivos, sin una base de datos. La edición conversacional de varias rondas y estimación exacta de gastos quedan fuera de esta versión.

Documentación: [OpenAI Image generation](https://developers.openai.com/api/docs/guides/image-generation).

## Formatos de descarga

Los originales se guardan en `imagenes/` como WebP. El selector **Guardar como** permite descargar **JPG** (valor predeterminado y formato de uso cotidiano), **PNG** (conserva transparencias) o **WebP** (original ligero), tanto de imágenes nuevas como de las anteriores. La conversión se realiza localmente mediante Pillow, no consume créditos de la API, no reemplaza el original y no crea copias adicionales en la galería. Para JPG las áreas transparentes se muestran blancas. Convertir WebP a PNG no recupera detalles perdidos si el original ya estaba comprimido.

## Usuarios del repositorio público

Cada instalación utiliza la clave del usuario que la configura, con consumo facturado a la cuenta de API correspondiente. **No se distribuye ninguna clave API**. No publiques tu clave ni la envíes a terceros. Usa un proyecto separado y límites de gasto en OpenAI Platform. El almacenamiento de Windows protege la clave en reposo, pero no impide el acceso de otros programas ejecutados por la misma cuenta de Windows. Si optas por «solo esta sesión», la clave reside exclusivamente en la memoria del proceso Python hasta cerrarlo. Para ejecutar las pruebas, instala `requirements-dev.txt`; no se realizan solicitudes pagadas de OpenAI.

## Distribución para Windows: ejecutable e instalador

La aplicación también puede distribuirse sin Python instalado en el equipo de destino.

### Etapa 1 — Portable (compilar y probar primero)

En **PowerShell de Windows**, desde la carpeta del repositorio, ejecuta:

    .\build-portable.ps1

El script instala herramientas de empaquetado en el entorno virtual local, ejecuta las pruebas automatizadas y compila mediante PyInstaller. El resultado aparece en:

    dist\ImagenesGPT\ImagenesGPT.exe

Abre el .exe con doble clic: aparece una ventana de control con opciones de abrir el navegador, abrir la carpeta de imágenes y cerrar el programa. Para distribuirlo, se debe **compartir toda la carpeta** dist\ImagenesGPT (puede comprimirse en un ZIP de distribución), no solamente el .exe. El usuario final **no requiere Python, Conda, pip ni GitHub**. La compilación de Windows debe realizarse en Windows.

### Etapa 2 — Instalador y desinstalador (después de validar el portable)

Requiere **Inno Setup 7 o 6** [descargable desde su web oficial](https://jrsoftware.org/isdl.php) **solo en la computadora del desarrollador**. Cuando el ejecutable portátil funcione correctamente, ejecuta:

    .\build-installer.ps1

Esto generará, si Inno Setup está instalado:

    dist\setup\ImagenesGPT-Setup-1.0.0.exe

El instalador incluirá accesos directos y una entrada en **Aplicaciones instaladas** de Windows. **Muestra siempre la pantalla para elegir la carpeta de instalación**: propone `%LOCALAPPDATA%\Programs\ImagenesGPT` por defecto, pero permite instalar en otra carpeta o unidad donde el usuario tenga permisos de escritura. Al reinstalar, propone la ubicación elegida anteriormente. El modo predeterminado es instalación por usuario (`PrivilegesRequired=lowest`), sin solicitud automática de permisos elevados; por eso instalar en una carpeta protegida como `C:\Program Files` puede provocar «Acceso denegado». Inno Setup proporciona el desinstalador automáticamente; elimina el programa y sus accesos directos.

### Qué se conserva al actualizar o desinstalar

- La versión de desarrollo sigue utilizando la carpeta `imagenes/` del repositorio y admite `.env` local como hasta ahora.
- La versión ejecutable guarda las imágenes en **%LOCALAPPDATA%\ImagenesGPT\imagenes** (cada cuenta de Windows tiene su propia carpeta).
- La clave API recordada se conserva en el **Administrador de credenciales de Windows**. No está incorporada al ejecutable.
- Por seguridad, **la desinstalación NO elimina automáticamente las imágenes ni la clave API**. Esto evita pérdidas accidentales. Para borrarlas definitivamente, primero usa «Quitar clave guardada» en ImagenesGPT y elimina manualmente la carpeta de imágenes tras hacer una copia de seguridad.

Un ejecutable sin firma digital puede mostrar la advertencia **editor desconocido** o SmartScreen. Las pruebas de compilación, de instalador y de desinstalación deben realizarse en Windows antes de distribuir una versión pública. No se utiliza GitHub Actions.
