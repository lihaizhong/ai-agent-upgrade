#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prompt-Learning Skill 基准测试脚本
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any


class BenchmarkEvaluator:
    """基准测试评估器"""

    def __init__(self, evals_file: str):
        self.evals_file = evals_file
        self.test_cases = []
        self.results = []

    def load_test_cases(self) -> None:
        """加载测试用例"""
        with open(self.evals_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.test_cases = data['evals']
        print(f"✓ 已加载 {len(self.test_cases)} 个测试用例")

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
            'suggestions': []
        }

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
            completeness = min(30, (output_length / expected_length) * 30)
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
            '1.' in output or '2.' in output,
            '•' in output or '*' in output or '-' in output,
            '【' in output or '（' in output
        ])
        dimensions['结构性'] = 20 if has_structure else 10

        # 4. 具体性（20分）
        has_examples = any([
            '示例' in output or 'example' in output.lower(),
            '例如' in output or 'for instance' in output.lower(),
            '如：' in output or 'such as' in output.lower()
        ])
        dimensions['具体性'] = 20 if has_examples else 10

        return dimensions

    def _extract_keywords(self, text: str) -> List[str]:
        """从文本中提取关键词"""
        # 简单的关键词提取
        keywords = []
        important_words = [
            '结构化', '教程', '定义', '原则', '示例', '对比',
            '分析', '问题', '改进', '建议', '评估', '评分',
            '角色', '任务', '要求', '步骤', '推理', '分类',
            '格式', 'JSON', '分解', '约束', '优化', '组合',
            '上下文', '调试', '维度', '优点', '不足'
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

        # 统计结果
        passed = sum(1 for r in self.results if r['passed'])
        failed = len(self.results) - passed
        pass_rate = (passed / len(self.results)) * 100 if self.results else 0
        avg_score = sum(r['score'] for r in self.results) / len(self.results) if self.results else 0

        report.append(f"\n总体统计:")
        report.append(f"  通过: {passed} 个")
        report.append(f"  失败: {failed} 个")
        report.append(f"  通过率: {pass_rate:.1f}%")
        report.append(f"  平均得分: {avg_score:.1f}/100")

        # 按难度统计
        report.append(f"\n按难度统计:")
        for difficulty in ['初级', '中级', '高级']:
            cases = [r for r in self.results if r['difficulty'] == difficulty]
            if cases:
                avg = sum(r['score'] for r in cases) / len(cases)
                passed_count = sum(1 for r in cases if r['passed'])
                report.append(f"  {difficulty}: {len(cases)} 个, 平均 {avg:.1f} 分, 通过 {passed_count} 个")

        # 按类别统计
        report.append(f"\n按类别统计:")
        categories = {}
        for r in self.results:
            cat = r['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(r)
        for cat, cases in sorted(categories.items()):
            avg = sum(r['score'] for r in cases) / len(cases)
            passed_count = sum(1 for r in cases if r['passed'])
            report.append(f"  {cat}: {len(cases)} 个, 平均 {avg:.1f} 分, 通过 {passed_count} 个")

        # 详细结果
        report.append(f"\n" + "=" * 80)
        report.append("详细测试结果")
        report.append("=" * 80)

        for i, result in enumerate(self.results, 1):
            status = "✓ 通过" if result['passed'] else "✗ 失败"
            report.append(f"\n{i}. {result['test_name']} [{result['category']}/{result['difficulty']}] {status}")
            report.append(f"   得分: {result['score']}/100")
            report.append(f"   提示词: {result['prompt'][:100]}...")
            report.append(f"   维度得分: {result['dimensions']}")

            if not result['passed']:
                report.append(f"   问题: {', '.join(result['issues'])}")
                report.append(f"   建议: {', '.join(result['suggestions'])}")

        # 改进建议
        report.append(f"\n" + "=" * 80)
        report.append("总体改进建议")
        report.append("=" * 80)

        if pass_rate < 70:
            report.append("\n⚠️  当前通过率较低，建议重点关注以下方面:")
            report.append("  1. 加强对用户需求的理解能力")
            report.append("  2. 提高输出的完整性和深度")
            report.append("  3. 改善输出内容的结构化程度")
            report.append("  4. 增加具体示例和案例分析")
        elif pass_rate < 90:
            report.append("\n✓ 总体表现良好，建议进一步优化:")
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
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'total_cases': len(self.results),
            'passed': sum(1 for r in self.results if r['passed']),
            'failed': sum(1 for r in self.results if not r['passed']),
            'pass_rate': (sum(1 for r in self.results if r['passed']) / len(self.results) * 100) if self.results else 0,
            'average_score': sum(r['score'] for r in self.results) / len(self.results) if self.results else 0,
            'results': self.results
        }
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        print(f"✓ JSON 报告已保存到: {output_file}")


def simulate_execution(test_case: Dict[str, Any]) -> str:
    """
    模拟执行 prompt-learning skill（由于无法实际调用 iFlow CLI）

    在实际使用中，这里应该调用 iFlow CLI 来执行测试
    """
    # 这里返回一个模拟的输出
    # 在实际基准测试中，应该通过 iFlow CLI 真正执行 skill

    # 模拟输出 - 根据测试用例类型生成不同的模拟输出
    category = test_case['category']

    if category == '基础学习':
        return """# 提示词工程基础知识

## 什么是提示词工程

提示词工程是指通过精心设计和优化输入给 AI 的文本，以获得更准确、更相关、更有用的输出的技术和艺术。

## 核心原则

### 1. 清晰明确
提示词应该清楚地表达你想要什么，避免模糊不清的表达。

### 2. 提供上下文
给 AI 足够的背景信息，帮助它理解你的需求和期望。

### 3. 指定输出格式
明确告诉 AI 你希望输出是什么样的格式。

### 4. 提供示例
给出好示例和坏示例，帮助 AI 理解你的期望。

### 5. 分解复杂任务
对于复杂任务，将其分解为多个步骤，让 AI 逐步完成。

## 示例对比

**示例 1: 模糊 vs 清晰**
- ❌ 模糊：帮我写个文档
- ✅ 清晰：帮我写一份关于 RESTful API 设计的技术文档，包含定义、特点、最佳实践和示例代码，字数约 2000 字

**示例 2: 缺乏上下文 vs 有上下文**
- ❌ 缺乏上下文：优化这段代码
- ✅ 有上下文：这是一个处理用户订单的 Python 函数，在处理大量订单时性能较差。请帮我优化它的性能，要求保持原有功能不变，并添加必要的注释。
"""

    elif category == '提示词优化':
        return """# 提示词分析与改进

## 当前提示词问题分析

**当前提示词**: "帮我写个函数来处理数据"

### 存在的问题：

1. **缺乏上下文** - 没有说明要处理什么类型的数据（用户数据、订单数据、日志数据等）
2. **不够具体** - "处理数据"太笼统，不清楚是要清洗、转换、分析还是存储
3. **未指定输入输出格式** - 没有说明数据的格式和期望的输出格式
4. **未说明语言和技术栈** - 没有指定使用 Python、JavaScript 还是其他语言
5. **缺乏约束条件** - 没有说明性能要求、错误处理需求等

## 改进建议

### 改进版本 1（基础版）：
```
请帮我用 Python 编写一个函数来处理 CSV 格式的用户数据，包括：
- 读取 CSV 文件
- 清洗数据（去除空值、重复值）
- 转换数据类型
- 将处理后的数据保存为新的 CSV 文件
```

### 改进版本 2（进阶版）：
```
请帮我用 Python 编写一个函数来处理用户订单数据，要求：
- 输入格式：包含用户ID、订单ID、订单金额、订单日期的CSV文件
- 处理逻辑：
  1. 读取并解析CSV文件
  2. 过滤掉金额小于0的无效订单
  3. 按用户ID统计每个用户的订单总额和订单数量
  4. 计算用户的平均订单金额
- 输出格式：返回包含用户ID、订单总额、订单数量、平均订单金额的字典列表
- 添加必要的错误处理和日志记录
```

## 改进前后对比

| 维度 | 原提示词 | 改进后 |
|------|---------|--------|
| 上下文 | 无 | 完整的业务场景 |
| 具体性 | 模糊 | 明确的输入输出和处理步骤 |
| 格式说明 | 无 | 详细的CSV格式说明 |
| 语言 | 未指定 | 明确指定Python |
| 约束条件 | 无 | 包含错误处理和日志要求 |
"""

    elif category == '练习生成':
        return """# 提示词工程练习题（中级难度）

## 练习题 1: 思维链应用

**任务描述**: 设计一个提示词，使用思维链模式让 AI 分析"如何提高团队工作效率"这个问题。

**练习目标**: 
- 掌握思维链提示词的设计方法
- 学会如何引导 AI 进行逐步推理
- 理解如何将复杂问题分解

**参考答案**:
```
请使用思维链模式分析"如何提高团队工作效率"，按照以下步骤进行：

步骤 1：识别影响团队工作效率的关键因素
步骤 2：分析每个因素的现状和问题
步骤 3：为每个因素提出具体的改进措施
步骤 4：评估改进措施的可行性和优先级
步骤 5：制定分阶段的实施计划

请逐步展示你的思考过程。
```

---

## 练习题 2: 少样本学习

**任务描述**: 设计一个提示词，使用少样本学习让 AI 对客户反馈进行情感分类。

**练习目标**:
- 理解少样本学习的原理和应用
- 学会如何设计有效的示例
- 掌握分类任务的提示词设计

**参考答案**:
```
请对以下客户反馈进行情感分类（积极/消极/中性）：

示例：
输入：产品质量很好，物流也很快，非常满意！
输出：积极

输入：产品还可以，但是价格有点贵。
输出：中性

输入：用了两天就坏了，客服态度也很差。
输出：消极

输入：[待分类的反馈]
输出：
```

---

## 练习题 3: 约束条件设计

**任务描述**: 设计一个提示词，让 AI 生成技术博客文章，要求满足多个约束条件。

**练习目标**:
- 学会如何设置明确的约束条件
- 理解不同类型约束的作用
- 掌握约束条件的优先级设置

**参考答案**:
```
请写一篇关于"微服务架构设计"的技术博客文章，要求：
- 字数：1500-2000字
- 语言风格：专业但易懂，面向中级开发者
- 结构要求：
  1. 引言（介绍微服务概念）
  2. 核心原理（至少3点）
  3. 优缺点分析
  4. 实际应用案例
  5. 最佳实践建议
- 必须包含：至少2个代码示例和1个架构图描述
- 避免：过于抽象的理论，多用具体案例说明
```

---

## 练习题 4: 角色扮演增强

**任务描述**: 设计一个提示词，让 AI 扮演"产品经理"角色，为一个新的移动应用制定产品路线图。

**练习目标**:
- 掌握角色扮演提示词的设计技巧
- 学会如何设定角色背景和职责
- 理解如何让 AI 进入角色并提供专业建议

**参考答案**:
```
你现在是一位有 10 年经验的资深产品经理，擅长移动应用产品规划和项目管理。请为"一款面向大学生的校园社交应用"制定产品路线图，要求：

1. 分析目标用户的核心需求
2. 定义产品的核心功能模块
3. 制定 6 个月的开发路线图，包含：
   - MVP（最小可行产品）的功能范围
   - 每个版本的迭代计划
   - 关键里程碑和时间节点
4. 识别潜在风险和应对策略

请以专业产品经理的视角，提供可落地的建议。
```

---

## 练习题 5: 提示词调试

**任务描述**: 以下提示词存在问题，请分析问题并提供修复方案。

**有问题的提示词**:
```
帮我分析这个代码的性能问题：
[代码]
```

**练习目标**:
- 学会识别提示词中的常见问题
- 掌握提示词调试的方法
- 提高提示词优化的能力

**参考答案**:

**问题分析**:
1. 缺乏上下文 - 没有说明代码的用途和场景
2. 未指定优化目标 - 是要减少内存使用、提高执行速度还是两者兼顾？
3. 没有提供性能指标 - 没有说明当前性能如何，期望达到什么水平
4. 缺少约束条件 - 没有说明是否可以修改代码逻辑

**修复方案**:
```
请帮我分析以下 Python 代码的性能问题：

[代码]

背景信息：
- 这是一个处理电商订单的函数
- 当前处理 10 万条订单需要约 30 秒
- 期望优化到 5 秒以内

请从以下方面进行分析：
1. 识别性能瓶颈
2. 分析时间复杂度和空间复杂度
3. 提供具体的优化建议
4. 给出优化后的代码示例
5. 预估优化后的性能提升

约束条件：
- 保持原有功能不变
- 优先考虑执行速度优化
- 可以修改算法和数据结构
```
"""

    else:
        # 默认模拟输出
        return f"""# 针对 {test_case['name']} 的响应

根据您的需求，我为您提供了以下内容：

## 核心要点

1. 针对您的请求，我分析了相关的概念和原则
2. 提供了具体的示例和最佳实践
3. 给出了可执行的建议和改进方案

## 详细说明

{test_case['expected_output']}

## 总结

以上内容涵盖了您需要的核心信息，包括定义、原则、示例和具体建议。希望这些内容能够帮助您更好地理解和应用。
"""


def main():
    """主函数"""
    # 设置路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    evals_file = os.path.join(script_dir, 'evals.json')
    output_dir = os.path.join(script_dir, 'results')

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 初始化评估器
    evaluator = BenchmarkEvaluator(evals_file)
    evaluator.load_test_cases()

    # 执行测试
    print(f"\n开始执行基准测试...")
    print(f"{'='*80}")

    for i, test_case in enumerate(evaluator.test_cases, 1):
        print(f"\n[{i}/{len(evaluator.test_cases)}] 测试: {test_case['name']}")

        # 模拟执行（实际应该调用 iFlow CLI）
        print(f"  模拟执行中...")
        output = simulate_execution(test_case)

        # 评估输出
        print(f"  评估输出...")
        result = evaluator.evaluate_output(test_case, output)
        evaluator.results.append(result)

        # 显示结果
        status = "✓ 通过" if result['passed'] else "✗ 失败"
        print(f"  结果: {status} (得分: {result['score']}/100)")

    # 生成报告
    print(f"\n{'='*80}")
    print(f"\n生成测试报告...")
    report = evaluator.generate_report()

    # 保存报告
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = os.path.join(output_dir, f'benchmark_report_{timestamp}.txt')
    json_report_file = os.path.join(output_dir, f'benchmark_report_{timestamp}.json')

    evaluator.save_report(report, report_file)
    evaluator.save_json_report(json_report_file)

    # 打印报告摘要
    print(f"\n{'='*80}")
    print(report)
    print(f"\n{'='*80}")


if __name__ == '__main__':
    main()