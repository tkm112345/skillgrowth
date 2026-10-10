def _upload(client, sample_md_template_bytes, name="My Markdown Template"):
    files = {"file": ("template.md", sample_md_template_bytes(), "text/markdown")}
    return client.post("/api/resume-md-templates", data={"name": name}, files=files)


def test_upload_first_template_is_auto_selected(client, sample_md_template_bytes):
    resp = _upload(client, sample_md_template_bytes)
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "My Markdown Template"
    assert body["is_selected"] is True


def test_upload_rejects_non_md_file(client):
    files = {"file": ("template.docx", b"not markdown", "application/octet-stream")}
    resp = client.post("/api/resume-md-templates", data={"name": "Bad"}, files=files)
    assert resp.status_code == 400


def test_second_template_is_not_auto_selected(client, sample_md_template_bytes):
    _upload(client, sample_md_template_bytes, name="First")
    second = _upload(client, sample_md_template_bytes, name="Second").json()
    assert second["is_selected"] is False


def test_update_section_formats_and_select(client, sample_md_template_bytes):
    first = _upload(client, sample_md_template_bytes, name="First").json()
    second = _upload(client, sample_md_template_bytes, name="Second").json()

    resp = client.put(
        f"/api/resume-md-templates/{second['id']}",
        json={"section_formats": {"skills": "table", "employment": "bullet"}, "is_selected": True},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["section_formats"] == '{"skills": "table", "employment": "bullet"}'
    assert body["is_selected"] is True

    templates = {t["id"]: t for t in client.get("/api/resume-md-templates").json()}
    assert templates[first["id"]]["is_selected"] is False
    assert templates[second["id"]]["is_selected"] is True


def test_update_rejects_invalid_section_format(client, sample_md_template_bytes):
    template = _upload(client, sample_md_template_bytes).json()
    resp = client.put(
        f"/api/resume-md-templates/{template['id']}",
        json={"section_formats": {"skills": "not-a-real-choice"}},
    )
    assert resp.status_code == 400


def test_generate_returns_a_markdown_file(client, sample_md_template_bytes):
    template = _upload(client, sample_md_template_bytes).json()
    client.post("/api/skills", json={"name": "Python", "category": "技術"})

    resp = client.post(f"/api/resume-md-templates/{template['id']}/generate")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/markdown")
    assert "Python" in resp.text


def test_generate_missing_template_returns_404(client):
    resp = client.post("/api/resume-md-templates/does-not-exist/generate")
    assert resp.status_code == 404


def test_delete_removes_template(client, sample_md_template_bytes):
    template = _upload(client, sample_md_template_bytes).json()
    resp = client.delete(f"/api/resume-md-templates/{template['id']}")
    assert resp.status_code == 200
    assert client.get("/api/resume-md-templates").json() == []
