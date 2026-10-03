def test_update_education_changes_fields_in_place(client):
    created = client.post("/api/profile/education", json={"school": "Old U", "degree": "B.S.", "major": "CS"}).json()[
        "education"
    ]

    resp = client.put(
        f"/api/profile/education/{created['id']}",
        json={"school": "New U", "degree": "M.S.", "major": "EE", "achievements": "Dean's list"},
    )
    assert resp.status_code == 200
    assert resp.json()["school"] == "New U"
    assert resp.json()["achievements"] == "Dean's list"

    listed = client.get("/api/profile/education").json()
    assert listed[0]["school"] == "New U"


def test_update_education_missing_id_returns_404(client):
    resp = client.put("/api/profile/education/does-not-exist", json={"school": "X"})
    assert resp.status_code == 404


def test_update_employment_changes_fields_in_place(client):
    created = client.post("/api/profile/employment", json={"company": "Old Co", "role": "Eng"}).json()["employment"]

    resp = client.put(f"/api/profile/employment/{created['id']}", json={"company": "New Co", "role": "Lead"})
    assert resp.status_code == 200
    assert resp.json()["company"] == "New Co"
    assert resp.json()["role"] == "Lead"


def test_update_employment_missing_id_returns_404(client):
    resp = client.put("/api/profile/employment/does-not-exist", json={"company": "X"})
    assert resp.status_code == 404


def test_update_project_changes_fields_and_relinks_employment(client):
    emp = client.post("/api/profile/employment", json={"company": "Acme"}).json()["employment"]
    created = client.post("/api/profile/projects", json={"title": "Old title", "employment_id": None}).json()["project"]
    assert created["employment_id"] is None

    resp = client.put(
        f"/api/profile/projects/{created['id']}",
        json={"title": "New title", "employment_id": emp["id"]},
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "New title"
    assert resp.json()["employment_id"] == emp["id"]


def test_update_project_missing_id_returns_404(client):
    resp = client.put("/api/profile/projects/does-not-exist", json={"title": "X"})
    assert resp.status_code == 404
