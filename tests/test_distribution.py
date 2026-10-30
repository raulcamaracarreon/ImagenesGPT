"""La versión empaquetada no debe escribir dentro del programa."""
import app as application


def test_development_storage_remains_in_repository(monkeypatch):
    monkeypatch.delattr(application.sys, "frozen", raising=False)
    assert application.storage_directory() == application.BASE_DIR / "imagenes"


def test_packaged_storage_uses_local_appdata(monkeypatch, tmp_path):
    monkeypatch.setattr(application.sys, "frozen", True, raising=False)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    assert application.storage_directory() == tmp_path / "ImagenesGPT" / "imagenes"
    assert application.storage_directory() != application.BASE_DIR / "imagenes"
