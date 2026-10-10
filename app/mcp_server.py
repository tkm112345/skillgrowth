import os

from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

ENV_ENABLED = "SKILLGROWTH_MCP_ENABLED"

# Read-only + add/update operations only — no DELETE, no Settings/backup
# (secrets, full data export/import/reset), no LLM-only endpoints
# (ai.py/consult.py/evidence.py/resume_import.py), no multipart file
# uploads (CSV import, certificate/photo/portfolio-file/template uploads).
# Each operation_id here is set explicitly on its route (see the routers
# below) rather than left to FastAPI's auto-generated id, matching
# fastapi-mcp's own naming recommendation.
MCP_OPERATIONS = [
    # app/routers/learning.py
    "list_learning_activities",
    "add_learning_activity",
    "update_learning_activity",
    "list_activity_types",
    "add_activity_type",
    # app/routers/planned_certifications.py
    "list_planned_certifications",
    "add_planned_certification",
    "update_planned_certification",
    "promote_planned_certification",
    # app/routers/bookmarks.py
    "list_bookmarks",
    "add_bookmark",
    "update_bookmark",
    # app/routers/skills.py
    "list_skills",
    "add_skill",
    "update_skill",
    "get_skill_action_counts",
    "get_skill_detail",
    # app/routers/profile.py
    "list_education",
    "add_education",
    "update_education",
    "list_employment",
    "add_employment",
    "update_employment",
    "list_projects",
    "add_project",
    "update_project",
    "list_profile_links",
    "add_profile_link",
    # app/routers/portfolio.py
    "list_portfolio_items",
    "get_portfolio_item",
    "add_portfolio_item",
    "update_portfolio_item",
    "add_portfolio_link",
    # app/routers/self_feedback.py
    "list_self_feedback",
    "add_self_feedback",
    "update_self_feedback",
    # app/routers/self_pr.py
    "list_self_pr",
    "add_self_pr",
    "update_self_pr",
    "select_self_pr",
    # app/routers/goals.py
    "list_goals",
    "update_goal",
    "set_goal_resume_inclusion",
    "list_goal_history",
    # app/routers/vision.py
    "get_vision",
    "update_vision",
    "set_vision_resume_inclusion",
]


def setup_mcp(app: FastAPI) -> None:
    if os.environ.get(ENV_ENABLED) not in ("1", "true", "True"):
        return  # gate disabled by default — unset means no /mcp endpoint at all

    mcp = FastApiMCP(app, name="skillgrowth", include_operations=MCP_OPERATIONS)
    mcp.mount_http()
