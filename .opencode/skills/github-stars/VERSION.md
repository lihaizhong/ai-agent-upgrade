---
title: 版本管理
version: 1.0.0
last_updated: 2026-04-06
---

# github-stars Skill 版本管理

## 当前版本

**Skill 版本**: v1.0.0 (2026-04-06)

## 文件版本对照表

### 核心文件

| 文件路径 | 文件版本 | Skill 版本 | 最后更新 |
|---------|---------|-----------|---------|
| `SKILL.md` | - | 1.0.0 | 2026-04-06 |
| `VERSION.md` | 1.0.0 | 1.0.0 | 2026-04-06 |

### Scripts 文件（脚本）

| 文件路径 | 文件版本 | Skill 版本 | 最后更新 |
|---------|---------|-----------|---------|
| `scripts/fetch_stars.py` | 1.0.0 | 1.0.0 | 2026-04-06 |

### Reference 文件（参考资料）

| 文件路径 | 文件版本 | Skill 版本 | 最后更新 |
|---------|---------|-----------|---------|
| `references/categories.md` | 1.0.0 | 1.0.0 | 2026-04-06 |

## 版本规范

本 skill 遵循语义化版本规范（Semantic Versioning）：

```
主版本号.次版本号.修订号 (MAJOR.MINOR.PATCH)
```

- **主版本号（MAJOR）**: 重大架构变更或不兼容的更新
- **次版本号（MINOR）**: 新增功能，向后兼容
- **修订号（PATCH）**: 错误修复和改进，向后兼容

## 版本历史

### v1.0.0 (2026-04-06)
**初始版本**

**核心功能**:
- ✨ 通过 gh 工具获取 GitHub Stars
- ✨ 按类别分类整理 starred 仓库
- ✨ 归档到 docs/github-stars/ 目录
- ✨ 查看仓库详情和用途说明
- ✨ 提供安装教程（CLI 工具、Python 包、Node.js 包）
- ✨ 根据需求推荐工具和工具组合
- ✨ 生成完整的工具搭配教程

**文件结构**:
- `SKILL.md` - skill 配置和使用说明
- `scripts/fetch_stars.py` - 获取 starred 仓库的脚本
- `references/categories.md` - 分类规则和关键词定义

**依赖**:
- gh CLI（已认证）
- Python 3.6+（用于运行 fetch_stars.py 脚本）

---

**最后更新**: 2026-04-06
**维护者**: lihaizhong
