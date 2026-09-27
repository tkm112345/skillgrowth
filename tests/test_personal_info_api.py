def test_get_personal_info_defaults_when_unset(client):
    resp = client.get("/api/personal-info")
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == ""
    assert body["photo_path"] is None


def test_update_personal_info(client):
    resp = client.put(
        "/api/personal-info",
        json={
            "name": "Taro Yamada",
            "name_kana": "ヤマダ タロウ",
            "birthdate": "1990-04-01",
            "postal_code": "100-0001",
            "address": "Tokyo",
            "address_kana": "トウキョウ",
            "phone": "090-0000-0000",
            "email": "taro@example.com",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "Taro Yamada"
    assert body["birthdate"] == "1990-04-01"

    again = client.get("/api/personal-info").json()
    assert again["name"] == "Taro Yamada"


def test_upload_and_delete_photo(client):
    files = {"file": ("photo.jpg", b"fake-image-bytes", "image/jpeg")}
    resp = client.post("/api/personal-info/photo", files=files)
    assert resp.status_code == 200
    assert resp.json()["photo_path"] is not None

    download = client.get("/api/personal-info/photo")
    assert download.status_code == 200
    assert download.content == b"fake-image-bytes"

    resp = client.delete("/api/personal-info/photo")
    assert resp.status_code == 200
    assert resp.json()["photo_path"] is None

    assert client.get("/api/personal-info/photo").status_code == 404


def test_get_photo_missing_returns_404(client):
    resp = client.get("/api/personal-info/photo")
    assert resp.status_code == 404


def test_backup_export_includes_personal_info_with_photo_content(client):
    client.put("/api/personal-info", json={"name": "Taro Yamada"})
    client.post("/api/personal-info/photo", files={"file": ("photo.jpg", b"fake-image-bytes", "image/jpeg")})

    body = client.get("/api/backup/export").json()
    assert len(body["personal_info"]) == 1
    assert body["personal_info"][0]["name"] == "Taro Yamada"
    assert body["personal_info"][0]["photo_content_base64"] is not None


def test_backup_import_restores_personal_info_and_photo(client):
    client.put("/api/personal-info", json={"name": "Taro Yamada"})
    client.post("/api/personal-info/photo", files={"file": ("photo.jpg", b"fake-image-bytes", "image/jpeg")})
    backup = client.get("/api/backup/export").json()
    client.post("/api/backup/reset-all")

    resp = client.post("/api/backup/import", json=backup)
    assert resp.status_code == 200
    assert resp.json()["personal_info"] == 1

    restored = client.get("/api/personal-info").json()
    assert restored["name"] == "Taro Yamada"
    assert client.get("/api/personal-info/photo").content == b"fake-image-bytes"


def test_backup_import_never_overwrites_existing_personal_info(client):
    client.put("/api/personal-info", json={"name": "Original"})
    backup = client.get("/api/backup/export").json()  # captured with name="Original"

    client.put("/api/personal-info", json={"name": "Already set locally"})
    client.post("/api/backup/import", json=backup)

    # A PersonalInfo row already exists on this instance, so the import must
    # not overwrite it with the backup's "Original" — all-or-nothing, never
    # partial-merge (see backup_import.py's comment on this).
    assert client.get("/api/personal-info").json()["name"] == "Already set locally"
