from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parent))
    from config import find_province_seeds, load_procedure_seeds
    from json_io import json_print
    from law_service import (
        LABOR_CONTRACT_LAW_DOC_ID,
        LABOR_CONTRACT_LAW_URL,
        fetch_and_store_law,
        show_latest_parsed,
    )
    from procedure_service import crawl_procedure
    from draft_service import generate_arbitration_application, load_case
    from workspace import ensure_workspace, get_workspace_root, normalize_workspace_username, resolve_git_username
else:
    from .config import find_province_seeds, load_procedure_seeds
    from .json_io import json_print
    from .law_service import (
        LABOR_CONTRACT_LAW_DOC_ID,
        LABOR_CONTRACT_LAW_URL,
        fetch_and_store_law,
        show_latest_parsed,
    )
    from .procedure_service import crawl_procedure
    from .draft_service import generate_arbitration_application, load_case
    from .workspace import (
        ensure_workspace,
        get_workspace_root,
        normalize_workspace_username,
        resolve_git_username,
    )


def _skill_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def main() -> None:
    parser = argparse.ArgumentParser(description="劳动维权助手（互联网白领）")
    subparsers = parser.add_subparsers(dest="command")

    parser_workspace = subparsers.add_parser("workspace", help="workspace 管理")
    parser_workspace.add_argument("--resolve-user", action="store_true")
    parser_workspace.add_argument("--show-root", action="store_true")
    parser_workspace.add_argument("--bootstrap", action="store_true")
    parser_workspace.add_argument("--username", type=str)

    parser_procedure = subparsers.add_parser("procedure", help="流程与入口信息（procedure_sources）")
    parser_procedure.add_argument("--show-seeds", action="store_true", help="显示指定省份的种子页配置")
    parser_procedure.add_argument("--crawl", action="store_true", help="从种子页开始抓取流程入口信息（仅 *.gov.cn）")
    parser_procedure.add_argument("--province", type=str, help="省份（必填）")
    parser_procedure.add_argument("--city", type=str, help="城市（可选）")
    parser_procedure.add_argument("--max-pages", type=int, default=30)
    parser_procedure.add_argument("--username", type=str, help="显式指定用户名")

    parser_law = subparsers.add_parser("law", help="官方法条（law_sources）")
    parser_law.add_argument("--fetch-seed", action="store_true", help="抓取并缓存劳动合同法（seed）")
    parser_law.add_argument("--fetch", action="store_true", help="抓取并缓存指定 law URL")
    parser_law.add_argument("--show-latest", action="store_true", help="显示指定 doc 的最新解析结果")
    parser_law.add_argument("--doc", type=str, help="doc_id（默认 labor_contract_law）")
    parser_law.add_argument("--url", type=str, help="law URL（仅允许 flk.npc.gov.cn）")
    parser_law.add_argument("--username", type=str, help="显式指定用户名")

    parser_draft = subparsers.add_parser("draft", help="文书草稿（D）")
    parser_draft.add_argument("--generate", action="store_true", help="生成仲裁申请书草稿")
    parser_draft.add_argument("--input", type=str, help="case JSON 路径")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    skill_dir = _skill_dir()

    if args.command == "workspace":
        if args.resolve_user:
            raw_username = args.username if args.username else resolve_git_username()
            json_print(
                {
                    "source_git_username": raw_username,
                    "workspace_user": normalize_workspace_username(raw_username),
                }
            )
            return
        if args.show_root:
            json_print({"workspace_root": str(get_workspace_root(skill_dir))})
            return
        if args.bootstrap:
            json_print(ensure_workspace(skill_dir, username=args.username))
            return
        parser_workspace.print_help()
        return

    if args.command == "procedure":
        if args.show_seeds and args.province:
            seeds = load_procedure_seeds(skill_dir)
            province_item = find_province_seeds(seeds, args.province)
            json_print(
                {
                    "interaction": {"mode": "inform"},
                    "province": args.province,
                    "found": bool(province_item),
                    "seed": province_item,
                }
            )
            return
        if args.crawl and args.province:
            run = crawl_procedure(
                skill_dir,
                province=args.province,
                city=args.city,
                max_pages=int(args.max_pages),
                username=args.username,
            )
            json_print(
                {
                    "interaction": {"mode": "inform"},
                    "action": "crawled",
                    "province": args.province,
                    "city": args.city,
                    "run_id": run.run_id,
                    "run_dir": run.run_dir,
                    "page_count": len(run.pages),
                    "pages": run.pages,
                }
            )
            return
        parser_procedure.print_help()
        return

    if args.command == "law":
        doc_id = args.doc if args.doc else LABOR_CONTRACT_LAW_DOC_ID
        if args.fetch_seed:
            output = fetch_and_store_law(
                skill_dir,
                doc_id=LABOR_CONTRACT_LAW_DOC_ID,
                url=LABOR_CONTRACT_LAW_URL,
                username=args.username,
            )
            json_print(
                {
                    "interaction": {"mode": "inform"},
                    "action": "fetched",
                    "doc_id": output.doc_id,
                    "source_url": output.source_url,
                    "retrieved_at": output.retrieved_at,
                    "content_hash": output.content_hash,
                    "parsed_json_path": output.parsed_json_path,
                }
            )
            return
        if args.fetch and args.url:
            output = fetch_and_store_law(
                skill_dir,
                doc_id=doc_id,
                url=args.url,
                username=args.username,
            )
            json_print(
                {
                    "interaction": {"mode": "inform"},
                    "action": "fetched",
                    "doc_id": output.doc_id,
                    "source_url": output.source_url,
                    "retrieved_at": output.retrieved_at,
                    "content_hash": output.content_hash,
                    "parsed_json_path": output.parsed_json_path,
                }
            )
            return
        if args.show_latest:
            payload = show_latest_parsed(
                skill_dir,
                doc_id=doc_id,
                username=args.username,
            )
            json_print(
                {
                    "interaction": {"mode": "inform"},
                    "action": "show_latest",
                    "doc_id": doc_id,
                    "found": bool(payload),
                    "parsed": payload,
                }
            )
            return
        parser_law.print_help()
        return

    if args.command == "draft":
        if args.generate and args.input:
            case = load_case(Path(args.input))
            output = generate_arbitration_application(case)
            json_print(
                {
                    "interaction": {"mode": "inform"},
                    "action": "draft_generated",
                    "warnings": output.warnings,
                    "draft_markdown": output.draft_markdown,
                }
            )
            return
        parser_draft.print_help()
        return

    raise AssertionError(f"Unhandled command: {args.command}")


if __name__ == "__main__":
    main()
