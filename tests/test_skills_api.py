def test_add_skill_creates_and_lists(client):
    resp = client.post("/api/skills", json={"name": "Python", "category": "技術"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "Python"

    resp = client.get("/api/skills")
    assert resp.status_code == 200
    names = [s["name"] for s in resp.json()]
    assert names == ["Python"]


def test_add_skill_is_case_insensitive_dedup(client):
    client.post("/api/skills", json={"name": "Python", "category": "技術"})
    client.post("/api/skills", json={"name": "python", "category": "技術"})

    resp = client.get("/api/skills")
    assert len(resp.json()) == 1


def test_update_skill_changes_name_and_category(client):
    created = client.post("/api/skills", json={"name": "Python", "category": "技術"}).json()

    resp = client.put(f"/api/skills/{created['id']}", json={"name": "Python3", "category": "言語"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "Python3"
    assert resp.json()["category"] == "言語"

    resp = client.get("/api/skills")
    assert resp.json()[0]["name"] == "Python3"
    assert resp.json()[0]["category"] == "言語"


def test_update_skill_rejects_name_colliding_with_another_skill(client):
    client.post("/api/skills", json={"name": "Python", "category": "技術"})
    other = client.post("/api/skills", json={"name": "Go", "category": "技術"}).json()

    resp = client.put(f"/api/skills/{other['id']}", json={"name": "python", "category": "技術"})
    assert resp.status_code == 400


def test_update_skill_missing_id_returns_404(client):
    resp = client.put("/api/skills/does-not-exist", json={"name": "X", "category": "Y"})
    assert resp.status_code == 404


def test_new_skill_has_no_proficiency_by_default(client):
    resp = client.post("/api/skills", json={"name": "Python", "category": "技術"})
    assert resp.json()["proficiency"] is None

    resp = client.get("/api/skills")
    assert resp.json()[0]["proficiency"] is None


def test_set_proficiency_on_create_and_update(client):
    created = client.post("/api/skills", json={"name": "Python", "category": "技術", "proficiency": 3}).json()
    assert created["proficiency"] == 3

    resp = client.put(f"/api/skills/{created['id']}", json={"name": "Python", "category": "技術", "proficiency": 5})
    assert resp.json()["proficiency"] == 5

    resp = client.get("/api/skills")
    assert resp.json()[0]["proficiency"] == 5


def test_proficiency_out_of_range_is_rejected(client):
    resp = client.post("/api/skills", json={"name": "Python", "category": "技術", "proficiency": 6})
    assert resp.status_code == 422

    resp = client.post("/api/skills", json={"name": "Go", "category": "技術", "proficiency": 0})
    assert resp.status_code == 422


def test_re_upserting_existing_skill_does_not_touch_proficiency(client):
    created = client.post("/api/skills", json={"name": "Python", "category": "技術", "proficiency": 4}).json()

    # Re-adding the same (case-insensitive) name matches the existing skill
    # and only bumps last_observed_at, the same as it already leaves
    # category untouched — proficiency must survive an unrelated auto-upsert.
    client.post("/api/skills", json={"name": "python", "category": "技術", "proficiency": 1})

    resp = client.get("/api/skills")
    assert len(resp.json()) == 1
    assert resp.json()[0]["proficiency"] == 4
    assert resp.json()[0]["id"] == created["id"]


def test_delete_skill(client):
    created = client.post("/api/skills", json={"name": "Python", "category": "技術"}).json()

    resp = client.delete(f"/api/skills/{created['id']}")
    assert resp.status_code == 200

    resp = client.get("/api/skills")
    assert resp.json() == []


def test_import_csv_creates_skills_and_dedupes_existing(client):
    client.post("/api/skills", json={"name": "Python", "category": "技術"})

    csv_content = "name,category\nPython,技術\nAWS,資格\n,無視される\n"
    files = {"file": ("skills.csv", csv_content, "text/csv")}
    resp = client.post("/api/skills/import-csv", files=files)

    assert resp.status_code == 200
    body = resp.json()
    assert len(body["imported"]) == 2  # Python(dedup) + AWS
    assert body["skipped_rows"] == 1  # empty name row

    resp = client.get("/api/skills")
    names = sorted(s["name"] for s in resp.json())
    assert names == ["AWS", "Python"]


def test_new_skill_defaults_to_included_in_resume(client):
    resp = client.post("/api/skills", json={"name": "Python", "category": "技術"})
    assert resp.json()["include_in_resume"] is True

    listed = client.get("/api/skills").json()
    assert listed[0]["include_in_resume"] is True


def test_toggle_skill_resume_inclusion(client):
    skill = client.post("/api/skills", json={"name": "Python", "category": "技術"}).json()

    resp = client.put(f"/api/skills/{skill['id']}/resume-inclusion", json={"include_in_resume": False})
    assert resp.status_code == 200
    assert resp.json()["include_in_resume"] is False

    listed = client.get("/api/skills").json()
    assert listed[0]["include_in_resume"] is False


def test_excluded_skill_is_omitted_from_resume(client):
    included = client.post("/api/skills", json={"name": "Python", "category": "技術"}).json()
    excluded = client.post("/api/skills", json={"name": "COBOL", "category": "技術"}).json()
    client.put(f"/api/skills/{excluded['id']}/resume-inclusion", json={"include_in_resume": False})

    content = client.post("/api/export").json()["content"]
    assert included["name"] in content
    assert excluded["name"] not in content
