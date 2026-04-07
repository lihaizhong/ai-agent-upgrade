---
name: github-stars
description: 管理 GitHub Stars 仓库的工具。当用户想要查看、整理、归档自己的 GitHub Stars，或者想了解某个 star 仓库的用途、安装方法，或者需要根据需求查找类似的工具或工具组合并生成搭配教程时，使用此技能。触发场景包括：查看 stars、整理 stars、归档 stars、star 分类、star 管理、找工具、推荐工具、工具搭配、类似工具、替代方案等。
metadata:
  version: 1.0.0
  author: lihaizhong
  last_updated: 2026-04-06
---

# GitHub Stars 管理工具

本 skill 帮助你管理 GitHub Stars，包含三大功能：

1. **查看与归档** - 通过 `gh` 工具获取 starred 仓库，分类整理后归档到 `docs/` 目录
2. **仓库详情与安装** - 了解 star 仓库的用途，如果是安装工具则提供安装教程
3. **工具推荐与搭配** - 根据需求描述，查找类似工具或工具组合，生成完整搭配教程

## 使用方式

当用户触发本技能时，使用 `question` 工具展示功能选择：

```
标题：欢迎使用 GitHub Stars 管理工具！
问题：请问您想做什么？
选项：
1. 查看与归档 Stars - 获取、分类、整理并归档所有 starred 仓库
2. 仓库详情与安装 - 了解某个 star 仓库的用途和安装方法
3. 工具推荐与搭配 - 根据需求查找类似工具，生成搭配教程
```

如果 `question` 工具不可用，降级为纯文本菜单。

---

## 功能 1：查看与归档 Stars

### 工作流程

1. **获取 starred 仓库列表**

使用 `gh` 命令获取所有 starred 仓库：

```bash
gh api user/starred --paginate -q '.[] | {full_name, description, language, stargazers_count, html_url, topics, pushed_at, created_at}'
```

2. **分类整理**

按照以下类别对仓库进行分类（详见 [references/categories.md](references/categories.md)）：

| 类别 | 说明 |
|------|------|
| AI/ML | 人工智能、机器学习、大模型相关 |
| 开发工具 | IDE 插件、CLI 工具、构建工具等 |
| 前端开发 | 前端框架、组件库、构建工具等 |
| 后端开发 | 后端框架、API 工具、数据库等 |
| DevOps | CI/CD、容器化、部署、监控等 |
| 数据科学 | 数据分析、可视化、ETL 等 |
| 安全工具 | 安全扫描、渗透测试、加密等 |
| 学习资源 | 教程、课程、书籍、科普项目等 |
| 效率工具 | 笔记、任务管理、自动化工具等 |
| 其他 | 无法归类的仓库 |

分类规则：
- 优先根据 `topics` 和 `description` 关键词匹配
- 其次根据 `language` 辅助判断
- 如果仓库有多个标签，归入最匹配的类别

3. **生成归档文档**

在 `docs/github-stars/` 目录下生成归档文档：

```
docs/github-stars/
├── README.md              # 总览和索引
├── stars-archive-2026-04-06.md  # 按日期归档的完整列表
└── by-category/
    ├── ai-ml.md
    ├── dev-tools.md
    ├── frontend.md
    ├── backend.md
    ├── devops.md
    ├── data-science.md
    ├── security.md
    ├── learning.md
    ├── productivity.md
    └── other.md
```

### 归档文档格式

每个仓库在归档中按以下格式展示：

```markdown
### [仓库名称](仓库URL)

- **描述**: 仓库描述
- **语言**: 主要编程语言
- **Stars**: ⭐ 数量
- **最后更新**: 日期
- **标签**: topic1, topic2, ...

> 💡 简要说明这个仓库是做什么的
```

### 执行步骤

1. 运行获取 starred 仓库的命令
2. 根据分类规则对每个仓库进行分类
3. 生成 `docs/github-stars/` 目录结构
4. 写入 `README.md` 总览（包含各类别仓库数量统计）
5. 写入按日期命名的归档文件（包含所有仓库的完整信息）
6. 写入 `by-category/` 下各分类文件（按类别分组）
7. 向用户报告归档结果

---

## 功能 2：仓库详情与安装

### 工作流程

当用户想了解某个 star 仓库的详情时：

1. **定位仓库**

如果用户提供了仓库名称或关键词，使用 `gh` 搜索：

```bash
gh search repos <关键词> --owner <owner> --limit 5
```

或者如果用户指定了已 star 的仓库，从归档数据中查找。

2. **获取详细信息**

```bash
gh api repos/<owner>/<repo> -q '{description, homepage, language, stargazers_count, forks_count, topics, default_branch}'
```

3. **获取 README 内容**

```bash
gh api repos/<owner>/<repo>/readme -q '.content' | base64 -d
```

4. **分析用途**

根据仓库的 `description`、`topics` 和 README 内容，用简洁的语言说明这个仓库是做什么的、解决了什么问题。

5. **提供安装指南**

如果该仓库是安装工具（如 CLI 工具、包、插件等），从 README 中提取安装步骤，或者根据仓库类型生成标准安装教程：

**CLI 工具安装格式**：

```markdown
## 安装 [工具名称]

### 方式一：使用包管理器

\`\`\`bash
# macOS
brew install <tool>

# Linux (deb)
sudo apt install <tool>

# Linux (rpm)
sudo dnf install <tool>
\`\`\`

### 方式二：使用脚本安装

\`\`\`bash
curl -fsSL https://example.com/install.sh | sh
\`\`\`

### 方式三：从源码编译

\`\`\`bash
git clone https://github.com/<owner>/<repo>.git
cd <repo>
make install
\`\`\`

### 验证安装

\`\`\`bash
<tool> --version
\`\`\`
```

**Python 包安装格式**：

```markdown
## 安装 [包名称]

\`\`\`bash
# 使用 pip
pip install <package>

# 使用 uv（推荐）
uv pip install <package>

# 使用 conda
conda install -c conda-forge <package>
\`\`\`

### 验证安装

\`\`\`bash
python -c "import <package>; print(<package>.__version__)"
\`\`\`
```

**Node.js 包安装格式**：

```markdown
## 安装 [包名称]

\`\`\`bash
# 使用 npm
npm install <package>

# 使用 yarn
yarn add <package>

# 使用 pnpm
pnpm add <package>
\`\`\`
```

### 输出格式

向用户展示：

```markdown
## [仓库名称](URL)

**一句话介绍**: 用一句话说明这个仓库是做什么的

**详细介绍**:
根据 README 和仓库信息，详细说明其功能、特点和使用场景。

---

## 安装指南

[根据仓库类型选择合适的安装格式]
```

---

## 功能 3：工具推荐与搭配

### 工作流程

当用户描述需求、想要做什么时：

1. **理解需求**

分析用户描述，提取：
- 目标：想要完成什么
- 场景：在什么环境下使用
- 约束：有什么限制（如语言偏好、平台限制等）

2. **查找候选工具**

使用 `gh` 搜索相关工具：

```bash
gh search repos <关键词> --sort=stars --order=desc --limit 20
```

同时结合自己的知识，推荐知名工具。

3. **筛选和对比**

对候选工具进行对比分析，包括：
- 功能特点
- 活跃度（stars、最近更新时间）
- 社区生态
- 学习成本
- 适用场景

4. **生成搭配教程**

如果用户需求需要多个工具组合，生成完整的搭配教程，包括：

```markdown
# [场景名称] 工具搭配教程

## 场景描述

说明这个搭配适用于什么场景，解决什么问题。

## 工具清单

| 工具 | 用途 | 链接 |
|------|------|------|
| 工具A | 用途说明 | URL |
| 工具B | 用途说明 | URL |
| 工具C | 用途说明 | URL |

## 安装步骤

### 1. 安装工具A

[安装命令和步骤]

### 2. 安装工具B

[安装命令和步骤]

### 3. 安装工具C

[安装命令和步骤]

## 配置与集成

### 工具A 配置

[配置说明]

### 工具B 配置

[配置说明]

### 工具间的集成

[如何让工具协同工作]

## 使用示例

[具体的使用示例，包含命令和预期输出]

## 常见问题

### Q: [常见问题]
A: [解答]
```

### 输出要求

- 推荐的工具要具体，包含仓库链接
- 安装步骤要可执行，不要让用户猜
- 搭配教程要完整，从零到一
- 如果涉及多个工具，说明它们之间的关系和数据流
- 提供实际可运行的示例

---

## 注意事项

1. **gh 依赖**: 本技能依赖 `gh` CLI 工具，使用前确保已认证 (`gh auth status`)
2. **分页获取**: 使用 `--paginate` 确保获取所有 starred 仓库
3. **分类准确性**: 分类时优先使用 `topics`，其次 `description`，最后 `language`
4. **文档更新**: 归档时如果 `docs/github-stars/` 已存在，更新而非覆盖
5. **安装教程**: 优先从仓库 README 提取安装步骤，如果没有则根据仓库类型生成标准模板
6. **工具推荐**: 推荐的工具应该是活跃维护的项目（最近一年内有更新）

## 常见使用场景

### 场景 1：整理我的 Stars
用户：`帮我整理一下我的 GitHub stars`
操作：执行功能 1，获取所有 starred 仓库，分类归档到 docs 目录

### 场景 2：这个 star 是做什么的
用户：`我之前 star 了一个叫 xxx 的仓库，它是做什么的？怎么安装？`
操作：执行功能 2，查找仓库，说明用途，提供安装教程

### 场景 3：找工具
用户：`我想搭建一个本地知识库，有什么好工具推荐？`
操作：执行功能 3，搜索相关工具，生成推荐和搭配教程

### 场景 4：工具搭配
用户：`我想用 AI 辅助写代码，有什么工具组合推荐？`
操作：执行功能 3，推荐工具组合，生成完整搭配教程
