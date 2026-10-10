def test_get_personal_values_returns_empty_default_when_unset(client):
    resp = client.get("/api/personal-values")
    assert resp.status_code == 200
    assert resp.json()["content"] == ""
    assert resp.json()["updated_at"] is None
    assert resp.json()["include_in_resume"] is True


def test_update_personal_values_persists_and_overwrites_in_place(client):
    resp = client.put("/api/personal-values", json={"content": "世界をちょっとだけ良くしたい"})
    assert resp.status_code == 200
    assert resp.json()["content"] == "世界をちょっとだけ良くしたい"

    resp = client.put("/api/personal-values", json={"content": "透明性と越境とリスペクト"})
    assert resp.json()["content"] == "透明性と越境とリスペクト"

    resp = client.get("/api/personal-values")
    assert resp.json()["content"] == "透明性と越境とリスペクト"


def test_resume_inclusion_defaults_true_and_can_be_toggled_off(client):
    resp = client.put("/api/personal-values/resume-inclusion", json={"include_in_resume": False})
    assert resp.status_code == 200
    assert resp.json()["include_in_resume"] is False
    assert client.get("/api/personal-values").json()["include_in_resume"] is False

    client.put("/api/personal-values/resume-inclusion", json={"include_in_resume": True})
    assert client.get("/api/personal-values").json()["include_in_resume"] is True
