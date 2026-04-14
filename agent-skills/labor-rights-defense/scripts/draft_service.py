from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DraftOutput:
    draft_markdown: str
    warnings: list[str]


def _line(title: str, value: str | None) -> str:
    return f"- {title}：{value if value else '（待补全）'}"


def _render_citations(citations: list[dict]) -> str:
    if not citations:
        return ""
    lines = ["\n## 官方依据引用（可追溯）"]
    for idx, item in enumerate(citations, start=1):
        locator = item.get("locator")
        source_url = item.get("source_url")
        retrieved_at = item.get("retrieved_at")
        content_hash = item.get("content_hash")
        doc_title = item.get("doc_title") or item.get("doc_id") or "（未命名法条）"
        lines.append(
            f"- [依据{idx}] {doc_title} {locator or '（待定位条款）'}；"
            f"source_url={source_url or '（缺）'}；retrieved_at={retrieved_at or '（缺）'}；"
            f"content_hash={content_hash or '（缺）'}"
        )
    return "\n".join(lines) + "\n"


def generate_arbitration_application(case: dict) -> DraftOutput:
    warnings: list[str] = []

    province = case.get("province")
    if not province:
        warnings.append("缺少 province（省份必填）；流程与入口信息将无法按省匹配。")
    city = case.get("city")

    applicant = case.get("applicant", {}) or {}
    respondent = case.get("respondent", {}) or {}

    claims = case.get("claims") or []
    if not claims:
        warnings.append("缺少 claims（请求事项）；已生成占位请求事项。")
        claims = ["（待补全）请求事项 1", "（待补全）请求事项 2"]

    facts = case.get("facts") or []
    if not facts:
        warnings.append("缺少 facts（事实经过）；已生成占位事实段落。")
        facts = [{"date": None, "event": "（待补全）事实经过"}]

    evidence = case.get("evidence") or []
    if not evidence:
        warnings.append("缺少 evidence（证据目录）；已生成占位证据条目。")
        evidence = [{"name": "（待补全）证据 1", "purpose": "（待补全）证明目的"}]

    citations = case.get("citations") or []
    if not citations:
        warnings.append("未提供 citations（官方依据引用）；草稿不包含可追溯条款引用。")

    lines: list[str] = []
    lines.append("# 劳动人事争议仲裁申请书（草稿）")
    lines.append("")
    lines.append("> 说明：本草稿为信息整理与材料生成辅助，不构成律师意见或法律结论，不保证结果。")
    lines.append("")
    lines.append("## 地区信息")
    lines.append(_line("省份", province))
    lines.append(_line("城市（可选）", city))
    lines.append("")
    lines.append("## 当事人信息")
    lines.append("### 申请人（劳动者）")
    lines.append(_line("姓名", applicant.get("name")))
    lines.append(_line("身份证号", applicant.get("id_number")))
    lines.append(_line("联系电话", applicant.get("phone")))
    lines.append(_line("联系地址", applicant.get("address")))
    lines.append("")
    lines.append("### 被申请人（用人单位）")
    lines.append(_line("单位名称", respondent.get("name")))
    lines.append(_line("统一社会信用代码", respondent.get("credit_code")))
    lines.append(_line("住所地/注册地址", respondent.get("address")))
    lines.append(_line("法定代表人/负责人", respondent.get("legal_rep")))
    lines.append("")
    lines.append("## 请求事项")
    for idx, item in enumerate(claims, start=1):
        lines.append(f"{idx}. {item}")
    lines.append("")
    lines.append("## 事实与理由")
    for item in facts:
        date = item.get("date") or "（日期待补全）"
        event = item.get("event") or "（事实待补全）"
        lines.append(f"- {date}：{event}")
    lines.append("")
    lines.append("## 证据目录")
    for idx, item in enumerate(evidence, start=1):
        name = item.get("name") or f"证据{idx}"
        purpose = item.get("purpose") or "（证明目的待补全）"
        lines.append(f"{idx}. {name}（证明目的：{purpose}）")

    citations_block = _render_citations(citations)
    if citations_block:
        lines.append(citations_block.rstrip("\n"))

    return DraftOutput(draft_markdown="\n".join(lines).rstrip() + "\n", warnings=warnings)


def load_case(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

