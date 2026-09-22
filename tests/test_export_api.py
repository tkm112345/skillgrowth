def test_update_export_edits_content_in_place(client):
    snapshot = client.post("/api/export").json()
    assert snapshot["edited_at"] is None

    resp = client.put(f"/api/export/{snapshot['id']}", json={"content": "# Resume\n\nHand-edited."})
    assert resp.status_code == 200
    body = resp.json()
    assert body["content"] == "# Resume\n\nHand-edited."
    assert body["edited_at"] is not None
    assert body["id"] == snapshot["id"]

    listed = client.get("/api/export").json()
    assert listed[0]["content"] == "# Resume\n\nHand-edited."


def test_update_export_missing_id_returns_404(client):
    resp = client.put("/api/export/does-not-exist", json={"content": "x"})
    assert resp.status_code == 404
