import base64
import io
from pathlib import Path
from types import SimpleNamespace

import pytest
from PIL import Image

import app as application


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(application, "OUTPUT_DIR", tmp_path)
    application.app.config.update(TESTING=True)
    return application.app.test_client()


def token_headers():
    return {"X-Local-Token": application.LOCAL_TOKEN}


def sample_webp():
    stream = io.BytesIO()
    Image.new("RGB", (3, 3), "red").save(stream, format="WEBP")
    return stream.getvalue()


class DummyImages:
    def __init__(self):
        self.last = None

    def generate(self, **kwargs):
        self.last = ("generate", kwargs)
        return SimpleNamespace(data=[SimpleNamespace(b64_json=base64.b64encode(sample_webp()).decode())])

    def edit(self, **kwargs):
        self.last = ("edit", kwargs)
        assert kwargs["image"].read()
        return self.generate(**{key: value for key, value in kwargs.items() if key != "image"})


def test_home_and_empty_gallery(client):
    assert client.get("/").status_code == 200
    assert client.get("/api/gallery").json == {"images": []}


def test_token_required(client):
    response = client.post("/api/generate", data={"prompt": "Un paisaje"})
    assert response.status_code == 403


def test_validation_prevents_api_call(client):
    response = client.post("/api/generate", headers=token_headers(), data={"prompt": "Hola", "model": "desconocido"})
    assert response.status_code == 400


def test_generate_and_gallery(client, monkeypatch):
    dummy = DummyImages()
    monkeypatch.setattr(application, "_client", lambda: SimpleNamespace(images=dummy))
    response = client.post("/api/generate", headers=token_headers(), data={"prompt": "Una flor", "model": "gpt-image-2.5-flare", "size": "1024x1024", "quality": "medium"})
    assert response.status_code == 200
    assert response.json["ok"] is True
    assert dummy.last[0] == "generate"
    assert (application.OUTPUT_DIR / response.json["filename"]).exists()
    assert len(client.get("/api/gallery").json["images"]) == 1
    assert client.get(response.json["url"]).status_code == 200


def test_edit(client, monkeypatch):
    dummy = DummyImages()
    monkeypatch.setattr(application, "_client", lambda: SimpleNamespace(images=dummy))
    stream = io.BytesIO()
    Image.new("RGB", (3, 3)).save(stream, format="PNG")
    stream.seek(0)
    response = client.post("/api/edit", headers=token_headers(), data={"prompt": "Ponle flores", "image": (stream, "foto.png")}, content_type="multipart/form-data")
    assert response.status_code == 200
    assert response.json["ok"] is True


def test_daily_limit(client, monkeypatch):
    monkeypatch.setenv("MAX_DAILY_REQUESTS", "1")
    dummy = DummyImages()
    monkeypatch.setattr(application, "_client", lambda: SimpleNamespace(images=dummy))
    data = {"prompt": "Una flor"}
    assert client.post("/api/generate", headers=token_headers(), data=data).status_code == 200
    assert client.post("/api/generate", headers=token_headers(), data=data).status_code == 400


def test_invalid_file(client, monkeypatch):
    monkeypatch.setattr(application, "_client", lambda: SimpleNamespace(images=DummyImages()))
    response = client.post("/api/edit", headers=token_headers(), data={"prompt": "Editar", "image": (io.BytesIO(b"not image"), "fake.png")}, content_type="multipart/form-data")
    assert response.status_code == 400

def test_download_formats_preserve_original(client):
    filename = "20261030_100000_123456abcd.webp"
    original = sample_webp()
    (application.OUTPUT_DIR / filename).write_bytes(original)

    for extension, expected_format, mime in (
        ("jpg", "JPEG", "image/jpeg"),
        ("png", "PNG", "image/png"),
        ("webp", "WEBP", "image/webp"),
    ):
        response = client.get(f"/api/download/{filename}?format={extension}")
        assert response.status_code == 200
        assert response.mimetype == mime
        assert f"{filename[:-5]}.{extension}" in response.headers["Content-Disposition"]
        with Image.open(io.BytesIO(response.data)) as image:
            assert image.format == expected_format
            assert image.size == (3, 3)

    assert (application.OUTPUT_DIR / filename).read_bytes() == original
    assert len(list(application.OUTPUT_DIR.iterdir())) == 1


def test_download_rejects_unknown_format_or_file(client):
    filename = "20261030_100000_123456abcd.webp"
    (application.OUTPUT_DIR / filename).write_bytes(sample_webp())
    assert client.get(f"/api/download/{filename}?format=invalid").status_code == 400
    assert client.get("/api/download/README.md?format=jpg").status_code == 404
    assert client.get("/api/download/20261030_100000_fffffffffe.webp?format=jpg").status_code == 404


def test_jpg_export_uses_white_background_for_transparency(client):
    filename = "20261030_100000_123456abcd.webp"
    stream = io.BytesIO()
    Image.new("RGBA", (12, 12), (0, 0, 0, 0)).save(stream, format="WEBP", lossless=True)
    (application.OUTPUT_DIR / filename).write_bytes(stream.getvalue())
    response = client.get(f"/api/download/{filename}?format=jpg")
    assert response.status_code == 200
    with Image.open(io.BytesIO(response.data)) as image:
        assert image.mode == "RGB"
        assert all(channel >= 245 for channel in image.getpixel((6, 6)))


def test_download_select_visible_in_interface(client):
    html = client.get("/").get_data(as_text=True)
    assert 'id="download-format"' in html
    assert '<option value="jpg" selected>JPG</option>' in html
