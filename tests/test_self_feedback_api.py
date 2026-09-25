def test_add_and_list_self_feedback(client):
    resp = client.post(
        "/api/self-feedback",
        json={
            "entry_date": "2026-09-20",
            "accomplishments": "Shipped the jump-to-month feature",
            "reflection": "Took longer than expected to get the tests right",
            "next_steps": "Write the test first next time",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["entry_date"] == "2026-09-20"
    assert body["accomplishments"] == "Shipped the jump-to-month feature"

    entries = client.get("/api/self-feedback").json()
    assert len(entries) == 1
    assert entries[0]["reflection"] == "Took longer than expected to get the tests right"


def test_list_self_feedback_orders_by_entry_date_desc_and_paginates(client):
    for d in ["2026-09-01", "2026-09-15", "2026-09-10"]:
        client.post("/api/self-feedback", json={"entry_date": d})

    entries = client.get("/api/self-feedback?limit=2&offset=0").json()
    assert [e["entry_date"] for e in entries] == ["2026-09-15", "2026-09-10"]

    entries = client.get("/api/self-feedback?limit=2&offset=2").json()
    assert [e["entry_date"] for e in entries] == ["2026-09-01"]


def test_update_self_feedback(client):
    created = client.post("/api/self-feedback", json={"entry_date": "2026-09-01", "accomplishments": "draft"}).json()

    resp = client.put(
        f"/api/self-feedback/{created['id']}",
        json={"entry_date": "2026-09-02", "accomplishments": "revised", "reflection": "", "next_steps": ""},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["entry_date"] == "2026-09-02"
    assert body["accomplishments"] == "revised"
    assert body["updated_at"] != body["created_at"]


def test_update_missing_self_feedback_returns_404(client):
    resp = client.put("/api/self-feedback/does-not-exist", json={"entry_date": "2026-09-01"})
    assert resp.status_code == 404


def test_delete_self_feedback(client):
    created = client.post("/api/self-feedback", json={"entry_date": "2026-09-01"}).json()

    resp = client.delete(f"/api/self-feedback/{created['id']}")
    assert resp.status_code == 200

    assert client.get("/api/self-feedback").json() == []
