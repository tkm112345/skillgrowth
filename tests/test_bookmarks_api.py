def test_add_bookmark_creates_and_lists(client):
    resp = client.post(
        "/api/bookmarks", json={"url": "https://zenn.dev/example", "title": "Example article", "memo": "good read"}
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Example article"

    resp = client.get("/api/bookmarks")
    assert [b["title"] for b in resp.json()] == ["Example article"]


def test_add_bookmark_requires_url_and_title(client):
    resp = client.post("/api/bookmarks", json={"url": "", "title": "Example"})
    assert resp.status_code == 400

    resp = client.post("/api/bookmarks", json={"url": "https://example.com", "title": ""})
    assert resp.status_code == 400


def test_update_bookmark(client):
    created = client.post("/api/bookmarks", json={"url": "https://example.com", "title": "Old"}).json()

    resp = client.put(
        f"/api/bookmarks/{created['id']}",
        json={"url": "https://example.com/new", "title": "New", "memo": "updated"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["title"] == "New"
    assert body["url"] == "https://example.com/new"
    assert body["memo"] == "updated"


def test_update_bookmark_missing_id_returns_404(client):
    resp = client.put("/api/bookmarks/does-not-exist", json={"url": "https://example.com", "title": "X"})
    assert resp.status_code == 404


def test_delete_bookmark(client):
    created = client.post("/api/bookmarks", json={"url": "https://example.com", "title": "X"}).json()

    resp = client.delete(f"/api/bookmarks/{created['id']}")
    assert resp.status_code == 200

    assert client.get("/api/bookmarks").json() == []
