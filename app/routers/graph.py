from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session, select

from app.db import get_session
from app.models import Education, Employment, LearningActivity, PortfolioItem, Project, Skill, SkillLink

router = APIRouter(prefix="/api/graph", tags=["graph"])


class GraphNode(BaseModel):
    id: str
    type: str
    label: str
    category: str | None = None


class GraphEdge(BaseModel):
    source: str
    target: str


class GraphData(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


@router.get("")
def get_graph(session: Session = Depends(get_session)) -> GraphData:
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []
    # evidence_id -> node id, so the SkillLink pass below only draws an edge
    # to entities actually included in this graph (certifications, not every
    # LearningActivity — the activity log is append-only and grows forever,
    # so unlike Skill/Education/Employment/Project/PortfolioItem it can't be
    # shown in full without the graph becoming an unreadable, ever-growing
    # tangle; see docs/ARCHITECTURE.md).
    evidence_to_node: dict[str, str] = {}

    for skill in session.exec(select(Skill)).all():
        nodes.append(GraphNode(id=f"skill:{skill.id}", type="skill", label=skill.name, category=skill.category))

    for cert in session.exec(select(LearningActivity).where(LearningActivity.activity_type == "certification")).all():
        node_id = f"learning_activity:{cert.id}"
        nodes.append(GraphNode(id=node_id, type="learning_activity", label=cert.title))
        if cert.evidence_id:
            evidence_to_node[cert.evidence_id] = node_id

    for edu in session.exec(select(Education)).all():
        node_id = f"education:{edu.id}"
        nodes.append(GraphNode(id=node_id, type="education", label=edu.school))
        if edu.evidence_id:
            evidence_to_node[edu.evidence_id] = node_id

    for emp in session.exec(select(Employment)).all():
        node_id = f"employment:{emp.id}"
        nodes.append(GraphNode(id=node_id, type="employment", label=emp.company))
        if emp.evidence_id:
            evidence_to_node[emp.evidence_id] = node_id

    project_node_id: dict[str, str] = {}
    for project in session.exec(select(Project)).all():
        node_id = f"project:{project.id}"
        nodes.append(GraphNode(id=node_id, type="project", label=project.title))
        project_node_id[project.id] = node_id
        if project.evidence_id:
            evidence_to_node[project.evidence_id] = node_id
        if project.employment_id:
            edges.append(GraphEdge(source=f"employment:{project.employment_id}", target=node_id))

    for item in session.exec(select(PortfolioItem)).all():
        node_id = f"portfolio_item:{item.id}"
        nodes.append(GraphNode(id=node_id, type="portfolio_item", label=item.title))
        if item.project_id and item.project_id in project_node_id:
            edges.append(GraphEdge(source=project_node_id[item.project_id], target=node_id))

    seen_edges: set[tuple[str, str]] = set()
    for skill_id, evidence_id in session.exec(select(SkillLink.skill_id, SkillLink.evidence_id)).all():
        target_node = evidence_to_node.get(evidence_id)
        if target_node is None:
            continue
        key = (skill_id, target_node)
        if key in seen_edges:
            continue
        seen_edges.add(key)
        edges.append(GraphEdge(source=f"skill:{skill_id}", target=target_node))

    return GraphData(nodes=nodes, edges=edges)
