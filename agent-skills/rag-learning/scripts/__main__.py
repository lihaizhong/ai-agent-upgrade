"""
RAG Learning 平台 CLI 入口。
当前提供 foundation、learning 和 build 的最小可运行命令面。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parent))
    from build import BuildService
    from config import load_lab_topics, load_review_scenarios
    from home import HomeService
    from lab import LabService
    from learning import LearningService
    from profile import ProfileService
    from review import ReviewService
    from workspace import (
        ensure_workspace,
        get_workspace_root,
        normalize_workspace_username,
        resolve_git_username,
    )
else:
    from .build import BuildService
    from .config import load_lab_topics, load_review_scenarios
    from .home import HomeService
    from .lab import LabService
    from .learning import LearningService
    from .profile import ProfileService
    from .review import ReviewService
    from .workspace import (
        ensure_workspace,
        get_workspace_root,
        normalize_workspace_username,
        resolve_git_username,
    )


def _skill_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def _json_print(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _lab_topics(skill_dir: Path) -> list[str]:
    return list(load_lab_topics(skill_dir).keys())


def _review_scenarios(skill_dir: Path) -> list[str]:
    return list(load_review_scenarios(skill_dir).keys())


def main() -> None:
    parser = argparse.ArgumentParser(description="RAG Learning 平台")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    parser_workspace = subparsers.add_parser("workspace", help="workspace 管理")
    parser_workspace.add_argument("--resolve-user", action="store_true")
    parser_workspace.add_argument("--show-root", action="store_true")
    parser_workspace.add_argument("--bootstrap", action="store_true")
    parser_workspace.add_argument("--username", type=str)

    parser_home = subparsers.add_parser("home", help="平台首页")
    parser_home.add_argument("--dashboard", action="store_true")
    parser_home.add_argument("--resume", action="store_true")
    parser_home.add_argument("--recommend", action="store_true")
    parser_home.add_argument("--username", type=str)

    parser_learning = subparsers.add_parser("learning", help="学习中心")
    parser_learning.add_argument("--catalog", action="store_true")
    parser_learning.add_argument("--path", action="store_true")
    parser_learning.add_argument(
        "--level", choices=["novice", "intermediate", "advanced", "enterprise"]
    )
    parser_learning.add_argument("--recommend-course", action="store_true")
    parser_learning.add_argument("--lesson-meta", action="store_true")
    parser_learning.add_argument("--complete", action="store_true")
    parser_learning.add_argument("--course", type=int)
    parser_learning.add_argument("--username", type=str)

    parser_build = subparsers.add_parser("build", help="实战中心")
    parser_build.add_argument("--entry-points", action="store_true")
    parser_build.add_argument("--start-project", action="store_true")
    parser_build.add_argument("--step-panel", action="store_true")
    parser_build.add_argument("--record-step", action="store_true")
    parser_build.add_argument("--project", type=str)
    parser_build.add_argument("--step", type=str)
    parser_build.add_argument("--username", type=str)

    parser_lab = subparsers.add_parser("lab", help="RAG Lab")
    parser_lab.add_argument("--entry-points", action="store_true")
    parser_lab.add_argument("--blueprint", action="store_true")
    parser_lab.add_argument("--record-result", action="store_true")
    parser_lab.add_argument("--history", action="store_true")
    parser_lab.add_argument("--topic", type=str)
    parser_lab.add_argument("--summary", type=str)
    parser_lab.add_argument("--recommended-choice", type=str)
    parser_lab.add_argument("--tradeoff-note", type=str)
    parser_lab.add_argument("--username", type=str)

    parser_review = subparsers.add_parser("review", help="架构评审")
    parser_review.add_argument("--entry-points", action="store_true")
    parser_review.add_argument("--template", action="store_true")
    parser_review.add_argument("--record-summary", action="store_true")
    parser_review.add_argument("--history", action="store_true")
    parser_review.add_argument("--scenario", type=str)
    parser_review.add_argument("--constraints-summary", type=str)
    parser_review.add_argument("--risk-summary", type=str)
    parser_review.add_argument("--recommended-stack", type=str)
    parser_review.add_argument("--username", type=str)

    parser_profile = subparsers.add_parser("profile", help="学习档案")
    parser_profile.add_argument("--summary", action="store_true")
    parser_profile.add_argument("--progress", action="store_true")
    parser_profile.add_argument("--experiments", action="store_true")
    parser_profile.add_argument("--reviews", action="store_true")
    parser_profile.add_argument("--username", type=str)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    skill_dir = _skill_dir()
    lab_topics = _lab_topics(skill_dir)
    review_scenarios = _review_scenarios(skill_dir)

    if args.command == "workspace":
        if args.resolve_user:
            raw_username = args.username if args.username else resolve_git_username()
            _json_print(
                {
                    "source_git_username": raw_username,
                    "workspace_user": normalize_workspace_username(raw_username),
                }
            )
            return
        if args.show_root:
            _json_print({"workspace_root": str(get_workspace_root(skill_dir))})
            return
        if args.bootstrap:
            _json_print(ensure_workspace(skill_dir, username=args.username))
            return
        parser_workspace.print_help()
        return

    ensure_workspace(skill_dir, username=getattr(args, "username", None))

    if args.command == "home":
        service = HomeService(skill_dir, username=args.username)
        if args.dashboard:
            _json_print(service.dashboard())
            return
        if args.resume:
            _json_print(service.resume())
            return
        if args.recommend:
            _json_print(service.recommend())
            return
        parser_home.print_help()
        return

    if args.command == "learning":
        service = LearningService(skill_dir, username=args.username)
        if args.catalog:
            _json_print(service.catalog())
            return
        if args.path and args.level:
            _json_print(service.path(args.level))
            return
        if args.recommend_course:
            _json_print(service.recommend_course())
            return
        if args.lesson_meta and args.course:
            _json_print(service.lesson_meta(args.course))
            return
        if args.complete and args.course:
            _json_print(service.complete_course(args.course))
            return
        parser_learning.print_help()
        return

    if args.command == "build":
        service = BuildService(skill_dir, username=args.username)
        if args.entry_points:
            _json_print(service.entry_points())
            return
        if args.start_project and args.project:
            _json_print(service.start_project(args.project))
            return
        if args.step_panel and args.project and args.step:
            _json_print(service.step_panel(args.project, args.step))
            return
        if args.record_step and args.project and args.step:
            _json_print(service.record_step(args.project, args.step))
            return
        parser_build.print_help()
        return

    if args.command == "lab":
        service = LabService(skill_dir, username=args.username)
        if args.topic and args.topic not in lab_topics:
            raise ValueError(f"Unknown lab topic: {args.topic}")
        if args.entry_points:
            _json_print(service.entry_points())
            return
        if args.blueprint and args.topic:
            _json_print(service.blueprint(args.topic))
            return
        if (
            args.record_result
            and args.topic
            and args.summary
            and args.recommended_choice
            and args.tradeoff_note
        ):
            _json_print(
                service.record_result(
                    topic=args.topic,
                    summary=args.summary,
                    recommended_choice=args.recommended_choice,
                    tradeoff_note=args.tradeoff_note,
                )
            )
            return
        if args.history:
            _json_print(service.history())
            return
        parser_lab.print_help()
        return

    if args.command == "review":
        service = ReviewService(skill_dir, username=args.username)
        if args.scenario and args.scenario not in review_scenarios:
            raise ValueError(f"Unknown review scenario: {args.scenario}")
        if args.entry_points:
            _json_print(service.entry_points())
            return
        if args.template and args.scenario:
            _json_print(service.template(args.scenario))
            return
        if (
            args.record_summary
            and args.scenario
            and args.constraints_summary
            and args.risk_summary
            and args.recommended_stack
        ):
            _json_print(
                service.record_summary(
                    scenario=args.scenario,
                    constraints_summary=args.constraints_summary,
                    recommended_stack=json.loads(args.recommended_stack),
                    risk_summary=args.risk_summary,
                )
            )
            return
        if args.history:
            _json_print(service.history())
            return
        parser_review.print_help()
        return

    if args.command == "profile":
        service = ProfileService(skill_dir, username=args.username)
        if args.summary:
            _json_print(service.summary())
            return
        if args.progress:
            _json_print(service.progress())
            return
        if args.experiments:
            _json_print(service.experiments())
            return
        if args.reviews:
            _json_print(service.reviews())
            return
        parser_profile.print_help()
        return


if __name__ == "__main__":
    main()
