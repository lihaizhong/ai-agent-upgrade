---
name: /openexp
id: openexp
category: Experience
description: |
  经验管理命令 - AI 记忆系统的核心，学习、积累和应用用户偏好与解决方案。

  强制触发场景：用户表达偏好("我喜欢...")、提到历史("之前怎么...")、
  显式学习("记住这个")、任务开始时搜索相关经验。
---

经验管理命令。使用自然语言描述你的需求，AI 会自动判断需要做什么操作。

---

## 快速开始

```bash
# 记录偏好
/openexp 我喜欢用 pnpm 而不是 npm

# 搜索经验
/openexp 搜索 CORS 相关的经验

# 查看状态
/openexp 经验库状态
```

---

## 命令参考

```bash
# 动态查找 CLI
OPENEXP=$(find . -name "openexp.sh" -path "*/skills/openexp/*" 2>/dev/null | head -1)

# 添加经验
$OPENEXP add <type> "<content>"

# 搜索经验
$OPENEXP search <keyword>

# 获取详情
$OPENEXP get <id>

# 列出经验
$OPENEXP list [type]

# 使用计数 +1
$OPENEXP bump <id>

# 反馈
$OPENEXP feedback <id> useful|useless

# 查看状态
$OPENEXP status

# 创建快照
$OPENEXP snapshot "描述"
```

---

## 经验类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `preference` | 用户偏好、习惯 | 包管理器选择、代码风格 |
| `workflow` | 工作流程 | 部署步骤、发布流程 |
| `solution` | 问题解决方案 | 报错处理、Bug 修复 |
| `knowledge` | 知识点 | API 用法、工具配置 |
| `experience` | 完整解决过程 | 复杂问题排查记录 |
| `convention` | 约定规范 | 命名规则、目录结构 |

---

## AI 判断逻辑

| 关键词 | 操作 |
|--------|------|
| "我喜欢"、"记住"、"习惯" | 添加经验 |
| "搜索"、"找"、"查询" | 搜索经验 |
| "列出"、"看看"、"有多少" | 列出/统计 |
| "详情"、"查看" | 获取详情 |
| "有效"、"不管用" | 反馈评价 |

---

## 注意事项

- 不要记录敏感信息（密码、密钥等）
- 必须通过 CLI 操作，禁止直接读写文件
- 经验 ID 格式：`exp_<type>_<YYYYMMDD>_<HHMMSS>_<seq>`
- 定期执行 `snapshot` 创建快照
- 新经验有 30 天保护期

---

## 相关文档

- [完整技能文档](../skills/openexp/SKILL.md)
- [CLI 脚本](../skills/openexp/openexp.sh)
