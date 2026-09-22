def test_add_self_pr_and_list_newest_first(client):
    client.post("/api/self-pr", json={"content": "first draft"})
    client.post("/api/self-pr", json={"content": "revised draft"})

    resp = client.get("/api/self-pr")
    assert resp.status_code == 200
    contents = [e["content"] for e in resp.json()]
    assert contents == ["revised draft", "first draft"]


def test_delete_self_pr(client):
    created = client.post("/api/self-pr", json={"content": "draft"}).json()

    resp = client.delete(f"/api/self-pr/{created['id']}")
    assert resp.status_code == 200
    assert client.get("/api/self-pr").json() == []


def test_resume_uses_latest_self_pr(client):
    client.post("/api/self-pr", json={"content": "old pitch"})
    client.post("/api/self-pr", json={"content": "current pitch"})

    resp = client.post("/api/export")
    assert resp.status_code == 200
    content = resp.json()["content"]
    assert "current pitch" in content
    assert "old pitch" not in content
