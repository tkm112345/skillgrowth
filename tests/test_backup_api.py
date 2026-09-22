def test_export_backup_returns_all_sections_when_empty(client):
    resp = client.get("/api/backup/export")
    assert resp.status_code == 200
    body = resp.json()
    assert "exported_at" in body
    for key in [
        "evidence",
        "skills",
        "skill_links",
        "career_goals",
        "education",
        "employment",
        "projects",
        "learning_activities",
        "external_links",
        "resume_exports",
    ]:
        assert body[key] == []


def test_export_backup_includes_created_records(client):
    client.post("/api/skills", json={"name": "Python", "category": "技術"})
    client.post("/api/profile/links", json={"label": "GitHub", "url": "https://github.com/example"})

    resp = client.get("/api/backup/export")
    body = resp.json()
    assert len(body["skills"]) == 1
    assert body["skills"][0]["name"] == "Python"
    assert len(body["external_links"]) == 1


def test_export_backup_does_not_include_settings(client):
    resp = client.get("/api/backup/export")
    assert "settings" not in resp.json()
