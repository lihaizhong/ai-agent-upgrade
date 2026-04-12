"""
Prompt Lab 模块
负责 workflow、槽位校验、草稿校验和模板持久化。
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from .state import LearningStateStore
from .workspace import get_workspace_paths


def _timestamp() -> str:
    return datetime.now().astimezone().isoformat()


def build_workflow(topic: str | None = None) -> dict:
    return {
        "interaction": {
            "mode": "inform",
        },
        "topic": topic,
        "workflow": [
            "先收集任务目标、输入、输出、限制",
            "脚本检查是否缺少关键槽位",
            "LLM 生成初稿提示词",
            "脚本按审查清单逐项复核",
            "LLM 只修改未通过项",
        ],
        "required_slots": [
            "task",
            "input",
            "output_format",
            "constraints",
            "quality_bar",
        ],
        "interview_order": [
            "task",
            "input",
            "output_format",
            "constraints",
            "quality_bar",
        ],
    }


def build_review_checklist(topic: str | None = None) -> dict:
    return {
        "interaction": {
            "mode": "inform",
        },
        "topic": topic,
        "checklist": [
            "任务目标是否单一明确",
            "输入信息是否定义清楚",
            "输出格式是否可直接判定",
            "约束条件是否可执行",
            "是否明确了失败或边界处理方式",
            "是否避免了重复或冲突指令",
        ],
    }


def build_interview_blueprint(topic: str | None = None) -> dict:
    return {
        "interaction": {
            "mode": "inform",
            "note": "每个 slot 是开放式追问，由 LLM 逐个引导用户填写，不要把 slot 做成选择器。",
        },
        "topic": topic,
        "goal": "先补齐稳定槽位，再生成提示词初稿",
        "slots": [
            {
                "name": "task",
                "required": True,
                "interaction": {
                    "mode": "open_ended",
                    "prompt_hint": "用自然语言追问用户想让 AI 完成的具体任务目标。",
                },
                "question": "你希望 AI 最终完成什么任务？",
                "examples": ["总结会议纪要", "把产品评论翻译成中文并保留情感"],
            },
            {
                "name": "input",
                "required": True,
                "interaction": {
                    "mode": "open_ended",
                    "prompt_hint": "用自然语言追问输入材料、字段和上下文来源。",
                },
                "question": "AI 会拿到什么输入？输入里有哪些字段或材料？",
                "examples": ["一段用户评论", "一份 Markdown 文档和一张表格"],
            },
            {
                "name": "output_format",
                "required": True,
                "interaction": {
                    "mode": "open_ended",
                    "prompt_hint": "用自然语言追问输出形式、字段和格式约束。",
                },
                "question": "你希望输出长什么样？是段落、列表、JSON 还是表格？",
                "examples": ["JSON", "三段式总结", "固定字段表格"],
            },
            {
                "name": "constraints",
                "required": True,
                "interaction": {
                    "mode": "open_ended",
                    "prompt_hint": "用自然语言追问限制条件、禁区和必须遵守的规则。",
                },
                "question": "有哪些限制、禁区或必须遵守的规则？",
                "examples": ["不要编造来源", "只返回中文", "不得超过 200 字"],
            },
            {
                "name": "quality_bar",
                "required": True,
                "interaction": {
                    "mode": "open_ended",
                    "prompt_hint": "用自然语言追问用户如何定义合格结果和最看重的质量标准。",
                },
                "question": "什么样的结果才算合格？你最看重准确、完整、速度还是风格？",
                "examples": ["格式稳定", "专业术语准确", "可直接复制给客户"],
            },
        ],
    }


def _is_empty_slot_value(value: object) -> bool:
    if value is None or value == [] or value == {}:
        return True
    if isinstance(value, str):
        return not value.strip()
    return False


def validate_slots(payload: dict, required_slots: list[str]) -> dict:
    missing = []
    empty = []

    for slot in required_slots:
        if slot not in payload:
            missing.append(slot)
            continue
        value = payload.get(slot)
        if _is_empty_slot_value(value):
            empty.append(slot)

    return {
        "interaction": {
            "mode": "inform",
        },
        "valid": not missing and not empty,
        "missing_slots": missing,
        "empty_slots": empty,
    }


def validate_draft(payload: dict, checklist: list[str]) -> dict:
    errors = []

    prompt = payload.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        errors.append("prompt 必须是非空字符串")

    review = payload.get("review", {})
    if not isinstance(review, dict):
        errors.append("review 必须是对象")
        review = {}

    failed_items = []
    for item in checklist:
        if item not in review:
            errors.append(f"review 缺少检查项: {item}")
            continue
        status = review[item]
        if status not in {"pass", "fail"}:
            errors.append(f"review[{item}] 必须为 pass 或 fail")
        elif status == "fail":
            failed_items.append(item)

    revisions = payload.get("revisions", [])
    if failed_items and not isinstance(revisions, list):
        errors.append("存在未通过项时，revisions 必须为列表")
    elif failed_items and not revisions:
        errors.append("存在未通过项时，必须提供 revisions")
    if failed_items:
        errors.append("review 存在未通过项: " + ", ".join(failed_items))

    return {
        "interaction": {
            "mode": "inform",
        },
        "valid": not errors,
        "failed_items": failed_items,
        "errors": errors,
    }


class PromptLabService:
    """Prompt Lab 服务。"""

    def __init__(self, workspace_paths: dict[str, Path], state_store: LearningStateStore):
        self.workspace_paths = workspace_paths
        self.state_store = state_store
        self.template_index_file = workspace_paths["template_index_file"]
        self.template_dir = workspace_paths["lab_templates_dir"]

    @classmethod
    def from_skill_dir(
        cls, skill_dir: Path, username: str | None = None
    ) -> "PromptLabService":
        workspace_paths = get_workspace_paths(skill_dir, username=username)
        return cls(
            workspace_paths=workspace_paths,
            state_store=LearningStateStore(workspace_paths),
        )

    def _load_template_index(self) -> dict:
        if not self.template_index_file.exists():
            return {"templates": [], "updated_at": None}
        return json.loads(self.template_index_file.read_text(encoding="utf-8"))

    def _save_template_index(self, payload: dict) -> None:
        payload["updated_at"] = _timestamp()
        self.template_index_file.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def save_template(self, payload: dict) -> dict:
        name = payload.get("name")
        topic = payload.get("topic")
        slots = payload.get("slots")
        prompt = payload.get("prompt")
        review = payload.get("review")
        revisions = payload.get("revisions", [])
        confirmed = payload.get("confirmed") is True

        errors = []
        if not isinstance(name, str) or not name.strip():
            errors.append("name 必须是非空字符串")
        if not isinstance(prompt, str) or not prompt.strip():
            errors.append("prompt 必须是非空字符串")
        if not isinstance(slots, dict) or not slots:
            errors.append("slots 必须是非空对象")
        else:
            slot_validation = validate_slots(slots, build_workflow(topic)["required_slots"])
            if not slot_validation["valid"]:
                if slot_validation["missing_slots"]:
                    errors.append(
                        "slots 缺少必填项: " + ", ".join(slot_validation["missing_slots"])
                    )
                if slot_validation["empty_slots"]:
                    errors.append(
                        "slots 存在空值项: " + ", ".join(slot_validation["empty_slots"])
                    )

        draft_validation = validate_draft(
            {
                "prompt": prompt,
                "review": review,
                "revisions": revisions,
            },
            build_review_checklist(topic)["checklist"],
        )
        if not draft_validation["valid"]:
            errors.extend(draft_validation["errors"])
        if not confirmed:
            errors.append("confirmed 必须为 true")
        if errors:
            return {
                "interaction": {
                    "mode": "inform",
                },
                "saved": False,
                "errors": errors,
            }

        template_index = self._load_template_index()
        next_index = len(template_index.get("templates", [])) + 1
        template_id = f"tpl-{datetime.now().strftime('%Y%m%d')}-{next_index:03d}"
        template_path = self.template_dir / f"{template_id}.json"
        now = _timestamp()
        template_payload = {
            "id": template_id,
            "name": name.strip(),
            "topic": topic,
            "slots": slots,
            "prompt": prompt,
            "notes": payload.get("notes", ""),
            "created_at": now,
            "updated_at": now,
        }
        template_path.write_text(
            json.dumps(template_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        template_index.setdefault("templates", []).append(
            {
                "id": template_id,
                "name": name.strip(),
                "topic": topic,
                "created_at": now,
                "updated_at": now,
                "path": str(template_path),
                "tags": payload.get("tags", []),
            }
        )
        self._save_template_index(template_index)
        self.state_store.update_current_state(
            current_module="lab",
            last_action="template_saved",
            recommended_next_action="open_dashboard",
        )

        return {
            "interaction": {
                "mode": "inform",
            },
            "saved": True,
            "template_id": template_id,
            "path": str(template_path),
        }

    def list_templates(self) -> dict:
        template_index = self._load_template_index()
        return {
            "interaction": {
                "mode": "inform",
            },
            "count": len(template_index.get("templates", [])),
            "templates": template_index.get("templates", []),
            "updated_at": template_index.get("updated_at"),
        }
