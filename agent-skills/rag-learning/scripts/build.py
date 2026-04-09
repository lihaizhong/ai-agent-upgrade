"""
RAG Learning 实战中心。
围绕最小 RAG 项目提供结构化步骤面板。
"""

from __future__ import annotations

from pathlib import Path

if __package__ in {None, ""}:
    from catalog import load_scenarios
    from state import RagLearningStateStore
else:
    from .catalog import load_scenarios
    from .state import RagLearningStateStore

PROJECT_OVERRIDES = {
    "local-minimum-rag": {
        "name": "本地最小 RAG",
        "status": "active",
        "description": "从文档导入到基础评估，完成一个本地可运行 RAG。",
    },
    "customer-support-rag": {
        "name": "客服机器人 RAG",
        "status": "planned",
        "description": "面向多轮问答与帮助中心知识库的对话系统。",
    },
    "enterprise-knowledge-search": {
        "name": "企业知识库搜索",
        "status": "planned",
        "description": "面向企业文档搜索、过滤和权限隔离场景。",
    },
}


STEP_PANELS = {
    "scenario": {
        "current_decision": "明确当前场景与成功标准",
        "recommendation": "先以单一文档问答场景启动，成功标准定义为“能检索到正确片段并给出带引用回答”。",
        "tradeoff": "先收窄场景可以降低变量数量，代价是短期内不覆盖复杂对话与权限问题。",
        "task": "选定一份文档语料，并写下 3 个你希望系统能回答的问题。",
        "next_step": "chunking",
        "competency_area": "rag_foundations",
    },
    "chunking": {
        "current_decision": "确定分块策略",
        "recommendation": "先用递归字符分块或结构化分块，保持段落语义完整。",
        "tradeoff": "固定分块更简单，但更容易打断语义；语义更完整的分块更稳，但实现稍复杂。",
        "task": "用一份样本文档切出 5 到 10 个 chunk，检查是否保留了可读语义边界。",
        "next_step": "embedding",
        "competency_area": "retrieval_design",
    },
    "embedding": {
        "current_decision": "选择 embedding 模型",
        "recommendation": "中文优先可从 `bge-m3` 起步；如果优先云服务和简单接入，可从 `text-embedding-3-small` 起步。",
        "tradeoff": "开源模型更适合本地和中文语料，商业 API 接入更简单但受成本和外部依赖约束。",
        "task": "根据你的语料语言和部署偏好，在两个候选中选一个作为默认 embedding。",
        "next_step": "vector_db",
        "competency_area": "embedding_selection",
    },
    "vector_db": {
        "current_decision": "选择向量数据库",
        "recommendation": "本地最小 RAG 先用 Chroma 或 Qdrant，本轮默认推荐 Qdrant 以保留后续过滤扩展空间。",
        "tradeoff": "Chroma 更轻量，Qdrant 更接近生产路径；前者更快起步，后者更利于后续迁移。",
        "task": "确定本轮是 `chroma` 还是 `qdrant`，并说明理由只基于当前场景，不提前为企业级过度设计。",
        "next_step": "retrieval",
        "competency_area": "vector_db_selection",
    },
    "retrieval": {
        "current_decision": "确定基础检索方式",
        "recommendation": "先用向量检索 Top-K 起步，把元数据和 hybrid search 留到第二轮优化。",
        "tradeoff": "先做纯向量检索能更快验证主流程，但对关键词强约束场景不一定足够。",
        "task": "定义默认 top-k，并准备 3 个问题验证召回是否合理。",
        "next_step": "rerank",
        "competency_area": "retrieval_design",
    },
    "rerank": {
        "current_decision": "判断当前阶段是否需要 rerank",
        "recommendation": "默认先不加 rerank，只有当基础召回能找到相关片段但排序不稳定时再引入。",
        "tradeoff": "不加 rerank 更省成本更低延迟，但排序精度可能不足；过早引入会增加复杂度。",
        "task": "先用基础检索结果做一次人工抽样判断，再决定是否进入 rerank 实验。",
        "next_step": "generation",
        "competency_area": "rerank_decision",
    },
    "generation": {
        "current_decision": "设计回答生成与引用策略",
        "recommendation": "回答中要求引用来源片段，并限制只基于检索上下文作答。",
        "tradeoff": "更严格的引用要求能减少幻觉，但回答可能更保守。",
        "task": "定义回答模板，至少包含结论、依据片段和无法回答时的兜底说法。",
        "next_step": "evaluation",
        "competency_area": "rag_foundations",
    },
    "evaluation": {
        "current_decision": "建立基础评估方法",
        "recommendation": "先用 5 到 10 个人工问题做功能验证，关注命中率、引用准确性和延迟。",
        "tradeoff": "人工评估启动快，但规模有限；自动评估后续再补。",
        "task": "写一组基础测试问题，并记录每个问题的召回与回答结果。",
        "next_step": "lab",
        "competency_area": "evaluation_design",
    },
}


class BuildService:
    def __init__(self, skill_dir: Path, username: str | None = None):
        self.skill_dir = skill_dir
        self.state = RagLearningStateStore.from_skill_dir(skill_dir, username=username)
        self.projects = self._load_projects()

    def _load_projects(self) -> list[dict]:
        projects: list[dict] = []
        for scenario in load_scenarios(self.skill_dir):
            project_id = scenario.get("project_id")
            if not project_id:
                continue
            overrides = PROJECT_OVERRIDES[project_id]
            projects.append(
                {
                    "id": project_id,
                    "name": overrides["name"],
                    "status": overrides["status"],
                    "description": overrides["description"],
                    "scenario_name": scenario["name"],
                    "estimated_time": scenario["estimated_time"],
                    "recommended_start": scenario["recommended_start"],
                }
            )
        return projects

    def _validate_project_id(self, project_id: str) -> None:
        if project_id not in {project["id"] for project in self.projects}:
            raise ValueError(f"Unknown build project: {project_id}")

    def entry_points(self) -> dict:
        return {
            "module": "build",
            "interaction": {
                "mode": "selector",
                "question": {
                    "header": "Build",
                    "question": "你想推进哪一个 RAG 项目？",
                    "options": [
                        {
                            "label": project["name"],
                            "description": project["description"],
                            "value": project["id"],
                        }
                        for project in self.projects
                    ],
                },
            },
            "projects": self.projects,
        }

    def start_project(self, project_id: str) -> dict:
        self._validate_project_id(project_id)
        progress = self.state.start_project(project_id)
        return {
            "module": "build",
            "project_id": project_id,
            "progress": progress,
        }

    def step_panel(self, project_id: str, step: str) -> dict:
        self._validate_project_id(project_id)
        if step not in STEP_PANELS:
            raise ValueError(f"Unknown build step: {step}")
        self.state.start_project(project_id)
        panel = STEP_PANELS[step]
        return {
            "module": "build",
            "project_id": project_id,
            "step": step,
            "current_decision": panel["current_decision"],
            "recommended_solution": panel["recommendation"],
            "tradeoff_reason": panel["tradeoff"],
            "minimum_task": panel["task"],
            "next_step": panel["next_step"],
        }

    def record_step(self, project_id: str, step: str) -> dict:
        self._validate_project_id(project_id)
        if step not in STEP_PANELS:
            raise ValueError(f"Unknown build step: {step}")
        panel = STEP_PANELS[step]
        progress = self.state.record_build_step(
            project_id, step, competency_area=panel["competency_area"]
        )
        return {
            "module": "build",
            "project_id": project_id,
            "step": step,
            "status": "recorded",
            "progress": progress,
        }
