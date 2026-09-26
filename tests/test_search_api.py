def test_search_finds_skill_activity_and_portfolio(client):
    client.post("/api/skills", json={"name": "Kubernetes", "category": "インフラ"})
    client.post("/api/learning", json={"activity_type": "Reading", "title": "Kubernetes patterns", "notes": ""})
    client.post("/api/portfolio", json={"title": "Kubernetes operator", "description": ""})

    resp = client.get("/api/search", params={"q": "Kubernetes"})
    assert resp.status_code == 200
    results = resp.json()
    entity_types = {r["entity_type"] for r in results}
    assert entity_types == {"skill", "learning_activity", "portfolio_item"}


def test_search_matches_body_field(client):
    client.post("/api/skills", json={"name": "Python", "category": "バックエンド言語"})

    resp = client.get("/api/search", params={"q": "バックエンド"})
    assert resp.status_code == 200
    assert any(r["title"] == "Python" for r in resp.json())


def test_deleted_skill_is_removed_from_search(client):
    skill = client.post("/api/skills", json={"name": "Rust", "category": "技術"}).json()

    assert len(client.get("/api/search", params={"q": "Rust"}).json()) == 1

    client.delete(f"/api/skills/{skill['id']}")

    assert client.get("/api/search", params={"q": "Rust"}).json() == []


def test_updated_skill_reflects_new_name_in_search(client):
    skill = client.post("/api/skills", json={"name": "Elixir", "category": "技術"}).json()

    client.put(f"/api/skills/{skill['id']}", json={"name": "Golang", "category": "技術"})

    assert client.get("/api/search", params={"q": "Elixir"}).json() == []
    assert len(client.get("/api/search", params={"q": "Golang"}).json()) == 1


def test_short_query_returns_empty(client):
    client.post("/api/skills", json={"name": "Java", "category": "技術"})
    assert client.get("/api/search", params={"q": "J"}).json() == []
    assert client.get("/api/search", params={"q": ""}).json() == []
