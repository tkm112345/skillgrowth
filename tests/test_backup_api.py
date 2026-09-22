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
        "career_goal_history",
        "career_vision",
        "education",
        "employment",
        "projects",
        "learning_activities",
        "external_links",
        "resume_exports",
        "self_prs",
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


def test_import_round_trip_preserves_data_and_links(client):
    client.post("/api/skills", json={"name": "Python", "category": "技術"})
    exported = client.get("/api/backup/export").json()

    imported = client.post("/api/backup/import", json=exported)
    assert imported.status_code == 200
    assert imported.json()["skills"] == 1

    skills = client.get("/api/skills").json()
    assert len(skills) == 2
    assert sorted(s["name"] for s in skills) == ["Python", "Python"]


def test_import_remaps_employment_and_evidence_foreign_keys(client):
    payload = {
        "evidence": [
            {
                "id": "old-ev-1",
                "source_type": "employment",
                "raw_input": "Worked at Acme",
                "file_path": None,
                "created_at": "2025-01-01T00:00:00+00:00",
            }
        ],
        "skills": [],
        "skill_links": [],
        "career_goals": [],
        "education": [],
        "employment": [
            {
                "id": "old-emp-1",
                "company": "Acme",
                "department": "",
                "role": "Engineer",
                "start_date": "2020-01-01",
                "end_date": None,
                "evidence_id": "old-ev-1",
            }
        ],
        "projects": [
            {
                "id": "old-proj-1",
                "employment_id": "old-emp-1",
                "title": "Widget launch",
                "role": "Lead",
                "start_date": None,
                "end_date": None,
                "description": "",
                "evidence_id": None,
            }
        ],
        "learning_activities": [],
        "external_links": [],
        "resume_exports": [],
    }

    resp = client.post("/api/backup/import", json=payload)
    assert resp.status_code == 200
    assert resp.json() == {
        "evidence": 1,
        "skills": 0,
        "skill_links": 0,
        "employment": 1,
        "education": 0,
        "projects": 1,
        "learning_activities": 0,
        "external_links": 0,
        "career_goals": 0,
        "career_goal_history": 0,
        "career_vision": 0,
        "resume_exports": 0,
        "self_prs": 0,
    }

    employment = client.get("/api/profile/employment").json()
    projects = client.get("/api/profile/projects").json()
    assert employment[0]["company"] == "Acme"
    assert projects[0]["employment_id"] == employment[0]["id"]  # remapped, not the old id
    assert employment[0]["evidence_id"] is not None
    assert employment[0]["evidence_id"] != "old-ev-1"  # remapped, not the old id


def test_import_career_goal_fills_only_when_empty(client):
    client.put("/api/goals/this_year", json={"horizon": "this_year", "description": "既に書いた目標"})

    payload = {
        "evidence": [], "skills": [], "skill_links": [], "education": [], "employment": [],
        "projects": [], "learning_activities": [], "external_links": [], "resume_exports": [],
        "career_goals": [
            {"horizon": "this_year", "description": "サンプルの目標"},
            {"horizon": "5_years", "description": "サンプルの5年後目標"},
        ],
    }
    resp = client.post("/api/backup/import", json=payload)
    assert resp.status_code == 200
    assert resp.json()["career_goals"] == 1  # only 5_years was empty and got filled

    goals = {g["horizon"]: g["description"] for g in client.get("/api/goals").json()}
    assert goals["this_year"] == "既に書いた目標"  # not overwritten
    assert goals["5_years"] == "サンプルの5年後目標"


def test_import_career_vision_fills_only_when_empty(client):
    client.put("/api/vision", json={"content": "既に書いたビジョン"})

    payload = {
        "evidence": [], "skills": [], "skill_links": [], "education": [], "employment": [],
        "projects": [], "learning_activities": [], "external_links": [], "resume_exports": [],
        "career_vision": [{"content": "サンプルのビジョン"}],
    }
    resp = client.post("/api/backup/import", json=payload)
    assert resp.status_code == 200
    assert resp.json()["career_vision"] == 0  # already had content, so nothing was filled
    assert client.get("/api/vision").json()["content"] == "既に書いたビジョン"


def test_load_sample_data_populates_expected_counts(client):
    resp = client.post("/api/backup/load-sample")
    assert resp.status_code == 200
    body = resp.json()
    assert body["evidence"] == 16
    assert body["skills"] == 17
    assert body["employment"] == 2
    assert body["career_goals"] == 3
    assert body["career_vision"] == 1
    assert body["projects"] == 4
    assert body["self_prs"] == 1

    skills = client.get("/api/skills").json()
    assert any(s["name"] == "Python" for s in skills)


def test_reset_sample_removes_only_sample_rows(client):
    client.post("/api/skills", json={"name": "MyRealSkill", "category": "技術"})
    client.post("/api/backup/load-sample")

    resp = client.post("/api/backup/reset-sample")
    assert resp.status_code == 200

    skills = client.get("/api/skills").json()
    assert [s["name"] for s in skills] == ["MyRealSkill"]
    assert client.get("/api/evidence").json() == []
    assert client.get("/api/profile/employment").json() == []

    goals = {g["horizon"]: g["description"] for g in client.get("/api/goals").json()}
    assert all(desc == "" for desc in goals.values())


def test_reset_sample_does_not_touch_goal_user_already_wrote(client):
    client.put("/api/goals/this_year", json={"horizon": "this_year", "description": "自分の目標"})
    client.post("/api/backup/load-sample")

    client.post("/api/backup/reset-sample")

    goals = {g["horizon"]: g["description"] for g in client.get("/api/goals").json()}
    assert goals["this_year"] == "自分の目標"  # this_year was never filled by sample, so untouched
    assert goals["5_years"] == ""


def test_reset_sample_is_idempotent(client):
    client.post("/api/backup/load-sample")
    client.post("/api/backup/reset-sample")

    resp = client.post("/api/backup/reset-sample")
    assert resp.status_code == 200
    assert client.get("/api/skills").json() == []
