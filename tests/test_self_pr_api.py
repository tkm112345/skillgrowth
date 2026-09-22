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


def test_list_self_pr_supports_pagination(client):
    for i in range(7):
        client.post("/api/self-pr", json={"content": f"draft {i}"})

    page1 = client.get("/api/self-pr", params={"limit": 5}).json()
    assert [e["content"] for e in page1] == [f"draft {i}" for i in [6, 5, 4, 3, 2]]

    page2 = client.get("/api/self-pr", params={"limit": 5, "offset": 5}).json()
    assert [e["content"] for e in page2] == ["draft 1", "draft 0"]


def test_resume_uses_latest_self_pr(client):
    client.post("/api/self-pr", json={"content": "old pitch"})
    client.post("/api/self-pr", json={"content": "current pitch"})

    resp = client.post("/api/export")
    assert resp.status_code == 200
    content = resp.json()["content"]
    assert "current pitch" in content
    assert "old pitch" not in content
