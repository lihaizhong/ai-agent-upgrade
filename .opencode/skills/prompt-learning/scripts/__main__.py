"""
提示词工程学习系统 - CLI 入口
提供命令行接口供 AI Agent 调用
"""

import argparse
import json
import os
import subprocess
import sys

from .engine import PromptLearningEngine
from .exam import ExamEngine


def resolve_username(explicit_username: str | None) -> str:
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


def build_generate_workflow(topic: str | None) -> dict:
    """返回提示词生成固定流程。"""
    return {
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
    }


def build_generate_checklist(topic: str | None) -> dict:
    """返回提示词审查清单。"""
    return {
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


def validate_generate_slots(payload: dict, required_slots: list[str]) -> dict:
    """校验生成模式所需槽位。"""
    missing = []
    empty = []

    for slot in required_slots:
        if slot not in payload:
            missing.append(slot)
            continue
        value = payload.get(slot)
        if value is None or value == "" or value == [] or value == {}:
            empty.append(slot)

    return {
        "valid": not missing and not empty,
        "missing_slots": missing,
        "empty_slots": empty,
    }


def validate_generate_draft(payload: dict, checklist: list[str]) -> dict:
    """校验提示词草稿结构和审查结果。"""
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

    return {
        "valid": not errors,
        "failed_items": failed_items,
        "errors": errors,
    }


def main():
    parser = argparse.ArgumentParser(description="提示词工程学习系统")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 模式选择
    subparsers.add_parser("mode", help="获取模式选择菜单")

    # 学习模式
    parser_learn = subparsers.add_parser("learn", help="学习模式")
    parser_learn.add_argument("--course", type=int, help="课程编号 (1-17)")
    parser_learn.add_argument("--list", action="store_true", help="列出所有课程")
    parser_learn.add_argument("--category", type=str, help="按类别列出课程")
    parser_learn.add_argument("--content", action="store_true", help="获取课程内容")
    parser_learn.add_argument("--code", action="store_true", help="获取代码实现")
    parser_learn.add_argument("--next", action="store_true", help="获取下一课推荐")
    parser_learn.add_argument("--complete", action="store_true", help="标记课程完成")
    parser_learn.add_argument(
        "--practice-type", action="store_true", help="获取练习题类型"
    )
    parser_learn.add_argument(
        "--practice-blueprint", action="store_true", help="获取稳定练习题蓝图"
    )

    # 考试模式
    parser_exam = subparsers.add_parser("exam", help="考试模式")
    parser_exam.add_argument("--structure", action="store_true", help="获取考试结构")
    parser_exam.add_argument("--blueprint", action="store_true", help="获取考试蓝图")
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
    parser_exam.add_argument("--question", type=int, help="题号")
    parser_exam.add_argument("--difficulty", type=str, help="难度")
    parser_exam.add_argument("--answer", type=str, help="用户答案")
    parser_exam.add_argument("--username", type=str, help="用户名")

    # 状态管理
    parser_state = subparsers.add_parser("state", help="状态管理")
    parser_state.add_argument("--show", action="store_true", help="显示当前状态")
    parser_state.add_argument("--recommend", action="store_true", help="获取学习推荐")

    # 提示词生成
    parser_gen = subparsers.add_parser("generate", help="提示词生成模式")
    parser_gen.add_argument("--topic", type=str, help="主题")
    parser_gen.add_argument(
        "--workflow", action="store_true", help="获取提示词生成固定流程"
    )
    parser_gen.add_argument(
        "--review-checklist", action="store_true", help="获取提示词审查清单"
    )
    parser_gen.add_argument(
        "--validate-slots", action="store_true", help="校验提示词生成必填槽位"
    )
    parser_gen.add_argument(
        "--validate-draft", action="store_true", help="校验提示词草稿和审查结果"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "mode":
        print(
            json.dumps(
                {
                    "modes": [
                        {
                            "id": "learn",
                            "name": "学习模式",
                            "desc": "系统学习提示词技术，互动问答",
                        },
                        {
                            "id": "exam",
                            "name": "考试模式",
                            "desc": "挑战自我，即时反馈评分",
                        },
                        {
                            "id": "generate",
                            "name": "提示词生成",
                            "desc": "头脑风暴生成提示词",
                        },
                    ]
                },
                ensure_ascii=False,
                indent=2,
            )
        )

    elif args.command == "learn":
        engine = PromptLearningEngine()

        if args.list:
            courses = engine.get_course_list_by_category()
            print(json.dumps(courses, ensure_ascii=False, indent=2, default=str))

        elif args.category:
            courses = engine.get_courses_by_category(args.category)
            print(json.dumps(courses, ensure_ascii=False, indent=2, default=str))

        elif args.content and args.course:
            content = engine.get_course_content(args.course)
            print(
                json.dumps(
                    {"course_id": args.course, "content": content},
                    ensure_ascii=False,
                    indent=2,
                )
            )

        elif args.code and args.course:
            code = engine.get_code_implementation(args.course)
            print(
                json.dumps(
                    {"course_id": args.course, "code": code},
                    ensure_ascii=False,
                    indent=2,
                )
            )

        elif args.next:
            rec = engine.get_next_course_recommendation()
            print(json.dumps(rec, ensure_ascii=False, indent=2))

        elif args.complete and args.course:
            engine.state.complete_course(
                f"{args.course:02d}-{engine._load_deps()[args.course]['name']}"
            )
            print(
                json.dumps(
                    {"status": "completed", "course": args.course},
                    ensure_ascii=False,
                    indent=2,
                )
            )

        elif args.practice_type and args.course:
            qtype = engine.select_question_type(args.course)
            print(
                json.dumps(
                    {"course_id": args.course, "question_type": qtype},
                    ensure_ascii=False,
                    indent=2,
                )
            )

        elif args.practice_blueprint and args.course:
            blueprint = engine.build_practice_blueprint(args.course)
            print(json.dumps(blueprint, ensure_ascii=False, indent=2))

    elif args.command == "exam":
        exam = ExamEngine()

        if args.structure:
            print(
                json.dumps(exam.generate_exam_structure(), ensure_ascii=False, indent=2)
            )

        elif args.blueprint:
            print(json.dumps(exam.build_exam_blueprint(), ensure_ascii=False, indent=2))

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
            print(json.dumps(exam.validate_mc_question(question), ensure_ascii=False, indent=2))

        elif args.validate_fill:
            question = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
            print(json.dumps(exam.validate_fill_question(question), ensure_ascii=False, indent=2))

        elif args.validate_essay:
            question = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
            print(json.dumps(exam.validate_essay_question(question), ensure_ascii=False, indent=2))

        elif args.validate_paper:
            questions = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else []
            print(json.dumps(exam.validate_exam_paper(questions), ensure_ascii=False, indent=2))

        elif args.report:
            questions = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else []
            report_path = exam.generate_report(
                questions, [], [], resolve_username(args.username)
            )
            print(
                json.dumps({"report_path": report_path}, ensure_ascii=False, indent=2)
            )
        else:
            parser_exam.print_help()
            sys.exit(1)

    elif args.command == "state":
        engine = PromptLearningEngine()

        if args.show:
            print(json.dumps(engine.state.state, ensure_ascii=False, indent=2))

        elif args.recommend:
            rec = engine.state.get_recommended_path()
            print(json.dumps(rec, ensure_ascii=False, indent=2))

    elif args.command == "generate":
        if args.workflow:
            print(json.dumps(build_generate_workflow(args.topic), ensure_ascii=False, indent=2))
        elif args.review_checklist:
            print(
                json.dumps(
                    build_generate_checklist(args.topic), ensure_ascii=False, indent=2
                )
            )
        elif args.validate_slots:
            payload = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
            required_slots = build_generate_workflow(args.topic)["required_slots"]
            print(
                json.dumps(
                    validate_generate_slots(payload, required_slots),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        elif args.validate_draft:
            payload = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
            checklist = build_generate_checklist(args.topic)["checklist"]
            print(
                json.dumps(
                    validate_generate_draft(payload, checklist),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            print(
                json.dumps(
                    {
                        "status": "ready",
                        "topic": args.topic,
                        "message": "提示词生成模式已就绪，请描述你的需求",
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )


if __name__ == "__main__":
    main()
