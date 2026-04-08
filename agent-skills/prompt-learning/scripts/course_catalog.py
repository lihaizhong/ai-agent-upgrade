"""
提示词工程学习系统 - 课程目录
统一维护课程元数据，避免课程文档、代码示例和脚本逻辑各自漂移。
"""

COURSE_CATALOG = [
    {
        "id": 1,
        "name": "零样本提示",
        "course_file": "01-零样本提示.md",
        "code_file": "01_zero_shot.py",
        "prereqs": [],
        "summary": "入门必学，学会直接给模型下清晰指令",
    },
    {
        "id": 2,
        "name": "少样本提示",
        "course_file": "02-少样本提示.md",
        "code_file": "02_few_shot.py",
        "prereqs": [1],
        "summary": "通过示例约束输出格式和风格",
    },
    {
        "id": 3,
        "name": "思维链提示",
        "course_file": "03-思维链提示.md",
        "code_file": "03_cot.py",
        "prereqs": [2],
        "summary": "让模型显式展开推理步骤",
    },
    {
        "id": 4,
        "name": "自我一致性",
        "course_file": "04-自我一致性.md",
        "code_file": "04_self_consistency.py",
        "prereqs": [3],
        "summary": "多次采样后投票，降低单次推理偏差",
    },
    {
        "id": 5,
        "name": "思维树",
        "course_file": "05-思维树.md",
        "code_file": "05_tot.py",
        "prereqs": [3, 4],
        "summary": "把复杂问题扩展成树状探索过程",
    },
    {
        "id": 6,
        "name": "生成知识提示",
        "course_file": "06-生成知识提示.md",
        "code_file": "06_generated_knowledge.py",
        "prereqs": [3],
        "summary": "先激活相关知识，再组织回答",
    },
    {
        "id": 7,
        "name": "检索增强生成",
        "course_file": "07-检索增强生成.md",
        "code_file": "07_rag.py",
        "prereqs": [6],
        "summary": "结合外部知识库，降低知识过期和幻觉",
    },
    {
        "id": 8,
        "name": "链式提示",
        "course_file": "08-链式提示.md",
        "code_file": "08_prompt_chaining.py",
        "prereqs": [3],
        "summary": "把任务拆成多个串联步骤执行",
    },
    {
        "id": 9,
        "name": "ReAct框架",
        "course_file": "09-ReAct框架.md",
        "code_file": "09_react.py",
        "prereqs": [3, 8],
        "summary": "让模型在推理和行动之间循环",
    },
    {
        "id": 10,
        "name": "程序辅助语言模型",
        "course_file": "10-程序辅助语言模型.md",
        "code_file": "10_pal.py",
        "prereqs": [3],
        "summary": "把推理转成代码执行，提升计算可靠性",
    },
    {
        "id": 11,
        "name": "自动推理和工具使用",
        "course_file": "11-自动推理和工具使用.md",
        "code_file": "11_art.py",
        "prereqs": [9],
        "summary": "自动选择工具与推理步骤完成任务",
    },
    {
        "id": 12,
        "name": "自动提示工程师",
        "course_file": "12-自动提示工程师.md",
        "code_file": "12_ape.py",
        "prereqs": [1],
        "summary": "自动生成和搜索更优提示词",
    },
    {
        "id": 13,
        "name": "主动提示",
        "course_file": "13-主动提示.md",
        "code_file": "13_active_prompt.py",
        "prereqs": [2],
        "summary": "动态挑选最有帮助的示例",
    },
    {
        "id": 14,
        "name": "方向性刺激提示",
        "course_file": "14-方向性刺激提示.md",
        "code_file": "14_dsp.py",
        "prereqs": [3],
        "summary": "通过刺激信号引导模型朝目标输出",
    },
    {
        "id": 15,
        "name": "自我反思",
        "course_file": "15-自我反思.md",
        "code_file": "15_reflexion.py",
        "prereqs": [3, 9],
        "summary": "基于失败反馈持续自我修正",
    },
    {
        "id": 16,
        "name": "多模态思维链",
        "course_file": "16-多模态思维链.md",
        "code_file": "16_multimodal_cot.py",
        "prereqs": [3],
        "summary": "把视觉信息纳入链式推理",
    },
    {
        "id": 17,
        "name": "图提示",
        "course_file": "17-图提示.md",
        "code_file": "17_graph_prompt.py",
        "prereqs": [5],
        "summary": "用图结构组织提示与关系推理",
    },
]

COURSE_METADATA = {course["id"]: course for course in COURSE_CATALOG}

CATEGORY_METADATA = {
    "基础课程": {
        "description": "建立提示词最基本的指令表达和示例意识。",
        "courses": [1, 2],
    },
    "推理课程": {
        "description": "学习如何让模型分步推理、投票和探索多条解法。",
        "courses": [3, 4, 5],
    },
    "知识课程": {
        "description": "处理知识注入、外部检索和多步骤任务编排。",
        "courses": [6, 7, 8],
    },
    "工具课程": {
        "description": "让模型调用工具、执行代码并与环境交互。",
        "courses": [9, 10, 11],
    },
    "优化课程": {
        "description": "关注提示词自动优化、示例选择与引导策略。",
        "courses": [12, 13, 14],
    },
    "前沿课程": {
        "description": "覆盖反馈学习、多模态推理和图结构提示等进阶主题。",
        "courses": [15, 16, 17],
    },
}

CATEGORY_ORDER = [
    "基础课程",
    "推理课程",
    "知识课程",
    "工具课程",
    "优化课程",
    "前沿课程",
]
