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


def test_growth_guidance_skips_llm_when_no_goals_set(client):
    resp = client.post("/api/goals/growth-guidance")
    assert resp.status_code == 200
    assert resp.json() == {"by_horizon": []}


def test_growth_guidance_calls_llm_only_for_goals_with_description(client, monkeypatch):
    from app import llm

    seen_goals = []

    def fake_guidance(goals, current_skills, settings):
        seen_goals.extend(goals)
        return {"by_horizon": [{"horizon": g["horizon_label"], "advice": "advice"} for g in goals]}

    monkeypatch.setattr(llm, "goal_growth_guidance", fake_guidance)

    client.put("/api/goals/this_year", json={"horizon": "this_year", "description": "AWS認定を取る"})

    resp = client.post("/api/goals/growth-guidance")
    assert resp.status_code == 200
    assert len(seen_goals) == 1
    assert seen_goals[0]["horizon"] == "this_year"
    assert resp.json()["by_horizon"] == [{"horizon": "今年", "advice": "advice"}]
