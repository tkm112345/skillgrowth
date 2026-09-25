from pathlib import Path


def _create_item(client, title="My Deliverable", project_id=None):
    return client.post("/api/portfolio", json={"title": title, "description": "desc", "project_id": project_id})


def _create_standalone_project(client):
    return client.post("/api/profile/projects", json={"title": "Side project"}).json()["project"]["id"]


def _create_company_project(client):
    employment_id = client.post("/api/profile/employment", json={"company": "Acme"}).json()["employment"]["id"]
    return client.post("/api/profile/projects", json={"title": "Work project", "employment_id": employment_id}).json()[
        "project"
    ]["id"]


def test_create_item_requires_title(client):
    resp = client.post("/api/portfolio", json={"title": "   "})
    assert resp.status_code == 400


def test_create_and_list_item(client):
    resp = _create_item(client)
    assert resp.status_code == 200
    assert resp.json()["title"] == "My Deliverable"

    items = client.get("/api/portfolio").json()
    assert len(items) == 1


def test_create_item_with_standalone_project_succeeds(client):
    project_id = _create_standalone_project(client)
    resp = _create_item(client, project_id=project_id)
    assert resp.status_code == 200
    assert resp.json()["project_id"] == project_id


def test_create_item_with_company_project_rejected(client):
    project_id = _create_company_project(client)
    resp = _create_item(client, project_id=project_id)
    assert resp.status_code == 400


def test_create_item_with_unknown_project_rejected(client):
    resp = _create_item(client, project_id="does-not-exist")
    assert resp.status_code == 400


def test_update_item_project_id_validated(client):
    item = _create_item(client).json()
    company_project_id = _create_company_project(client)

    resp = client.put(f"/api/portfolio/{item['id']}", json={"project_id": company_project_id})
    assert resp.status_code == 400

    standalone_project_id = _create_standalone_project(client)
    resp = client.put(f"/api/portfolio/{item['id']}", json={"project_id": standalone_project_id})
    assert resp.status_code == 200
    assert resp.json()["project_id"] == standalone_project_id


def test_links_add_and_delete(client):
    item = _create_item(client).json()

    resp = client.post(
        f"/api/portfolio/{item['id']}/links", json={"label": "GitHub", "url": "https://github.com/example"}
    )
    assert resp.status_code == 200
    link = resp.json()

    detail = client.get(f"/api/portfolio/{item['id']}").json()
    assert [link_["label"] for link_ in detail["links"]] == ["GitHub"]

    resp = client.delete(f"/api/portfolio/links/{link['id']}")
    assert resp.status_code == 200
    detail = client.get(f"/api/portfolio/{item['id']}").json()
    assert detail["links"] == []


def test_upload_multiple_files_under_limit(client):
    item = _create_item(client).json()

    files = [
        ("files", ("a.pdf", b"pdf-bytes", "application/pdf")),
        ("files", ("b.png", b"png-bytes", "image/png")),
    ]
    resp = client.post(f"/api/portfolio/{item['id']}/files", files=files)
    assert resp.status_code == 200
    body = resp.json()
    assert {f["original_filename"] for f in body} == {"a.pdf", "b.png"}
    assert {f["size_bytes"] for f in body} == {len(b"pdf-bytes"), len(b"png-bytes")}


def test_upload_file_over_limit_rejects_whole_batch(client):
    item = _create_item(client).json()

    oversized = b"x" * (10 * 1024 * 1024 + 1)
    files = [
        ("files", ("small.pdf", b"ok", "application/pdf")),
        ("files", ("big.pdf", oversized, "application/pdf")),
    ]
    resp = client.post(f"/api/portfolio/{item['id']}/files", files=files)
    assert resp.status_code == 400

    detail = client.get(f"/api/portfolio/{item['id']}").json()
    assert detail["files"] == []


def test_upload_rejects_unsupported_extension(client):
    item = _create_item(client).json()

    files = [("files", ("script.exe", b"MZ", "application/octet-stream"))]
    resp = client.post(f"/api/portfolio/{item['id']}/files", files=files)
    assert resp.status_code == 400

    detail = client.get(f"/api/portfolio/{item['id']}").json()
    assert detail["files"] == []


def test_download_file_returns_original_content(client):
    item = _create_item(client).json()
    files = [("files", ("report.pdf", b"the-content", "application/pdf"))]
    uploaded = client.post(f"/api/portfolio/{item['id']}/files", files=files).json()[0]

    resp = client.get(f"/api/portfolio/files/{uploaded['id']}/download")
    assert resp.status_code == 200
    assert resp.content == b"the-content"
    assert "report.pdf" in resp.headers["content-disposition"]


def test_delete_file(client):
    item = _create_item(client).json()
    files = [("files", ("report.pdf", b"the-content", "application/pdf"))]
    uploaded = client.post(f"/api/portfolio/{item['id']}/files", files=files).json()[0]

    resp = client.delete(f"/api/portfolio/files/{uploaded['id']}")
    assert resp.status_code == 200

    detail = client.get(f"/api/portfolio/{item['id']}").json()
    assert detail["files"] == []


def test_delete_item_cascades_links_and_files_including_disk(client):
    item = _create_item(client).json()
    client.post(f"/api/portfolio/{item['id']}/links", json={"label": "X", "url": "https://x.com"})
    files = [("files", ("report.pdf", b"the-content", "application/pdf"))]
    uploaded = client.post(f"/api/portfolio/{item['id']}/files", files=files).json()[0]
    on_disk = Path(uploaded["file_path"])
    assert on_disk.exists()

    resp = client.delete(f"/api/portfolio/{item['id']}")
    assert resp.status_code == 200
    assert client.get("/api/portfolio").json() == []
    assert not on_disk.exists()


def test_backup_export_includes_portfolio_with_file_content(client):
    item = _create_item(client).json()
    client.post(f"/api/portfolio/{item['id']}/links", json={"label": "X", "url": "https://x.com"})
    client.post(
        f"/api/portfolio/{item['id']}/files",
        files=[("files", ("report.pdf", b"the-content", "application/pdf"))],
    )

    body = client.get("/api/backup/export").json()
    assert len(body["portfolio_items"]) == 1
    assert len(body["portfolio_links"]) == 1
    assert len(body["portfolio_files"]) == 1
    assert body["portfolio_files"][0]["file_content_base64"] is not None


def test_backup_import_remaps_project_and_item_ids(client):
    project_id = _create_standalone_project(client)
    item = _create_item(client, project_id=project_id).json()
    client.post(f"/api/portfolio/{item['id']}/links", json={"label": "X", "url": "https://x.com"})
    client.post(
        f"/api/portfolio/{item['id']}/files",
        files=[("files", ("report.pdf", b"the-content", "application/pdf"))],
    )

    backup = client.get("/api/backup/export").json()

    # Wipe and re-import into a fresh instance's state via the same session/engine.
    for portfolio_item in client.get("/api/portfolio").json():
        client.delete(f"/api/portfolio/{portfolio_item['id']}")
    for project in client.get("/api/profile/projects").json():
        client.delete(f"/api/profile/projects/{project['id']}")

    resp = client.post("/api/backup/import", json=backup)
    assert resp.status_code == 200
    counts = resp.json()
    assert counts["portfolio_items"] == 1
    assert counts["portfolio_links"] == 1
    assert counts["portfolio_files"] == 1

    imported_items = client.get("/api/portfolio").json()
    assert len(imported_items) == 1
    new_item_id = imported_items[0]["id"]
    assert new_item_id != item["id"]
    # project_id was remapped to a freshly created project, not the stale old id
    assert imported_items[0]["project_id"] != project_id

    detail = client.get(f"/api/portfolio/{new_item_id}").json()
    assert len(detail["links"]) == 1
    assert len(detail["files"]) == 1
