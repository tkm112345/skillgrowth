def test_list_goals_returns_three_default_horizons(client):
    resp = client.get("/api/goals")
    assert resp.status_code == 200
    horizons = [g["horizon"] for g in resp.json()]
    assert horizons == ["this_year", "5_years", "10_years"]
    assert all(g["description"] == "" for g in resp.json())
    assert all(g["updated_at"] is None for g in resp.json())
    assert all(g["include_in_resume"] is False for g in resp.json())


def test_resume_inclusion_defaults_off_and_can_be_toggled_per_horizon(client):
    resp = client.put("/api/goals/this_year/resume-inclusion", json={"include_in_resume": True})
    assert resp.status_code == 200
    assert resp.json()["include_in_resume"] is True

    goals = {g["horizon"]: g for g in client.get("/api/goals").json()}
    assert goals["this_year"]["include_in_resume"] is True
    assert goals["5_years"]["include_in_resume"] is False


def test_resume_inclusion_toggle_rejects_horizon_outside_the_fixed_set(client):
    resp = client.put("/api/goals/not-a-real-horizon/resume-inclusion", json={"include_in_resume": True})
    assert resp.status_code == 400


def test_resume_inclusion_toggle_does_not_create_history(client):
    client.put("/api/goals/this_year", json={"horizon": "this_year", "description": "AWS認定を取る"})
    client.put("/api/goals/this_year/resume-inclusion", json={"include_in_resume": True})

    history = [h for h in client.get("/api/goals/history").json() if h["horizon"] == "this_year"]
    assert len(history) == 1  # only the description PUT above recorded history


def test_list_goals_returns_real_timestamp_only_for_saved_horizon(client):
    client.put("/api/goals/this_year", json={"horizon": "this_year", "description": "AWS認定を取る"})
    goals = {g["horizon"]: g for g in client.get("/api/goals").json()}
    assert goals["this_year"]["updated_at"] is not None
    assert goals["5_years"]["updated_at"] is None


def test_update_goal_persists_description(client):
    resp = client.put("/api/goals/this_year", json={"horizon": "this_year", "description": "AWS認定を取る"})
    assert resp.status_code == 200
    assert resp.json()["description"] == "AWS認定を取る"

    resp = client.get("/api/goals")
    updated = next(g for g in resp.json() if g["horizon"] == "this_year")
    assert updated["description"] == "AWS認定を取る"


def test_update_goal_rejects_horizon_outside_the_fixed_set(client):
    """CareerGoal.horizon is keyed/looked up everywhere else (list_goals,
    build_consult_context) against the fixed 3-value HORIZONS set — an
    arbitrary value here would create a row nothing ever displays or reads,
    just a permanent orphan."""
    resp = client.put("/api/goals/not-a-real-horizon", json={"horizon": "not-a-real-horizon", "description": "x"})
    assert resp.status_code == 400

    resp = client.get("/api/goals")
    assert [g["horizon"] for g in resp.json()] == ["this_year", "5_years", "10_years"]


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
