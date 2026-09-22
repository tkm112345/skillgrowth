def test_growth_guidance_skips_llm_when_no_goals_set(client):
    resp = client.post("/api/ai/growth-guidance")
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

    resp = client.post("/api/ai/growth-guidance")
    assert resp.status_code == 200
    assert len(seen_goals) == 1
    assert seen_goals[0]["horizon"] == "this_year"
    assert resp.json()["by_horizon"] == [{"horizon": "今年", "advice": "advice"}]


def test_gap_check_calls_llm_with_current_skills(client, monkeypatch):
    from app import llm

    client.post("/api/skills", json={"name": "Python", "category": "技術"})

    seen = {}

    def fake_gap_check(job_description, current_skills, settings):
        seen["job_description"] = job_description
        seen["current_skills"] = current_skills
        return {"matched": ["Python"], "missing": ["Go"], "summary": "good fit"}

    monkeypatch.setattr(llm, "gap_check", fake_gap_check)

    resp = client.post("/api/ai/gap-check", json={"job_description": "Need a Python and Go engineer"})
    assert resp.status_code == 200
    assert resp.json() == {"matched": ["Python"], "missing": ["Go"], "summary": "good fit"}
    assert seen["job_description"] == "Need a Python and Go engineer"
    assert seen["current_skills"] == [{"name": "Python", "category": "技術"}]
