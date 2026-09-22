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


def test_update_self_pr_edits_content_in_place(client):
    entry = client.post("/api/self-pr", json={"content": "draft"}).json()

    resp = client.put(f"/api/self-pr/{entry['id']}", json={"content": "fixed a typo"})
    assert resp.status_code == 200
    assert resp.json()["content"] == "fixed a typo"
    assert resp.json()["id"] == entry["id"]

    listed = client.get("/api/self-pr").json()
    assert listed[0]["content"] == "fixed a typo"


def test_new_self_pr_is_auto_selected_and_only_one_is_selected_at_a_time(client):
    first = client.post("/api/self-pr", json={"content": "old pitch"}).json()
    second = client.post("/api/self-pr", json={"content": "current pitch"}).json()

    entries = {e["id"]: e for e in client.get("/api/self-pr").json()}
    assert entries[first["id"]]["is_selected"] is False
    assert entries[second["id"]]["is_selected"] is True


def test_selecting_an_older_self_pr_changes_what_the_resume_uses(client):
    old = client.post("/api/self-pr", json={"content": "old pitch"}).json()
    client.post("/api/self-pr", json={"content": "current pitch"})

    resp = client.put(f"/api/self-pr/{old['id']}/select")
    assert resp.status_code == 200
    assert resp.json()["is_selected"] is True

    entries = {e["id"]: e for e in client.get("/api/self-pr").json()}
    assert entries[old["id"]]["is_selected"] is True

    content = client.post("/api/export").json()["content"]
    assert "old pitch" in content
    assert "current pitch" not in content
