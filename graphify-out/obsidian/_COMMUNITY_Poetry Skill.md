---
type: community
members: 23
---

# Poetry Skill

**Members:** 23 nodes

## Members
- [[._normalize_poem()]] - code - agent-skills/poetry/scripts/poetry_loader.py
- [[.download_file()]] - code - agent-skills/poetry/scripts/poetry_loader.py
- [[.load_json_file()]] - code - agent-skills/poetry/scripts/poetry_loader.py
- [[.load_poems()]] - code - agent-skills/poetry/scripts/poetry_loader.py
- [[.pull_latest_data()]] - code - agent-skills/poetry/scripts/poetry_loader.py
- [[.search_by_author()]] - code - agent-skills/poetry/scripts/poetry_loader.py
- [[.search_by_dynasty()]] - code - agent-skills/poetry/scripts/poetry_loader.py
- [[.search_by_keyword()]] - code - agent-skills/poetry/scripts/poetry_loader.py
- [[.search_by_title()]] - code - agent-skills/poetry/scripts/poetry_loader.py
- [[.search_by_type()]] - code - agent-skills/poetry/scripts/poetry_loader.py
- [[PoetryLoader]] - code - agent-skills/poetry/scripts/poetry_loader.py
- [[main()_1]] - code - agent-skills/poetry/scripts/poetry_loader.py
- [[poetry_loader.py]] - code - agent-skills/poetry/scripts/poetry_loader.py
- [[下载文件到本地                  Args             url 远程文件 URL             local_path]] - rationale - agent-skills/poetry/scripts/poetry_loader.py
- [[从 GitHub 拉取最新数据（自然语言方式）                  Returns             是否成功拉取]] - rationale - agent-skills/poetry/scripts/poetry_loader.py
- [[加载本地 JSON 文件                  Args             local_path 本地文件路径]] - rationale - agent-skills/poetry/scripts/poetry_loader.py
- [[加载诗歌数据                  Args             dynasty 朝代筛选（tang, song, song_ci, all]] - rationale - agent-skills/poetry/scripts/poetry_loader.py
- [[按体裁搜索                  Args             poem_type 诗歌体裁（如五言绝句、七言律诗、宋词等）]] - rationale - agent-skills/poetry/scripts/poetry_loader.py
- [[按作者搜索                  Args             author 作者姓名             poems 诗歌数据列表，]] - rationale - agent-skills/poetry/scripts/poetry_loader.py
- [[按关键词搜索                  Args             keyword 关键词             poems 诗歌数据列表]] - rationale - agent-skills/poetry/scripts/poetry_loader.py
- [[按朝代搜索                  Args             dynasty 朝代（tang, song, song_ci）]] - rationale - agent-skills/poetry/scripts/poetry_loader.py
- [[按标题搜索                  Args             title 诗歌标题             poems 诗歌数据列表，如]] - rationale - agent-skills/poetry/scripts/poetry_loader.py
- [[标准化诗歌数据格式                  Args             poem 原始诗歌数据             dynasty 朝]] - rationale - agent-skills/poetry/scripts/poetry_loader.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Poetry_Skill
SORT file.name ASC
```

## Connections to other communities
- 1 edge to [[_COMMUNITY_Practice Agent Loops]]

## Top bridge nodes
- [[PoetryLoader]] - degree 13, connects to 1 community