#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prompt-Learning Skill 真实基准测试脚本
通过调用 iFlow CLI 执行测试用例
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional


class RealBenchmarkEvaluator:
    """真实基准测试评估器"""

    def __init__(self, evals_file: str, output_dir: str):
        self.evals_file = evals_file
        self.output_dir = output_dir
        self.test_cases = []
        self.results = []
        self.use_manual_mode = True  # 默认使用手动模式

    def load_test_cases(self) -> None:
        """加载测试用例"""
        with open(self.evals_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.test_cases = data['evals']
        print(f"✓ 已加载 {len(self.test_cases)} 个测试用例")

    def execute_with_iflow(self, prompt: str) -> Optional[str]:
        """
        使用 iFlow CLI 执行提示词

        Args:
            prompt: 用户提示词

        Returns:
            AI 输出，如果执行失败则返回 None
        """
        try:
            # 尝试调用 iFlow CLI
            cmd = ['iflow', '-p', prompt, '--stream']
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(self.evals_file))))
            )
            if result.returncode == 0:
                return result.stdout
            else:
                print(f"  ⚠️  iFlow CLI 执行失败: {result.stderr}")
                return None
        except FileNotFoundError:
            print(f"  ⚠️  未找到 iFlow CLI，切换到手动模式")
            self.use_manual_mode = True
            return None
        except Exception as e:
            print(f"  ⚠️  执行出错: {str(e)}")
            return None

    def get_manual_output(self, test_case: Dict[str, Any]) -> str:
        """
        手动获取输出（用户需要手动执行并提供输出）

        Args:
            test_case: 测试用例

        Returns:
            AI 输出
        """
        print(f"\n{'='*80}")
        print(f"测试用例 {test_case['id']}: {test_case['name']}")
        print(f"类别: {test_case['category']}, 难度: {test_case['difficulty']}")
        print(f"{'='*80}")
        print(f"\n提示词:")
        print(f"{test_case['prompt']}")
        print(f"\n预期输出:")
        print(f"{test_case['expected_output']}")
        print(f"\n{'='*80}")

        print(f"\n请使用以下方式执行测试:")
        print(f"  方式 1: iflow -p \"{test_case['prompt']}\" --stream")
        print(f"  方式 2: 在 iFlow 交互会话中输入上述提示词")
        print(f"\n然后将 AI 的输出粘贴到下面（或输入 'skip' 跳过此测试）:")

        output_lines = []
        print(f"\n--- 开始粘贴输出 (输入空行结束) ---")
        while True:
            try:
                line = input()
                if line.strip() == '':
                    break
                output_lines.append(line)
            except EOFError:
                break

        output = '\n'.join(output_lines)
        if output.strip().lower() == 'skip':
            return ""

        return output

    def evaluate_output(self, test_case: Dict[str, Any], output: str) -> Dict[str, Any]:
        """
        评估输出质量

        Args:
            test_case: 测试用例
            output: AI 输出

        Returns:
            评估结果
        """
        expected = test_case['expected_output']
        result = {
            'test_id': test_case['id'],
            'test_name': test_case['name'],
            'category': test_case['category'],
            'difficulty': test_case['difficulty'],
            'prompt': test_case['prompt'],
            'expected': expected,
            'output': output,
            'passed': False,
            'score': 0,
            'dimensions': {},
            'issues': [],
            'suggestions': [],
            'execution_mode': 'manual' if self.use_manual_mode else 'automatic'
        }

        # 如果输出为空，标记为跳过
        if not output or output.strip() == '':
            result['passed'] = False
            result['score'] = 0
            result['issues'].append('测试被跳过或输出为空')
            result['suggestions'].append('请提供有效的输出')
            result['dimensions'] = {'完整性': 0, '相关性': 0, '结构性': 0, '具体性': 0}
            return result

        # 评估维度
        dimensions = self._evaluate_dimensions(output, expected)
        result['dimensions'] = dimensions

        # 计算总分（0-100）
        total_score = sum(dimensions.values()) / len(dimensions)
        result['score'] = round(total_score, 1)

        # 判断是否通过（分数 >= 70）
        result['passed'] = total_score >= 70

        # 生成问题和建议
        issues, suggestions = self._generate_feedback(output, expected, dimensions)
        result['issues'] = issues
        result['suggestions'] = suggestions

        return result

    def _evaluate_dimensions(self, output: str, expected: str) -> Dict[str, float]:
        """评估输出在各个维度的表现"""
        dimensions = {}

        # 1. 完整性（30分）
        output_length = len(output)
        expected_length = len(expected)
        if output_length > 0:
            completeness = min(30, (output_length / max(expected_length, 1)) * 30)
        else:
            completeness = 0
        dimensions['完整性'] = round(completeness, 1)

        # 2. 相关性（30分）
        relevant_keywords = self._extract_keywords(expected)
        matched_keywords = sum(1 for kw in relevant_keywords if kw.lower() in output.lower())
        relevance = (matched_keywords / len(relevant_keywords)) * 30 if relevant_keywords else 15
        dimensions['相关性'] = round(relevance, 1)

        # 3. 结构性（20分）
        has_structure = any([
            '\n' in output,
            '步骤' in output or 'step' in output.lower(),
            '1.' in output or '2.' in output or '3.' in output,
            '•' in output or '*' in output or '-' in output,
            '【' in output or '（' in output,
            '##' in output or '###' in output,  # Markdown 标题
            '```' in output  # 代码块
        ])
        dimensions['结构性'] = 20 if has_structure else 10

        # 4. 具体性（20分）
        has_examples = any([
            '示例' in output or 'example' in output.lower(),
            '例如' in output or 'for instance' in output.lower(),
            '如：' in output or 'such as' in output.lower(),
            '示例1' in output or '示例2' in output,
            'Example' in output
        ])
        dimensions['具体性'] = 20 if has_examples else 10

        return dimensions

    def _extract_keywords(self, text: str) -> List[str]:
        """从文本中提取关键词"""
        keywords = []
        important_words = [
            '结构化', '教程', '定义', '原则', '示例', '对比',
            '分析', '问题', '改进', '建议', '评估', '评分',
            '角色', '任务', '要求', '步骤', '推理', '分类',
            '格式', 'JSON', '分解', '约束', '优化', '组合',
            '上下文', '调试', '维度', '优点', '不足',
            '维度', '清晰度', '完整性', '具体性', '约束性',
            '可执行性', '有效性', '角色扮演', '思维链',
            '少样本', '输出格式', '任务分解', '迭代优化',
            '模式组合', '技术选型', '架构设计', '性能指标'
        ]
        for word in important_words:
            if word in text:
                keywords.append(word)
        return keywords if keywords else ['内容']

    def _generate_feedback(self, output: str, expected: str, dimensions: Dict[str, float]) -> tuple:
        """生成问题和建议"""
        issues = []
        suggestions = []

        # 根据各个维度的得分生成反馈
        if dimensions['完整性'] < 20:
            issues.append('输出内容不够完整')
            suggestions.append('增加更多细节和深度')

        if dimensions['相关性'] < 20:
            issues.append('输出与预期不够相关')
            suggestions.append('更仔细地理解用户需求')

        if dimensions['结构性'] < 15:
            issues.append('输出缺乏清晰的结构')
            suggestions.append('使用标题、列表、步骤等组织内容')

        if dimensions['具体性'] < 15:
            issues.append('输出缺乏具体示例')
            suggestions.append('添加实际示例和案例')

        # 如果没有问题，给出正面反馈
        if not issues:
            issues.append('无明显问题')
            suggestions.append('继续保持高质量输出')

        return issues, suggestions

    def generate_report(self) -> str:
        """生成测试报告"""
        report = []
        report.append("=" * 80)
        report.append("Prompt-Learning Skill 基准测试报告")
        report.append("=" * 80)
        report.append(f"\n测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"测试用例总数: {len(self.results)}")
        report.append(f"执行模式: {'手动模式' if self.use_manual_mode else '自动模式'}")

        # 统计结果
        skipped = sum(1 for r in self.results if r['score'] == 0)
        executed = len(self.results) - skipped
        passed = sum(1 for r in self.results if r['passed'])
        failed = executed - passed
        pass_rate = (passed / executed * 100) if executed > 0 else 0
        avg_score = sum(r['score'] for r in self.results if r['score'] > 0) / executed if executed > 0 else 0

        report.append(f"\n总体统计:")
        report.append(f"  已执行: {executed} 个")
        report.append(f"  跳过: {skipped} 个")
        report.append(f"  通过: {passed} 个")
        report.append(f"  失败: {failed} 个")
        report.append(f"  通过率: {pass_rate:.1f}%")
        report.append(f"  平均得分: {avg_score:.1f}/100")

        # 按难度统计
        report.append(f"\n按难度统计:")
        for difficulty in ['初级', '中级', '高级']:
            cases = [r for r in self.results if r['difficulty'] == difficulty]
            if cases:
                executed_cases = [r for r in cases if r['score'] > 0]
                if executed_cases:
                    avg = sum(r['score'] for r in executed_cases) / len(executed_cases)
                    passed_count = sum(1 for r in executed_cases if r['passed'])
                    report.append(f"  {difficulty}: {len(executed_cases)}/{len(cases)} 个已执行, 平均 {avg:.1f} 分, 通过 {passed_count} 个")

        # 按类别统计
        report.append(f"\n按类别统计:")
        categories = {}
        for r in self.results:
            cat = r['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(r)
        for cat, cases in sorted(categories.items()):
            executed_cases = [r for r in cases if r['score'] > 0]
            if executed_cases:
                avg = sum(r['score'] for r in executed_cases) / len(executed_cases)
                passed_count = sum(1 for r in executed_cases if r['passed'])
                report.append(f"  {cat}: {len(executed_cases)}/{len(cases)} 个已执行, 平均 {avg:.1f} 分, 通过 {passed_count} 个")

        # 详细结果
        report.append(f"\n" + "=" * 80)
        report.append("详细测试结果")
        report.append("=" * 80)

        for i, result in enumerate(self.results, 1):
            if result['score'] == 0:
                status = "⊘ 跳过"
            elif result['passed']:
                status = "✓ 通过"
            else:
                status = "✗ 失败"

            report.append(f"\n{i}. {result['test_name']} [{result['category']}/{result['difficulty']}] {status}")
            report.append(f"   得分: {result['score']}/100")
            report.append(f"   提示词: {result['prompt'][:80]}...")
            report.append(f"   维度得分: {result['dimensions']}")

            if not result['passed'] and result['score'] > 0:
                report.append(f"   问题: {', '.join(result['issues'])}")
                report.append(f"   建议: {', '.join(result['suggestions'])}")

        # 改进建议
        report.append(f"\n" + "=" * 80)
        report.append("总体改进建议")
        report.append("=" * 80)

        if executed == 0:
            report.append("\n⚠️  没有执行任何测试用例")
            report.append("  请手动执行测试并提供输出")
        elif pass_rate < 70:
            report.append(f"\n⚠️  当前通过率较低 ({pass_rate:.1f}%)，建议重点关注以下方面:")
            report.append("  1. 加强对用户需求的理解能力")
            report.append("  2. 提高输出的完整性和深度")
            report.append("  3. 改善输出内容的结构化程度")
            report.append("  4. 增加具体示例和案例分析")
        elif pass_rate < 90:
            report.append(f"\n✓ 总体表现良好，建议进一步优化:")
            report.append("  1. 针对失败用例进行专项改进")
            report.append("  2. 提高对复杂场景的处理能力")
            report.append("  3. 增强输出的专业性")
        else:
            report.append("\n✓✓ 优秀！继续保持高质量输出")

        report.append(f"\n" + "=" * 80)
        report.append("报告结束")
        report.append("=" * 80)

        return "\n".join(report)

    def save_report(self, report: str, output_file: str) -> None:
        """保存报告到文件"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✓ 报告已保存到: {output_file}")

    def save_json_report(self, output_file: str) -> None:
        """保存 JSON 格式的报告"""
        executed = sum(1 for r in self.results if r['score'] > 0)
        passed = sum(1 for r in self.results if r['passed'])
        failed = executed - passed

        report_data = {
            'timestamp': datetime.now().isoformat(),
            'execution_mode': 'manual' if self.use_manual_mode else 'automatic',
            'total_cases': len(self.results),
            'executed': executed,
            'skipped': len(self.results) - executed,
            'passed': passed,
            'failed': failed,
            'pass_rate': (passed / executed * 100) if executed > 0 else 0,
            'average_score': sum(r['score'] for r in self.results if r['score'] > 0) / executed if executed > 0 else 0,
            'results': self.results
        }
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        print(f"✓ JSON 报告已保存到: {output_file}")

    def run(self):
        """运行基准测试"""
        # 加载测试用例
        self.load_test_cases()

        print(f"\n开始执行基准测试...")
        print(f"{'='*80}")

        # 检查是否使用自动模式
        if not self.use_manual_mode:
            print(f"\n尝试使用自动模式...")
            print(f"注意：自动模式需要安装 iFlow CLI")
            print(f"如果自动模式失败，将切换到手动模式\n")

        # 执行测试
        for i, test_case in enumerate(self.test_cases, 1):
            print(f"\n[{i}/{len(self.test_cases)}] 测试: {test_case['name']}")

            # 获取输出
            if not self.use_manual_mode:
                print(f"  自动执行中...")
                output = self.execute_with_iflow(test_case['prompt'])

                # 如果自动执行失败，切换到手动模式
                if output is None:
                    self.use_manual_mode = True
                    output = self.get_manual_output(test_case)
            else:
                output = self.get_manual_output(test_case)

            # 评估输出
            print(f"  评估输出...")
            result = self.evaluate_output(test_case, output)
            self.results.append(result)

            # 显示结果
            if result['score'] == 0:
                status = "⊘ 跳过"
            elif result['passed']:
                status = "✓ 通过"
            else:
                status = "✗ 失败"
            print(f"  结果: {status} (得分: {result['score']}/100)")

        # 生成报告
        print(f"\n{'='*80}")
        print(f"\n生成测试报告...")
        report = self.generate_report()

        # 保存报告
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = os.path.join(self.output_dir, f'benchmark_report_{timestamp}.txt')
        json_report_file = os.path.join(self.output_dir, f'benchmark_report_{timestamp}.json')

        self.save_report(report, report_file)
        self.save_json_report(json_report_file)

        # 打印报告摘要
        print(f"\n{'='*80}")
        print(report)
        print(f"\n{'='*80}")


def main():
    """主函数"""
    # 设置路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    evals_file = os.path.join(script_dir, 'evals.json')
    output_dir = os.path.join(script_dir, 'results')

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == '--auto':
        print("尝试使用自动模式（需要 iFlow CLI）")
        evaluator = RealBenchmarkEvaluator(evals_file, output_dir)
        evaluator.use_manual_mode = False
    else:
        print("使用手动模式")
        print("提示：使用 --auto 参数尝试自动模式")
        evaluator = RealBenchmarkEvaluator(evals_file, output_dir)

    # 运行基准测试
    evaluator.run()


if __name__ == '__main__':
    main()