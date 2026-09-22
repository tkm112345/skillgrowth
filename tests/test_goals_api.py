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


def test_goal_history_supports_horizon_filter_and_pagination(client):
    for i in range(7):
        client.put("/api/goals/this_year", json={"horizon": "this_year", "description": f"v{i}"})
    client.put("/api/goals/5_years", json={"horizon": "5_years", "description": "別の目標"})

    resp = client.get("/api/goals/history", params={"horizon": "this_year", "limit": 5})
    assert resp.status_code == 200
    page1 = resp.json()
    assert len(page1) == 5
    assert [h["horizon"] for h in page1] == ["this_year"] * 5
    assert page1[0]["description"] == "v6"  # newest first

    page2 = client.get("/api/goals/history", params={"horizon": "this_year", "limit": 5, "offset": 5}).json()
    assert [h["description"] for h in page2] == ["v1", "v0"]
