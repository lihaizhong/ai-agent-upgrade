# 代码示例说明

本目录包含提示词工程技术的 Python 实现示例。

## 目录结构

每个文件对应一门课程的实现：
- `utils.py` - 通用工具函数
- `01_zero_shot.py` - 零样本提示
- `02_few_shot.py` - 少样本提示
- `03_cot.py` - 思维链提示
- `04_self_consistency.py` - 自我一致性
- `05_tot.py` - 思维树
- `06_generated_knowledge.py` - 生成知识提示
- `07_rag.py` - 检索增强生成
- `08_prompt_chaining.py` - 链式提示
- `09_react.py` - ReAct框架
- `10_pal.py` - 程序辅助语言模型
- `11_art.py` - 自动推理和工具使用
- `12_ape.py` - 自动提示工程师
- `13_active_prompt.py` - 主动提示
- `14_dsp.py` - 方向性刺激提示
- `15_reflexion.py` - 自我反思
- `16_multimodal_cot.py` - 多模态思维链
- `17_graph_prompt.py` - 图形提示

## 使用前提

安装依赖：
```bash
pip install openai anthropic
```

## 使用方法

1. 设置环境变量：
```bash
export OPENAI_API_KEY="your-api-key"
# 或
export ANTHROPIC_API_KEY="your-api-key"
```

2. 直接运行示例文件：
```bash
python 03_cot.py
```

## 代码规范

- 每个文件包含：
  1. `call_llm()` - LLM 调用封装
  2. `example_xxx()` - 具体技术示例
  3. `main()` - 演示入口

- 返回格式统一：
  - 成功：`{"success": True, "data": ..., "cost": ...}`
  - 失败：`{"success": False, "error": ...}`
