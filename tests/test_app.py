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


@pytest.fixture
def fake_credentials(client, monkeypatch):
    credentials = {}
    monkeypatch.setattr(application, "SESSION_API_KEY", None)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(application.keyring, "get_password", lambda service, user: credentials.get((service, user)))
    monkeypatch.setattr(application.keyring, "set_password", lambda service, user, password: credentials.__setitem__((service, user), password))
    def delete_password(service, user):
        if (service, user) not in credentials:
            raise application.PasswordDeleteError("No existe")
        del credentials[(service, user)]
    monkeypatch.setattr(application.keyring, "delete_password", delete_password)
    return credentials


def test_api_key_status_and_no_exposure(client, fake_credentials):
    response = client.get("/api/key", headers=token_headers())
    assert response.json == {"configured": False, "source": "missing"}
    assert "api_key" not in response.json
    assert client.get("/api/key").status_code == 403


def test_save_persistent_key_and_remove_it(client, fake_credentials):
    key = "sk-test-clave-que-no-se-publica"
    result = client.post("/api/key", headers=token_headers(), json={"api_key": key, "remember": True})
    assert result.status_code == 200
    assert result.json == {"ok": True, "configured": True, "source": "saved"}
    assert key not in result.get_data(as_text=True)
    assert fake_credentials[(application.CREDENTIAL_SERVICE, application.CREDENTIAL_USER)] == key
    assert application._key_from_storage() == (key, "saved")
    result = client.post("/api/key/forget", headers=token_headers())
    assert result.status_code == 200
    assert result.json["source"] == "missing"
    assert not fake_credentials


def test_session_key_is_not_remembered(client, fake_credentials):
    key = "sk-test-sesion-efimera"
    result = client.post("/api/key", headers=token_headers(), json={"api_key": key, "remember": False})
    assert result.status_code == 200
    assert result.json["source"] == "session"
    assert not fake_credentials
    assert application._key_from_storage() == (key, "session")
    application.SESSION_API_KEY = None
    assert application._key_from_storage() == ("", "missing")


def test_choose_session_removes_previously_saved_key(client, fake_credentials):
    old_key = "sk-test-clave-persistente"
    fake_credentials[(application.CREDENTIAL_SERVICE, application.CREDENTIAL_USER)] = old_key
    result = client.post("/api/key", headers=token_headers(), json={"api_key": "sk-test-sesion-nueva", "remember": False})
    assert result.status_code == 200
    assert not fake_credentials
    assert application._key_from_storage() == ("sk-test-sesion-nueva", "session")


def test_key_management_rejects_invalid_payloads(client, fake_credentials):
    assert client.post("/api/key", json={"api_key": "sk-valid-example", "remember": True}).status_code == 403
    for payload in [
        {"api_key": "corta", "remember": True},
        {"api_key": "sk-valid-example", "remember": "true"},
        {"api_key": "sk-test-\nsecret", "remember": True},
    ]:
        assert client.post("/api/key", headers=token_headers(), json=payload).status_code == 400
    assert not fake_credentials


def test_existing_dotenv_key_remains_supported(client, fake_credentials, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-example-env-key")
    assert client.get("/api/key", headers=token_headers()).json["source"] == "environment"
    assert application._key_from_storage()[0] == "sk-example-env-key"
    result = client.post("/api/key/forget", headers=token_headers())
    assert result.json["source"] == "environment"



def test_edit_from_gallery_preserves_original_and_creates_new_image(client, monkeypatch):
    dummy = DummyImages()
    monkeypatch.setattr(application, "_client", lambda: SimpleNamespace(images=dummy))
    source_name = "20261030_100000_123456abcd.webp"
    source_content = sample_webp()
    (application.OUTPUT_DIR / source_name).write_bytes(source_content)

    response = client.post(
        "/api/edit",
        headers=token_headers(),
        data={"prompt": "Añade flores", "saved_image": source_name},
    )
    assert response.status_code == 200
    assert response.json["ok"] is True
    assert dummy.last[0] == "generate"  # DummyImages.edit delega en generate.
    assert dummy.last[1]["prompt"] == "Añade flores"
    assert (application.OUTPUT_DIR / source_name).read_bytes() == source_content
    assert response.json["filename"] != source_name
    assert (application.OUTPUT_DIR / response.json["filename"]).exists()
    assert len(client.get("/api/gallery").json["images"]) == 2


@pytest.mark.parametrize("saved_name", [
    "../secret.webp",
    "..\\secret.webp",
    "another-file.webp",
    "20261030_100000_fffffffffe.webp",
])
def test_edit_rejects_invalid_or_missing_gallery_image(client, monkeypatch, saved_name):
    called = []
    monkeypatch.setattr(application, "_client", lambda: called.append(True))
    response = client.post(
        "/api/edit",
        headers=token_headers(),
        data={"prompt": "Editar", "saved_image": saved_name},
    )
    assert response.status_code == 400
    assert called == []


def test_edit_rejects_both_gallery_and_local_file(client, monkeypatch):
    source_name = "20261030_100000_123456abcd.webp"
    (application.OUTPUT_DIR / source_name).write_bytes(sample_webp())
    called = []
    monkeypatch.setattr(application, "_client", lambda: called.append(True))
    response = client.post(
        "/api/edit",
        headers=token_headers(),
        data={
            "prompt": "Editar",
            "saved_image": source_name,
            "image": (io.BytesIO(sample_webp()), "archivo.webp"),
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert called == []


def test_edit_from_gallery_requires_local_token(client):
    response = client.post(
        "/api/edit",
        data={"prompt": "Editar", "saved_image": "20261030_100000_123456abcd.webp"},
    )
    assert response.status_code == 403


def test_gallery_edit_controls_in_template(client):
    html = client.get("/").get_data(as_text=True)
    assert 'id="edit-current-btn"' in html
    assert 'id="saved-image"' in html
    assert 'name="saved_image"' in html
    assert 'id="clear-saved-image"' in html


def test_result_actions_share_a_single_toolbar(client):
    """Formato, descarga y edición aparecen agrupados sin márgenes negativos."""
    html = client.get("/").get_data(as_text=True)
    toolbar = html.split('id="download-controls"', 1)[1].split("</div>", 1)[0]
    assert 'id="download-format"' in toolbar
    assert 'id="download-btn"' in toolbar
    assert 'id="edit-current-btn"' in toolbar

    stylesheet = (application.BASE_DIR / "static" / "style.css").read_text(encoding="utf-8")
    assert ".edit-current{display:inline-flex" in stylesheet
    assert "margin:-13px" not in stylesheet
