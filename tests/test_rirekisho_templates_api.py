from io import BytesIO

from docx import Document


def _upload(client, sample_rirekisho_docx_bytes, name="My Template"):
    files = {
        "file": (
            "template.docx",
            sample_rirekisho_docx_bytes(),
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    }
    return client.post("/api/rirekisho-templates", data={"name": name}, files=files)


def test_upload_first_template_is_auto_selected(client, sample_rirekisho_docx_bytes):
    resp = _upload(client, sample_rirekisho_docx_bytes)
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "My Template"
    assert body["is_selected"] is True


def test_upload_rejects_non_docx_file(client):
    files = {"file": ("template.txt", b"not a docx", "text/plain")}
    resp = client.post("/api/rirekisho-templates", data={"name": "Bad"}, files=files)
    assert resp.status_code == 400


def test_second_template_is_not_auto_selected(client, sample_rirekisho_docx_bytes):
    _upload(client, sample_rirekisho_docx_bytes, name="First")
    second = _upload(client, sample_rirekisho_docx_bytes, name="Second").json()
    assert second["is_selected"] is False


def test_update_name_and_select(client, sample_rirekisho_docx_bytes):
    first = _upload(client, sample_rirekisho_docx_bytes, name="First").json()
    second = _upload(client, sample_rirekisho_docx_bytes, name="Second").json()

    resp = client.put(f"/api/rirekisho-templates/{second['id']}", json={"name": "Renamed", "is_selected": True})
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "Renamed"
    assert body["is_selected"] is True

    templates = {t["id"]: t for t in client.get("/api/rirekisho-templates").json()}
    assert templates[first["id"]]["is_selected"] is False
    assert templates[second["id"]]["is_selected"] is True


def test_update_missing_template_returns_404(client):
    resp = client.put("/api/rirekisho-templates/does-not-exist", json={"name": "x"})
    assert resp.status_code == 404


def test_generate_returns_a_docx_file(client, sample_rirekisho_docx_bytes):
    template = _upload(client, sample_rirekisho_docx_bytes).json()
    client.put("/api/personal-info", json={"name": "Taro Yamada"})

    resp = client.post(f"/api/rirekisho-templates/{template['id']}/generate")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == ("application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    doc = Document(BytesIO(resp.content))
    text = "\n".join(p.text for p in doc.paragraphs)
    assert "Taro Yamada" in text


def test_generate_missing_template_returns_404(client):
    resp = client.post("/api/rirekisho-templates/does-not-exist/generate")
    assert resp.status_code == 404


def test_delete_removes_template(client, sample_rirekisho_docx_bytes):
    template = _upload(client, sample_rirekisho_docx_bytes).json()
    resp = client.delete(f"/api/rirekisho-templates/{template['id']}")
    assert resp.status_code == 200
    assert client.get("/api/rirekisho-templates").json() == []


def test_backup_export_includes_file_content(client, sample_rirekisho_docx_bytes):
    _upload(client, sample_rirekisho_docx_bytes)

    body = client.get("/api/backup/export").json()
    assert len(body["rirekisho_templates"]) == 1
    assert body["rirekisho_templates"][0]["file_content_base64"] is not None


def test_backup_import_restores_template(client, sample_rirekisho_docx_bytes):
    _upload(client, sample_rirekisho_docx_bytes, name="Original")
    backup = client.get("/api/backup/export").json()
    client.post("/api/backup/reset-all")

    resp = client.post("/api/backup/import", json=backup)
    assert resp.status_code == 200
    assert resp.json()["rirekisho_templates"] == 1

    restored = client.get("/api/rirekisho-templates").json()
    assert len(restored) == 1
    assert restored[0]["name"] == "Original"
    # is_selected is deliberately never imported (same as resume_templates).
    assert restored[0]["is_selected"] is False
