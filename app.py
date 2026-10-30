"""Aplicación local para generar y editar imágenes mediante OpenAI."""

from __future__ import annotations

import base64
import hmac
import io
import os
import re
import secrets
import threading
from datetime import date, datetime
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from flask import Flask, abort, jsonify, render_template, request, send_file, send_from_directory
from openai import OpenAI, OpenAIError
from PIL import Image, UnidentifiedImageError

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
OUTPUT_DIR = BASE_DIR / "imagenes"
OUTPUT_DIR.mkdir(exist_ok=True)

MODELS = {
    "gpt-image-2.5-flare": "GPT Image 2.5 Flare",
    "gpt-image-2.5-sunburst": "GPT Image 2.5 Sunburst",
    "gpt-image-1-mini": "GPT Image 1 Mini (económico)",
}
SIZES = {"1024x1024", "1024x1536", "1536x1024"}
QUALITIES = {"low", "medium", "high"}

app = Flask(__name__)
app.config.update(
    MAX_CONTENT_LENGTH=12 * 1024 * 1024,
    TRUSTED_HOSTS=["localhost", "127.0.0.1"],
)
LOCAL_TOKEN = secrets.token_urlsafe(32)
request_lock = threading.Lock()


def _client() -> OpenAI:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("Configura OPENAI_API_KEY en el archivo .env.")
    return OpenAI(api_key=key, timeout=180, max_retries=1)


def _validate_request() -> tuple[str, str, str, str]:
    prompt = request.form.get("prompt", "").strip()
    model = request.form.get("model", "gpt-image-2.5-flare")
    size = request.form.get("size", "1024x1024")
    quality = request.form.get("quality", "medium")
    if not prompt or len(prompt) > 32000:
        raise ValueError("Escribe una descripción de hasta 32,000 caracteres.")
    if model not in MODELS or size not in SIZES or quality not in QUALITIES:
        raise ValueError("Modelo, calidad o formato no válido.")
    return prompt, model, size, quality


def _today_count() -> int:
    stamp = date.today().strftime("%Y%m%d")
    return sum(1 for path in OUTPUT_DIR.glob(f"{stamp}_*.webp") if path.is_file())


def _check_limit() -> None:
    raw = os.getenv("MAX_DAILY_REQUESTS", "0")
    try:
        limit = max(0, int(raw))
    except ValueError:
        limit = 0
    if limit and _today_count() >= limit:
        raise ValueError(f"Se alcanzó el límite local de {limit} imágenes para hoy.")


def _save_image(result) -> str:
    data = getattr(result.data[0], "b64_json", None) if getattr(result, "data", None) else None
    if not data:
        raise RuntimeError("OpenAI no devolvió una imagen.")
    content = base64.b64decode(data, validate=True)
    # Comprobación básica del archivo devuelto antes de guardarlo.
    with Image.open(io.BytesIO(content)) as image:
        if image.format != "WEBP":
            raise RuntimeError("Formato de imagen inesperado en la respuesta.")
        image.verify()
    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:10]}.webp"
    (OUTPUT_DIR / filename).write_bytes(content)
    return filename


def _require_local_token() -> None:
    candidate = request.headers.get("X-Local-Token", "")
    if not hmac.compare_digest(candidate, LOCAL_TOKEN):
        abort(403)


def _perform(kind: str):
    _require_local_token()
    if not request_lock.acquire(blocking=False):
        return jsonify(error="Ya hay una generación en curso. Espera a que termine."), 429
    try:
        prompt, model, size, quality = _validate_request()
        _check_limit()
        params = dict(model=model, prompt=prompt, size=size, quality=quality, output_format="webp", n=1)
        client = _client()
        if kind == "edit":
            upload = request.files.get("image")
            if not upload or not upload.filename:
                raise ValueError("Selecciona una imagen para editar.")
            try:
                with Image.open(upload.stream) as image:
                    image.verify()
                    fmt = image.format
            except (UnidentifiedImageError, OSError, ValueError) as exc:
                raise ValueError("El archivo no es una imagen válida.") from exc
            if fmt not in {"PNG", "JPEG", "WEBP"}:
                raise ValueError("Usa una imagen PNG, JPG o WebP.")
            upload.stream.seek(0)
            image_data = io.BytesIO(upload.stream.read())
            image_data.name = "referencia." + {"PNG": "png", "JPEG": "jpg", "WEBP": "webp"}[fmt]
            result = client.images.edit(image=image_data, **params)
        else:
            result = client.images.generate(**params)
        filename = _save_image(result)
        return jsonify(ok=True, filename=filename, url=f"/imagenes/{filename}")
    except ValueError as exc:
        return jsonify(error=str(exc)), 400
    except RuntimeError as exc:
        return jsonify(error=str(exc)), 503
    except OpenAIError as exc:
        # No exponer credenciales ni detalles completos de las solicitudes.
        status = getattr(exc, "status_code", None)
        if status == 401:
            message = "La clave API no es válida. Revisa tu archivo .env."
        elif status == 429:
            message = "La API alcanzó su cuota o límite de velocidad. Revisa tu cuenta de OpenAI."
        else:
            message = "OpenAI no pudo completar la solicitud. Revisa el saldo, acceso al modelo o vuelve a intentarlo."
        app.logger.warning("Error de OpenAI (%s): %s", status, type(exc).__name__)
        return jsonify(error=message), 502
    except Exception:
        app.logger.exception("Error inesperado al procesar una imagen")
        return jsonify(error="Ocurrió un error inesperado al procesar la imagen."), 500
    finally:
        request_lock.release()


@app.get("/")
def home():
    return render_template("index.html", local_token=LOCAL_TOKEN, models=MODELS)


@app.post("/api/generate")
def generate():
    return _perform("generate")


@app.post("/api/edit")
def edit():
    return _perform("edit")


@app.get("/api/gallery")
def gallery():
    paths = sorted(OUTPUT_DIR.glob("*.webp"), key=lambda p: p.stat().st_mtime, reverse=True)
    return jsonify(images=[{"filename": p.name, "url": f"/imagenes/{p.name}"} for p in paths[:60]])


@app.get("/imagenes/<path:filename>")
def image_file(filename):
    if not filename.endswith(".webp"):
        abort(404)
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=False)


@app.get("/api/download/<filename>")
def download_image(filename):
    """Descargar una copia en el formato elegido sin modificar el original WebP."""
    if not re.fullmatch(r"\d{8}_\d{6}_[0-9a-f]{10}\.webp", filename):
        abort(404)

    source = OUTPUT_DIR / filename
    if not source.is_file():
        abort(404)

    output_format = request.args.get("format", "jpg").lower()
    if output_format not in {"jpg", "png", "webp"}:
        abort(400, description="Formato de descarga no válido.")
    if output_format == "webp":
        return send_file(source, as_attachment=True, download_name=filename, mimetype="image/webp")

    output = io.BytesIO()
    try:
        with Image.open(source) as image:
            if output_format == "png":
                image.save(output, format="PNG", optimize=True)
            else:
                # JPEG no admite transparencia: utilizar blanco en áreas transparentes.
                if "A" in image.getbands() or "transparency" in image.info:
                    rgba = image.convert("RGBA")
                    flattened = Image.new("RGB", rgba.size, "white")
                    flattened.paste(rgba, mask=rgba.getchannel("A"))
                    image_to_save = flattened
                else:
                    image_to_save = image.convert("RGB")
                image_to_save.save(output, format="JPEG", quality=93, subsampling=0)
    except (OSError, UnidentifiedImageError):
        abort(500, description="No se pudo convertir la imagen.")

    output.seek(0)
    return send_file(
        output,
        mimetype="image/png" if output_format == "png" else "image/jpeg",
        as_attachment=True,
        download_name=f"{filename[:-5]}.{output_format}",
    )


@app.errorhandler(413)
def too_large(_error):
    return jsonify(error="La imagen excede el límite de 12 MB."), 413


if __name__ == "__main__":
    print("ImagenesGPT disponible en http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)
