# Imágenes GPT

Aplicación **local para Windows** que genera y edita imágenes con la API de OpenAI. Interfaz en HTML, CSS y JavaScript, backend Python/Flask. **Sin Vercel, Supabase ni base de datos.**

## Instalación (Windows)

1. Descarga o clona el repositorio y extrae los archivos a una carpeta.
2. Necesitas Python 3.11 o superior. Puedes usar Python instalado desde [python.org](https://www.python.org/downloads/) o una instalación existente, por ejemplo Miniforge. El instalador acepta `py`, `python`, `python3` y Python de un entorno Conda activado. No instales otra copia de Python si ya tienes una versión compatible.
3. Haz doble clic en **`instalar.bat`** para crear el entorno virtual e instalar dependencias.
4. Abre el archivo **`.env`** y reemplaza `pega_aqui_tu_clave_api` por tu clave de [OpenAI API](https://platform.openai.com/api-keys). **No compartas esta clave y no subas `.env` a GitHub.**
5. Haz doble clic en **`Iniciar generador.bat`**. Se abrirá el navegador en `http://127.0.0.1:5000`.
6. Usa las pestañas **Crear imagen** o **Editar imagen**. Las imágenes se guardan en la carpeta `imagenes/`.

Si aparece «No se encontró una instalación accesible de Python», ejecuta `python --version`, `py --version` y `where.exe python` en PowerShell. En Miniforge Prompt puedes activar un entorno de Python 3.11+ y ejecutar `instalar.bat` desde la carpeta del proyecto.

Para cerrar, cierra la ventana de comandos donde se está ejecutando Flask.

## Configuración y costos

El archivo `.env` contiene `OPENAI_API_KEY`. También puedes establecer `MAX_DAILY_REQUESTS=20` para imponer un límite local de imágenes por día; `0` significa que la aplicación no impone límite. Este contador se basa en archivos guardados: **no es un límite financiero garantizado** y no contabiliza solicitudes que fallen, se interrumpan o se ejecuten fuera de esta aplicación. Usa además los límites y avisos de tu cuenta de OpenAI.

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

Generación, edición de una imagen existente, orientación, selección de modelo/calidad, vista previa, descarga y galería local de las últimas 60 imágenes. La galería se reconstruye desde los archivos, sin una base de datos. La edición conversacional de varias rondas y estimación exacta de gastos quedan fuera de esta versión.

Documentación: [OpenAI Image generation](https://developers.openai.com/api/docs/guides/image-generation).
