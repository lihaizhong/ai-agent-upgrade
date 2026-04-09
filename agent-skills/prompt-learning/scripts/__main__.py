"""
提示词工程学习系统 - CLI 入口
提供命令行接口供 AI Agent 调用
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from scripts.exam import ExamEngine, ExamService
    from scripts.home import HomeService
    from scripts.learning import LearningService
    from scripts.practice import PracticeService
    from scripts.profile import ProfileService
    from scripts.prompt_lab import (
        PromptLabService,
        build_interview_blueprint,
        build_review_checklist,
        build_workflow,
        validate_draft,
        validate_slots,
    )
    from scripts.workspace import (
        ensure_workspace,
        get_workspace_root,
        normalize_workspace_username,
        resolve_git_username,
    )
else:
    from .exam import ExamEngine, ExamService
    from .home import HomeService
    from .learning import LearningService
    from .practice import PracticeService
    from .profile import ProfileService
    from .prompt_lab import (
        PromptLabService,
        build_interview_blueprint,
        build_review_checklist,
        build_workflow,
        validate_draft,
        validate_slots,
    )
    from .workspace import (
        ensure_workspace,
        get_workspace_root,
        normalize_workspace_username,
        resolve_git_username,
    )


def _skill_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def resolve_username(explicit_username: str = None) -> str:
    """解析报告使用的用户名。"""
    if explicit_username and explicit_username.strip():
        return explicit_username.strip()

    try:
        result = subprocess.run(
            ["git", "config", "user.name"],
            check=True,
            capture_output=True,
            text=True,
        )
        git_username = result.stdout.strip()
        if git_username:
            return git_username
    except (OSError, subprocess.CalledProcessError):
        pass

    return os.environ.get("USER", "unknown")


def main():
    parser = argparse.ArgumentParser(description="提示词工程学习系统")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # Workspace
    parser_workspace = subparsers.add_parser("workspace", help="workspace 管理")
    parser_workspace.add_argument(
        "--resolve-user", action="store_true", help="解析当前 workspace 用户名"
    )
    parser_workspace.add_argument(
        "--show-root", action="store_true", help="显示 workspace 根目录"
    )
    parser_workspace.add_argument(
        "--bootstrap", action="store_true", help="初始化当前用户 workspace"
    )
    parser_workspace.add_argument("--username", type=str, help="显式指定用户名")

    # Home
    parser_home = subparsers.add_parser("home", help="平台首页")
    parser_home.add_argument("--dashboard", action="store_true", help="获取首页面板")
    parser_home.add_argument("--resume", action="store_true", help="获取继续学习目标")
    parser_home.add_argument(
        "--recommend", action="store_true", help="获取下一步推荐动作"
    )
    parser_home.add_argument("--username", type=str, help="显式指定用户名")

    # Learning
    parser_learning = subparsers.add_parser("learning", help="学习中心")
    parser_learning.add_argument("--catalog", action="store_true", help="获取课程目录")
    parser_learning.add_argument("--category", type=str, help="按类别列出课程")
    parser_learning.add_argument(
        "--recommend-course", action="store_true", help="获取推荐课程"
    )
    parser_learning.add_argument(
        "--lesson-meta", action="store_true", help="获取课程内容元数据"
    )
    parser_learning.add_argument(
        "--lesson-panel", action="store_true", help="获取课后面板"
    )
    parser_learning.add_argument(
        "--code-meta", action="store_true", help="获取代码元数据"
    )
    parser_learning.add_argument(
        "--code-outline", action="store_true", help="获取代码讲解结构"
    )
    parser_learning.add_argument("--course", type=int, help="课程编号")
    parser_learning.add_argument("--complete", action="store_true", help="标记课程完成")
    parser_learning.add_argument("--username", type=str, help="显式指定用户名")

    # Practice
    parser_practice = subparsers.add_parser("practice", help="练习中心")
    parser_practice.add_argument(
        "--entry-points", action="store_true", help="获取练习入口"
    )
    parser_practice.add_argument(
        "--resume", action="store_true", help="获取继续练习目标"
    )
    parser_practice.add_argument(
        "--blueprint", action="store_true", help="获取练习蓝图"
    )
    parser_practice.add_argument(
        "--record-result", action="store_true", help="记录练习结果摘要"
    )
    parser_practice.add_argument(
        "--review-mistakes", action="store_true", help="查看未解决错题"
    )
    parser_practice.add_argument("--summary", action="store_true", help="获取练习摘要")
    parser_practice.add_argument(
        "--mode",
        type=str,
        choices=["current", "targeted", "mistake"],
        help="练习模式",
    )
    parser_practice.add_argument("--course", type=int, help="课程编号")
    parser_practice.add_argument("--focus-tag", type=str, help="错题回练焦点标签")
    parser_practice.add_argument("--username", type=str, help="显式指定用户名")

    # Profile
    parser_profile = subparsers.add_parser("profile", help="学习档案")
    parser_profile.add_argument("--summary", action="store_true", help="获取档案摘要")
    parser_profile.add_argument("--progress", action="store_true", help="获取进度详情")
    parser_profile.add_argument("--mistakes", action="store_true", help="获取错题详情")
    parser_profile.add_argument(
        "--exam-history", action="store_true", help="获取考试历史"
    )
    parser_profile.add_argument("--templates", action="store_true", help="获取模板列表")
    parser_profile.add_argument("--username", type=str, help="显式指定用户名")

    # 考试模式
    parser_exam = subparsers.add_parser("exam", help="考试模式")
    parser_exam.add_argument("--entry-points", action="store_true", help="获取考试入口")
    parser_exam.add_argument("--structure", action="store_true", help="获取考试结构")
    parser_exam.add_argument("--blueprint", action="store_true", help="获取考试蓝图")
    parser_exam.add_argument("--start", action="store_true", help="开始考试会话")
    parser_exam.add_argument(
        "--current-question", action="store_true", help="获取当前题上下文"
    )
    parser_exam.add_argument("--resume", action="store_true", help="获取恢复考试入口")
    parser_exam.add_argument("--abandon", action="store_true", help="放弃考试会话")
    parser_exam.add_argument(
        "--submit-answer", action="store_true", help="提交当前题答案"
    )
    parser_exam.add_argument(
        "--submit-question", action="store_true", help="提交题目到考试会话"
    )
    parser_exam.add_argument("--finish", action="store_true", help="完成考试并生成报告")
    parser_exam.add_argument(
        "--type",
        type=str,
        choices=["diagnostic", "final"],
        help="考试类型",
    )
    parser_exam.add_argument("--grade-mc", action="store_true", help="评分选择题")
    parser_exam.add_argument("--grade-fill", action="store_true", help="评分填空题")
    parser_exam.add_argument("--grade-essay", action="store_true", help="评分大题")
    parser_exam.add_argument(
        "--validate-mc", action="store_true", help="校验选择题结构"
    )
    parser_exam.add_argument(
        "--validate-fill", action="store_true", help="校验填空题结构"
    )
    parser_exam.add_argument(
        "--validate-essay", action="store_true", help="校验大题结构"
    )
    parser_exam.add_argument(
        "--validate-paper", action="store_true", help="校验整张试卷结构"
    )
    parser_exam.add_argument("--report", action="store_true", help="生成考试报告")
    parser_exam.add_argument(
        "--record-history", action="store_true", help="记录考试历史摘要"
    )
    parser_exam.add_argument(
        "--history-summary", action="store_true", help="获取考试历史摘要"
    )
    parser_exam.add_argument("--question", type=int, help="题号")
    parser_exam.add_argument("--difficulty", type=str, help="难度")
    parser_exam.add_argument("--answer", type=str, help="用户答案")
    parser_exam.add_argument("--session", type=str, help="考试会话 ID")
    parser_exam.add_argument("--username", type=str, help="用户名")

    # Prompt Lab
    parser_lab = subparsers.add_parser("lab", help="Prompt Lab")
    parser_lab.add_argument("--topic", type=str, help="主题")
    parser_lab.add_argument("--workflow", action="store_true", help="获取固定流程")
    parser_lab.add_argument(
        "--interview-blueprint", action="store_true", help="获取固定澄清槽位"
    )
    parser_lab.add_argument(
        "--review-checklist", action="store_true", help="获取审查清单"
    )
    parser_lab.add_argument("--validate-slots", action="store_true", help="校验槽位")
    parser_lab.add_argument("--validate-draft", action="store_true", help="校验草稿")
    parser_lab.add_argument("--save-template", action="store_true", help="保存模板")
    parser_lab.add_argument("--list-templates", action="store_true", help="列出模板")
    parser_lab.add_argument("--username", type=str, help="显式指定用户名")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "exam":
        skill_dir = _skill_dir()
        ensure_workspace(skill_dir, username=args.username)
        exam = ExamEngine(skill_dir=skill_dir, username=args.username)
        exam_service = ExamService.from_skill_dir(skill_dir, username=args.username)

        exam_type = args.type or "diagnostic"

        if args.entry_points:
            print(json.dumps(exam.get_entry_points(), ensure_ascii=False, indent=2))

        elif args.structure:
            print(
                json.dumps(
                    exam.generate_exam_structure(exam_type),
                    ensure_ascii=False,
                    indent=2,
                )
            )

        elif args.blueprint:
            print(
                json.dumps(
                    exam.build_exam_blueprint(exam_type),
                    ensure_ascii=False,
                    indent=2,
                )
            )

        elif args.start:
            print(
                json.dumps(
                    exam_service.start_session(exam_type),
                    ensure_ascii=False,
                    indent=2,
                )
            )

        elif args.current_question:
            print(
                json.dumps(
                    exam_service.get_current_question_context(args.session),
                    ensure_ascii=False,
                    indent=2,
                )
            )

        elif args.resume:
            print(
                json.dumps(
                    exam_service.get_resume_prompt(),
                    ensure_ascii=False,
                    indent=2,
                )
            )

        elif args.abandon:
            print(
                json.dumps(
                    exam_service.abandon_session(args.session),
                    ensure_ascii=False,
                    indent=2,
                )
            )

        elif args.submit_answer:
            payload = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
            print(
                json.dumps(
                    exam_service.submit_answer(payload, args.session),
                    ensure_ascii=False,
                    indent=2,
                )
            )

        elif args.submit_question:
            payload = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
            print(
                json.dumps(
                    exam_service.submit_question(payload, args.session),
                    ensure_ascii=False,
                    indent=2,
                )
            )

        elif args.finish:
            print(
                json.dumps(
                    exam_service.finish_session(args.session),
                    ensure_ascii=False,
                    indent=2,
                )
            )

        elif args.grade_mc and args.question and args.answer:
            question = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
            is_correct, score = exam.grade_mc(question, args.answer)
            print(
                json.dumps(
                    {"correct": is_correct, "score": score},
                    ensure_ascii=False,
                    indent=2,
                )
            )

        elif args.grade_fill and args.question and args.answer:
            question = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
            is_correct, score = exam.grade_fill(question, args.answer)
            print(
                json.dumps(
                    {"correct": is_correct, "score": score},
                    ensure_ascii=False,
                    indent=2,
                )
            )

        elif args.validate_mc:
            question = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
            print(
                json.dumps(
                    exam.validate_mc_question(question), ensure_ascii=False, indent=2
                )
            )

        elif args.validate_fill:
            question = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
            print(
                json.dumps(
                    exam.validate_fill_question(question), ensure_ascii=False, indent=2
                )
            )

        elif args.validate_essay:
            question = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
            print(
                json.dumps(
                    exam.validate_essay_question(question), ensure_ascii=False, indent=2
                )
            )

        elif args.validate_paper:
            questions = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else []
            print(
                json.dumps(
                    exam.validate_exam_paper(questions), ensure_ascii=False, indent=2
                )
            )

        elif args.report:
            questions = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else []
            report_path = exam.generate_report(
                questions, [], [], resolve_username(args.username)
            )
            print(
                json.dumps({"report_path": report_path}, ensure_ascii=False, indent=2)
            )
        elif args.record_history:
            payload = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
            print(
                json.dumps(
                    exam_service.record_history(payload),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        elif args.history_summary:
            print(
                json.dumps(
                    exam_service.get_history_summary(),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            parser_exam.print_help()
            sys.exit(1)

    elif args.command == "lab":
        skill_dir = _skill_dir()
        ensure_workspace(skill_dir, username=args.username)
        prompt_lab = PromptLabService.from_skill_dir(skill_dir, username=args.username)

        if args.workflow:
            print(json.dumps(build_workflow(args.topic), ensure_ascii=False, indent=2))
        elif args.review_checklist:
            print(
                json.dumps(
                    build_review_checklist(args.topic),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        elif args.interview_blueprint:
            print(
                json.dumps(
                    build_interview_blueprint(args.topic),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        elif args.validate_slots:
            payload = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
            required_slots = build_workflow(args.topic)["required_slots"]
            print(
                json.dumps(
                    validate_slots(payload, required_slots),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        elif args.validate_draft:
            payload = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
            checklist = build_review_checklist(args.topic)["checklist"]
            print(
                json.dumps(
                    validate_draft(payload, checklist),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        elif args.save_template:
            payload = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
            print(
                json.dumps(
                    prompt_lab.save_template(payload),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        elif args.list_templates:
            print(
                json.dumps(
                    prompt_lab.list_templates(),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            parser_lab.print_help()
            sys.exit(1)

    elif args.command == "workspace":
        skill_dir = _skill_dir()

        if args.resolve_user:
            source_git_username = (
                args.username if args.username is not None else resolve_git_username()
            )
            print(
                json.dumps(
                    {
                        "source_git_username": source_git_username,
                        "workspace_user": normalize_workspace_username(
                            source_git_username
                        ),
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        elif args.show_root:
            print(
                json.dumps(
                    {
                        "workspace_root": str(get_workspace_root(skill_dir)),
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        elif args.bootstrap:
            print(
                json.dumps(
                    ensure_workspace(skill_dir, username=args.username),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            parser_workspace.print_help()
            sys.exit(1)

    elif args.command == "home":
        skill_dir = _skill_dir()
        ensure_workspace(skill_dir, username=args.username)
        home_service = HomeService.from_skill_dir(skill_dir, username=args.username)

        if args.dashboard:
            print(
                json.dumps(home_service.get_dashboard(), ensure_ascii=False, indent=2)
            )
        elif args.resume:
            print(
                json.dumps(
                    home_service.get_resume_target(),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        elif args.recommend:
            print(
                json.dumps(
                    home_service.get_recommendation(),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            parser_home.print_help()
            sys.exit(1)

    elif args.command == "learning":
        skill_dir = _skill_dir()
        ensure_workspace(skill_dir, username=args.username)
        learning_service = LearningService.from_skill_dir(
            skill_dir, username=args.username
        )

        if args.catalog:
            print(
                json.dumps(
                    learning_service.get_catalog(),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        elif args.category:
            print(
                json.dumps(
                    learning_service.get_category(args.category),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        elif args.recommend_course:
            print(
                json.dumps(
                    learning_service.recommend_course(),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        elif args.lesson_meta and args.course:
            print(
                json.dumps(
                    learning_service.get_lesson_meta(args.course),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        elif args.lesson_panel and args.course:
            print(
                json.dumps(
                    learning_service.get_lesson_panel(args.course),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        elif args.code_meta and args.course:
            print(
                json.dumps(
                    learning_service.get_code_meta(args.course),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        elif args.code_outline and args.course:
            print(
                json.dumps(
                    learning_service.get_code_outline(args.course),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        elif args.complete and args.course:
            print(
                json.dumps(
                    learning_service.complete_course(args.course),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            parser_learning.print_help()
            sys.exit(1)

    elif args.command == "practice":
        skill_dir = _skill_dir()
        ensure_workspace(skill_dir, username=args.username)
        practice_service = PracticeService.from_skill_dir(
            skill_dir, username=args.username
        )

        if args.entry_points:
            print(
                json.dumps(
                    practice_service.get_entry_points(),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        elif args.resume:
            print(
                json.dumps(
                    practice_service.get_resume_target(),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        elif args.blueprint:
            print(
                json.dumps(
                    practice_service.build_blueprint(
                        course_id=args.course,
                        mode=args.mode or "current",
                        focus_tag=args.focus_tag,
                    ),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        elif args.record_result:
            payload = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
            print(
                json.dumps(
                    practice_service.record_result(payload),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        elif args.review_mistakes:
            print(
                json.dumps(
                    practice_service.list_open_mistakes(course_id=args.course),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        elif args.summary:
            print(
                json.dumps(
                    practice_service.get_practice_summary(),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            parser_practice.print_help()
            sys.exit(1)

    elif args.command == "profile":
        skill_dir = _skill_dir()
        ensure_workspace(skill_dir, username=args.username)
        profile_service = ProfileService.from_skill_dir(
            skill_dir, username=args.username
        )

        if args.summary:
            print(
                json.dumps(
                    profile_service.get_summary(),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        elif args.progress:
            print(
                json.dumps(
                    profile_service.get_progress(),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        elif args.mistakes:
            print(
                json.dumps(
                    profile_service.get_mistakes(),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        elif args.exam_history:
            print(
                json.dumps(
                    profile_service.get_exam_history(),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        elif args.templates:
            print(
                json.dumps(
                    profile_service.get_templates(),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            parser_profile.print_help()
            sys.exit(1)


if __name__ == "__main__":
    main()
