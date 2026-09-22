def test_list_goals_returns_three_default_horizons(client):
    resp = client.get("/api/goals")
    assert resp.status_code == 200
    horizons = [g["horizon"] for g in resp.json()]
    assert horizons == ["this_year", "5_years", "10_years"]
    assert all(g["description"] == "" for g in resp.json())


def test_update_goal_persists_description(client):
    resp = client.put("/api/goals/this_year", json={"horizon": "this_year", "description": "AWS認定を取る"})
    assert resp.status_code == 200
    assert resp.json()["description"] == "AWS認定を取る"

    resp = client.get("/api/goals")
    updated = next(g for g in resp.json() if g["horizon"] == "this_year")
    assert updated["description"] == "AWS認定を取る"


def test_update_goal_records_history_only_on_actual_change(client):
    client.put("/api/goals/this_year", json={"horizon": "this_year", "description": "AWS認定を取る"})
    client.put("/api/goals/this_year", json={"horizon": "this_year", "description": "AWS認定を取る"})
    client.put("/api/goals/this_year", json={"horizon": "this_year", "description": "AWS認定+登壇"})

    history = client.get("/api/goals/history").json()
    this_year_history = [h for h in history if h["horizon"] == "this_year"]
    assert [h["description"] for h in this_year_history] == ["AWS認定+登壇", "AWS認定を取る"]
