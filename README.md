# Imágenes GPT

Aplicación **local para Windows** que genera y edita imágenes con la API de OpenAI. Interfaz en HTML, CSS y JavaScript, backend Python/Flask. **Sin Vercel, Supabase ni base de datos.**

## Instalación (Windows)

1. Descarga o clona el repositorio y extrae los archivos a una carpeta.
2. Necesitas Python 3.11 o superior. Puedes usar Python instalado desde [python.org](https://www.python.org/downloads/) o una instalación existente, por ejemplo Miniforge. El instalador acepta `py`, `python`, `python3` y Python de un entorno Conda activado. No instales otra copia de Python si ya tienes una versión compatible.
3. Haz doble clic en **`instalar.bat`** para crear el entorno virtual e instalar dependencias.
4. En la interfaz, escribe tu propia clave de [OpenAI API](https://platform.openai.com/api-keys) y pulsa **Guardar clave**. La casilla **Recordar de forma segura en esta PC** está seleccionada por defecto; desactívala para utilizarla solo durante la sesión. Si ya tienes una clave en `.env`, seguirá funcionando sin configurar nada.
5. Haz doble clic en **`Iniciar generador.bat`**. Se abrirá el navegador en `http://127.0.0.1:5000`.
6. Usa las pestañas **Crear imagen** o **Editar imagen**. Las imágenes se guardan en la carpeta `imagenes/`. Para descargarlas, selecciona JPG (predeterminado), PNG o WebP en **Guardar como** y pulsa **Descargar**.

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

Generación, edición de una imagen existente, orientación, selección de modelo/calidad, vista previa, descarga en JPG/PNG/WebP y galería local de las últimas 60 imágenes. La galería se reconstruye desde los archivos, sin una base de datos. La edición conversacional de varias rondas y estimación exacta de gastos quedan fuera de esta versión.

Documentación: [OpenAI Image generation](https://developers.openai.com/api/docs/guides/image-generation).

## Formatos de descarga

Los originales se guardan en `imagenes/` como WebP. El selector **Guardar como** permite descargar **JPG** (valor predeterminado y formato de uso cotidiano), **PNG** (conserva transparencias) o **WebP** (original ligero), tanto de imágenes nuevas como de las anteriores. La conversión se realiza localmente mediante Pillow, no consume créditos de la API, no reemplaza el original y no crea copias adicionales en la galería. Para JPG las áreas transparentes se muestran blancas. Convertir WebP a PNG no recupera detalles perdidos si el original ya estaba comprimido.

## Usuarios del repositorio público

Cada instalación utiliza la clave del usuario que la configura, con consumo facturado a la cuenta de API correspondiente. **No se distribuye ninguna clave API**. No publiques tu clave ni la envíes a terceros. Usa un proyecto separado y límites de gasto en OpenAI Platform. El almacenamiento de Windows protege la clave en reposo, pero no impide el acceso de otros programas ejecutados por la misma cuenta de Windows. Si optas por «solo esta sesión», la clave reside exclusivamente en la memoria del proceso Python hasta cerrarlo. Para ejecutar las pruebas, instala `requirements-dev.txt`; no se realizan solicitudes pagadas de OpenAI.
