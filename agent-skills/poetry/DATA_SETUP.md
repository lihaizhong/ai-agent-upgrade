# Poetry Skill 数据设置指南

## 概述

Poetry Skill 需要访问 chinese-poetry 数据库来检索诗歌。我们支持两种数据源：

1. **本地数据源**（推荐）：从克隆的本地仓库读取数据
2. **在线数据源**（备用）：从 GitHub 下载 JSON 文件

## 方式一：手动克隆数据（推荐）

### 步骤 1：创建目录

```bash
mkdir -p ~/Exp\ Vault/Poetry
cd ~/Exp\ Vault/Poetry
```

### 步骤 2：克隆仓库

```bash
git clone https://github.com/chinese-poetry/chinese-poetry.git .
```

如果网络不稳定，可以使用浅克隆（更快）：

```bash
git clone --depth 1 https://github.com/chinese-poetry/chinese-poetry.git .
```

### 步骤 3：验证数据

检查是否包含 `jsons/` 目录：

```bash
ls jsons/
```

应该看到以下文件：
- `poet.tang.0.json` ~ `poet.tang.8.json`（唐诗）
- `poets.song.0.json` ~ `poets.song.9.json`（宋诗）
- `ci.song.0.json` ~ `ci.song.21.json`（宋词）

## 方式二：使用 GitHub Desktop（图形界面）

1. 打开 GitHub Desktop
2. File → Clone Repository
3. 输入 URL: `https://github.com/chinese-poetry/chinese-poetry.git`
4. 选择本地路径: `~/Exp Vault/Poetry`
5. 点击 Clone

## 更新数据

### 命令行方式

```bash
cd ~/Exp\ Vault/Poetry
git pull
```

### 使用 poetry_loader.py

```bash
python3 /path/to/poetry/scripts/poetry_loader.py --pull
```

这会自动从 GitHub 拉取最新数据。

## 使用示例

### 基本搜索

```bash
# 搜索李白的诗
python3 /path/to/poetry/scripts/poetry_loader.py --author "李白"

# 搜索《静夜思》
python3 /path/to/poetry/scripts/poetry_loader.py --title "静夜思"

# 搜索包含"明月"的诗
python3 /path/to/poetry/scripts/poetry_loader.py --keyword "明月"

# 搜索唐诗
python3 /path/to/poetry/scripts/poetry_loader.py --dynasty "tang"

# 搜索宋词
python3 /path/to/poetry/scripts/poetry_loader.py --dynasty "song_ci"

# 搜索七言绝句
python3 /path/to/poetry/scripts/poetry_loader.py --type "七言绝句"
```

### 组合搜索

```bash
# 搜索李白的五言绝句
python3 /path/to/poetry/scripts/poetry_loader.py --author "李白" --type "五言绝句"

# 搜索苏轼的宋词，限制返回 3 首
python3 /path/to/poetry/scripts/poetry_loader.py --author "苏轼" --dynasty "song_ci" --limit 3
```

### 拉取最新数据

```bash
# 拉取最新数据并搜索
python3 /path/to/poetry/scripts/poetry_loader.py --pull --author "李白"
```

## 数据源优先级

1. **本地数据源**：优先使用 `~/Exp Vault/Poetry` 目录中的数据
2. **在线数据源**：如果本地数据不可用或为空，自动从 GitHub 下载

## 网络问题解决

如果无法直接访问 GitHub，可以尝试以下方法：

### 方法 1：使用代理

```bash
export https_proxy=http://your-proxy:port
git clone https://github.com/chinese-poetry/chinese-poetry.git ~/Exp\ Vault/Poetry
```

### 方法 2：使用 GitHub 镜像

```bash
git clone https://github.com.cnpmjs.org/chinese-poetry/chinese-poetry.git ~/Exp\ Vault/Poetry
```

### 方法 3：下载 ZIP 文件

1. 访问：https://github.com/chinese-poetry/chinese-poetry/archive/refs/heads/master.zip
2. 下载 ZIP 文件
3. 解压到 `~/Exp Vault/Poetry` 目录
4. 确保 `jsons/` 目录在正确位置

## 验证安装

运行以下命令验证数据是否正确加载：

```bash
python3 /path/to/poetry/scripts/poetry_loader.py --author "李白" --limit 1
```

如果返回 JSON 格式的诗歌数据，说明安装成功。

## 常见问题

### Q: 提示"文件不存在"或"加载失败"

A: 检查 `~/Exp Vault/Poetry/jsons/` 目录是否存在并包含 JSON 文件。

### Q: 搜索结果为空

A: 可能是数据未正确加载，尝试运行 `--pull` 参数重新拉取数据。

### Q: 网络连接超时

A: 使用本地数据源，先手动克隆仓库，或配置代理。

### Q: 如何自定义数据目录？

A: 使用 `--local-data` 参数指定自定义路径：

```bash
python3 /path/to/poetry/scripts/poetry_loader.py --local-data "/path/to/data" --author "李白"
```

## 数据统计

chinese-poetry 数据库包含：

- 唐诗：约 5.5 万首
- 宋诗：约 26 万首
- 宋词：约 2.1 万首
- 诗人：约 1.4 万位（唐宋）
- 词人：约 1.5 千位（两宋）

## 维护

定期更新数据以获取最新内容：

```bash
cd ~/Exp\ Vault/Poetry
git pull
```

建议每月更新一次。

---

**最后更新**：2026-03-14
**维护者**：iFlow CLI