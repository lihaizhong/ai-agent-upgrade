#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基准测试演示脚本
展示如何使用基准测试工具并生成示例报告
"""

import json
import os
from datetime import datetime


def load_test_cases(evals_file):
    """加载测试用例"""
    with open(evals_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data['evals']


def create_demo_results(test_cases):
    """创建演示用的测试结果"""
    demo_results = []

    # 为前 5 个测试用例创建不同的演示结果
    demo_outputs = {
        1: """# 提示词工程基础知识

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
""",
        2: """# 提示词分析与改进

## 当前提示词问题分析

**当前提示词**: "帮我写个函数来处理数据"

### 存在的问题：

1. **缺乏上下文** - 没有说明要处理什么类型的数据
2. **不够具体** - "处理数据"太笼统
3. **未指定输入输出格式** - 没有说明数据的格式
4. **未说明语言和技术栈** - 没有指定使用什么语言
5. **缺乏约束条件** - 没有说明性能要求等

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
""",
        3: """# 提示词工程练习题（中级难度）

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
""",
        4: """# 提示词质量评估

## 评估维度

我将从以下维度评估这个提示词：

### 1. 清晰度 (8/10)
✓ 角色定位明确
✓ 任务目标清晰
⚠️ 可以进一步细化具体要求

### 2. 完整性 (7/10)
✓ 包含角色设定
✓ 包含技术栈要求
✓ 包含功能需求
⚠️ 缺少设计风格和用户体验要求

### 3. 具体性 (6/10)
✓ 明确了技术栈（React）
✓ 明确了功能（用户名密码登录、记住密码）
⚠️ 未说明表单验证规则
⚠️ 未说明错误处理方式
⚠️ 未说明响应式设计要求

### 4. 约束性 (5/10)
✓ 明确了功能约束
⚠️ 未指定代码风格
⚠️ 未指定性能要求
⚠️ 未指定安全要求（如密码加密）

### 5. 可执行性 (8/10)
✓ AI 可以直接理解并执行
✓ 有明确的交付物

### 6. 有效性 (7/10)
✓ 能够获得相关的输出
⚠️ 可能需要多次迭代才能达到理想效果

## 总体评分

**总分: 6.8/10**
**评级: 良好**

## 优点
- 角色定位清晰
- 技术栈明确
- 核心功能明确

## 不足
- 缺少设计细节
- 缺少安全性要求
- 缺少用户体验规范

## 优化建议

```
你是一位有 5 年经验的前端开发专家，专注于 React 生态和用户体验设计。请帮我创建一个现代化的登录页面组件，要求：

技术栈：
- 使用 React Hooks
- 使用 TypeScript
- 使用 Ant Design 组件库

功能需求：
- 用户名密码登录
- 记住密码功能（使用 localStorage）
- 表单验证（实时验证）
- 错误提示（友好的用户反馈）

设计要求：
- 响应式设计，支持移动端
- 现代化的 UI 风格
- 良好的用户体验（加载状态、动画效果）
- 遵循无障碍设计原则

安全要求：
- 密码字段使用 type="password"
- 防止 XSS 攻击
- 添加 CSRF 保护

代码要求：
- 使用 TypeScript 类型定义
- 添加必要的注释
- 遵循 ESLint 规范
- 组件化设计，易于复用
```
""",
        5: """# 角色扮演提示词设计

## 提示词

```
你现在是一位拥有 20 年经验的资深系统架构师，曾主导过多个千万级用户的大型分布式系统设计。你精通高并发、高可用、可扩展的架构设计，熟悉微服务架构、云原生技术、分布式存储、缓存策略、消息队列等核心技术。

## 任务背景

请帮我设计一个高并发电商系统的整体架构，该系统需要支持：
- 日活用户数：1000 万+
- 峰值 QPS：10 万+
- 商品数量：1 亿+
- 订单处理能力：每秒 1000 单

## 架构设计要求

请从以下维度进行架构设计：

### 1. 整体架构
- 选择合适的架构模式（微服务 / 单体 / 混合）
- 画出核心架构图（描述各层组件及其关系）
- 说明技术选型的理由

### 2. 核心模块设计
- 用户服务（注册、登录、权限）
- 商品服务（商品管理、搜索、推荐）
- 订单服务（下单、支付、物流）
- 营销服务（优惠券、活动、秒杀）

### 3. 性能优化策略
- 缓存策略（多级缓存设计）
- 数据库优化（分库分表、读写分离）
- 异步处理（消息队列应用）
- CDN 加速

### 4. 高可用保障
- 服务降级与熔断
- 限流策略
- 容灾备份
- 监控告警

### 5. 扩展性设计
- 水平扩展能力
- 模块化设计
- 插件化架构

## 输出要求

请按照以下格式输出：

1. **架构概览**：整体架构思路和架构图描述
2. **技术栈选型**：详细说明各组件的选型理由
3. **核心模块设计**：每个模块的详细设计
4. **性能优化方案**：具体的优化措施和预期效果
5. **高可用方案**：容灾和备份策略
6. **演进路线图**：从 MVP 到大规模的演进规划

在分析过程中，请展示你的思考过程，说明为什么选择某种方案，以及考虑了哪些权衡。
```
"""
    }

    for i, test_case in enumerate(test_cases[:5], 1):  # 只演示前 5 个
        output = demo_outputs.get(i, "")
        if not output:
            # 使用默认输出
            output = f"针对 {test_case['name']} 的响应...\n\n{test_case['expected_output']}"

        # 模拟评估
        result = {
            'test_id': test_case['id'],
            'test_name': test_case['name'],
            'category': test_case['category'],
            'difficulty': test_case['difficulty'],
            'prompt': test_case['prompt'],
            'expected': test_case['expected_output'],
            'output': output,
            'passed': i <= 3,  # 前 3 个通过
            'score': 85.0 if i <= 3 else 65.0,
            'dimensions': {
                '完整性': 28.0,
                '相关性': 26.0,
                '结构性': 18.0,
                '具体性': 16.0
            } if i <= 3 else {
                '完整性': 20.0,
                '相关性': 22.0,
                '结构性': 12.0,
                '具体性': 11.0
            },
            'issues': [] if i <= 3 else ['输出缺乏具体示例', '结构不够清晰'],
            'suggestions': [] if i <= 3 else ['添加实际示例', '改善内容结构'],
            'execution_mode': 'demo'
        }
        demo_results.append(result)

    # 添加跳过的测试用例
    for test_case in test_cases[5:]:
        demo_results.append({
            'test_id': test_case['id'],
            'test_name': test_case['name'],
            'category': test_case['category'],
            'difficulty': test_case['difficulty'],
            'prompt': test_case['prompt'],
            'expected': test_case['expected_output'],
            'output': '',
            'passed': False,
            'score': 0,
            'dimensions': {'完整性': 0, '相关性': 0, '结构性': 0, '具体性': 0},
            'issues': ['演示模式下跳过'],
            'suggestions': ['使用完整基准测试'],
            'execution_mode': 'demo'
        })

    return demo_results


def generate_report(results):
    """生成测试报告"""
    report = []
    report.append("=" * 80)
    report.append("Prompt-Learning Skill 基准测试报告（演示）")
    report.append("=" * 80)
    report.append(f"\n测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"测试用例总数: {len(results)}")
    report.append(f"执行模式: 演示模式")

    # 统计结果
    executed = sum(1 for r in results if r['score'] > 0)
    passed = sum(1 for r in results if r['passed'])
    failed = executed - passed
    pass_rate = (passed / executed * 100) if executed > 0 else 0
    avg_score = sum(r['score'] for r in results if r['score'] > 0) / executed if executed > 0 else 0

    report.append(f"\n总体统计:")
    report.append(f"  已执行: {executed} 个")
    report.append(f"  跳过: {len(results) - executed} 个")
    report.append(f"  通过: {passed} 个")
    report.append(f"  失败: {failed} 个")
    report.append(f"  通过率: {pass_rate:.1f}%")
    report.append(f"  平均得分: {avg_score:.1f}/100")

    # 详细结果
    report.append(f"\n" + "=" * 80)
    report.append("详细测试结果（前 5 个）")
    report.append("=" * 80)

    for i, result in enumerate(results[:5], 1):
        if result['score'] == 0:
            status = "⊘ 跳过"
        elif result['passed']:
            status = "✓ 通过"
        else:
            status = "✗ 失败"

        report.append(f"\n{i}. {result['test_name']} [{result['category']}/{result['difficulty']}] {status}")
        report.append(f"   得分: {result['score']}/100")
        report.append(f"   维度得分: {result['dimensions']}")

        if not result['passed'] and result['score'] > 0:
            report.append(f"   问题: {', '.join(result['issues'])}")
            report.append(f"   建议: {', '.join(result['suggestions'])}")

    # 改进建议
    report.append(f"\n" + "=" * 80)
    report.append("演示说明")
    report.append("=" * 80)

    report.append(f"\n这是一个演示报告，展示了基准测试工具的使用方法。")
    report.append(f"\n要运行真实的基准测试，请使用:")
    report.append(f"  python3 run_real_benchmark.py")
    report.append(f"\n或查看 README.md 了解更多使用方法。")

    report.append(f"\n" + "=" * 80)
    report.append("报告结束")
    report.append("=" * 80)

    return "\n".join(report)


def main():
    """主函数"""
    # 设置路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    evals_file = os.path.join(script_dir, 'evals.json')
    output_dir = os.path.join(script_dir, 'results')

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 80)
    print("Prompt-Learning Skill 基准测试演示")
    print("=" * 80)

    # 加载测试用例
    print("\n加载测试用例...")
    test_cases = load_test_cases(evals_file)
    print(f"✓ 已加载 {len(test_cases)} 个测试用例")

    # 创建演示结果
    print("\n生成演示结果...")
    results = create_demo_results(test_cases)
    print(f"✓ 已生成 {len(results)} 个演示结果")

    # 生成报告
    print("\n生成测试报告...")
    report = generate_report(results)

    # 保存报告
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = os.path.join(output_dir, f'demo_report_{timestamp}.txt')

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"✓ 演示报告已保存到: {report_file}")

    # 打印报告
    print("\n" + report)

    print("\n" + "=" * 80)
    print("演示完成！")
    print("=" * 80)


if __name__ == '__main__':
    main()