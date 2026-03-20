#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chinese Poetry Data Loader
从 chinese-poetry 数据库检索中国古诗词
支持本地数据和在线数据源，可通过自然语言拉取最新内容
"""

import os
import json
import argparse
import urllib.request
import subprocess
from pathlib import Path
from typing import List, Dict, Optional


class PoetryLoader:
    """中国古诗词数据加载器"""
    
    def __init__(self, cache_dir: Optional[str] = None, local_data_dir: Optional[str] = None):
        """
        初始化数据加载器
        
        Args:
            cache_dir: 数据缓存目录，默认为 ~/.chinese-poetry-cache
            local_data_dir: 本地数据目录，默认为 ~/Exp Vault/Poetry
        """
        if cache_dir is None:
            cache_dir = os.path.expanduser("~/.chinese-poetry-cache")
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 本地数据目录（优先使用）
        if local_data_dir is None:
            local_data_dir = os.path.expanduser("~/Exp Vault/Poetry/chinese-poetry")
        self.local_data_dir = Path(local_data_dir)
        
        # 在线数据源（备用）
        self.base_url = "https://raw.githubusercontent.com/chinese-poetry/chinese-poetry/master"
        
        # 数据文件配置（适配本地数据源）
        self.data_files = {
            "tang": [
                "全唐诗/poet.song.0.json"
            ],
            "song": [
                "全唐诗/poet.song.0.json"
            ],
            "song_ci": [
                "宋词/"
            ]
        }
        
        self.poems_cache: List[Dict] = []
        self.use_local_data = self.local_data_dir.exists()
    
    def download_file(self, url: str, local_path: Path) -> bool:
        """
        下载文件到本地
        
        Args:
            url: 远程文件 URL
            local_path: 本地保存路径
        
        Returns:
            下载是否成功
        """
        try:
            print(f"下载: {url}")
            urllib.request.urlretrieve(url, local_path)
            return True
        except Exception as e:
            print(f"下载失败: {e}")
            return False
    
    def pull_latest_data(self) -> bool:
        """
        从 GitHub 拉取最新数据（自然语言方式）
        
        Returns:
            是否成功拉取
        """
        if not self.local_data_dir.exists():
            print(f"本地数据目录不存在: {self.local_data_dir}")
            print("正在从 GitHub 克隆数据...")
            try:
                subprocess.run(
                    ["git", "clone", "--depth", "1", 
                     "https://github.com/chinese-poetry/chinese-poetry.git",
                     str(self.local_data_dir)],
                    check=True,
                    capture_output=True,
                    text=True
                )
                print("✓ 数据克隆成功！")
                self.use_local_data = True
                return True
            except subprocess.CalledProcessError as e:
                print(f"✗ 克隆失败: {e}")
                return False
        
        # 如果本地目录存在，尝试拉取最新内容
        print("正在从 GitHub 拉取最新内容...")
        try:
            subprocess.run(
                ["git", "pull"],
                cwd=str(self.local_data_dir),
                check=True,
                capture_output=True,
                text=True
            )
            print("✓ 数据更新成功！")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ 拉取失败: {e}")
            return False
    
    def load_json_file(self, local_path: Path) -> List[Dict]:
        """
        加载本地 JSON 文件
        
        Args:
            local_path: 本地文件路径
        
        Returns:
            诗歌数据列表
        """
        try:
            with open(local_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 处理不同的数据格式
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and 'poems' in data:
                    return data['poems']
                elif isinstance(data, dict) and 'items' in data:
                    return data['items']
                else:
                    print(f"未知的数据格式: {local_path}")
                    return []
        except Exception as e:
            print(f"加载文件失败 {local_path}: {e}")
            return []
    
    def load_poems(self, dynasty: str = "all", force_reload: bool = False) -> List[Dict]:
        """
        加载诗歌数据
        
        Args:
            dynasty: 朝代筛选（tang, song, song_ci, all）
            force_reload: 是否强制重新加载
        
        Returns:
            诗歌数据列表
        """
        if self.poems_cache and not force_reload:
            return self.poems_cache
        
        all_poems = []
        
        # 确定要加载的朝代
        dynasties_to_load = []
        if dynasty == "all":
            dynasties_to_load = ["tang", "song", "song_ci"]
        elif dynasty in self.data_files:
            dynasties_to_load = [dynasty]
        else:
            print(f"未知朝代: {dynasty}")
            return []
        
        # 优先使用本地数据
        if self.use_local_data and self.local_data_dir.exists():
            print(f"使用本地数据源: {self.local_data_dir}")
            
            # 加载唐诗三百首
            tangshi_file = self.local_data_dir / "全唐诗/唐诗三百首.json"
            if tangshi_file.exists():
                poems = self.load_json_file(tangshi_file)
                for poem in poems:
                    normalized = self._normalize_poem(poem, "唐")
                    if normalized:
                        all_poems.append(normalized)
            
            # 加载其他唐诗文件（示例）
            poet_file = self.local_data_dir / "全唐诗/poet.song.0.json"
            if poet_file.exists():
                poems = self.load_json_file(poet_file)
                for poem in poems:
                    normalized = self._normalize_poem(poem, "唐")
                    if normalized:
                        all_poems.append(normalized)
            
            if all_poems:
                self.poems_cache = all_poems
                print(f"加载完成，共 {len(all_poems)} 首诗歌（本地数据）")
                return all_poems
            else:
                print("本地数据为空，尝试在线数据源...")
        
        # 备用：使用在线数据源
        print("使用在线数据源...")
        for dyn in dynasties_to_load:
            for file_path in self.data_files[dyn]:
                url = f"{self.base_url}/{file_path}"
                local_path = self.cache_dir / os.path.basename(file_path)
                
                # 检查缓存
                if not local_path.exists() or force_reload:
                    if not self.download_file(url, local_path):
                        continue
                
                # 加载数据
                poems = self.load_json_file(local_path)
                
                # 标准化数据格式
                for poem in poems:
                    normalized = self._normalize_poem(poem, dyn)
                    if normalized:
                        all_poems.append(normalized)
        
        self.poems_cache = all_poems
        print(f"加载完成，共 {len(all_poems)} 首诗歌")
        return all_poems
    
    def _normalize_poem(self, poem: Dict, dynasty: str) -> Optional[Dict]:
        """
        标准化诗歌数据格式
        
        Args:
            poem: 原始诗歌数据
            dynasty: 朝代
        
        Returns:
            标准化后的诗歌数据
        """
        try:
            # 提取基本信息
            normalized = {
                "title": poem.get("title", ""),
                "author": poem.get("author", ""),
                "contents": poem.get("contents", []),
                "strains": poem.get("strains", ""),
                "dynasty": dynasty
            }
            
            # 处理内容格式（优先使用 paragraphs）
            if not normalized["contents"]:
                if "paragraphs" in poem:
                    normalized["contents"] = poem["paragraphs"]
                elif "content" in poem:
                    if isinstance(poem["content"], str):
                        # 按标点分割
                        content = poem["content"]
                        # 按。或；分割
                        sentences = []
                        current = ""
                        for char in content:
                            current += char
                            if char in ['。', '；', '，', '！', '？']:
                                sentences.append(current)
                                current = ""
                        if current:
                            sentences.append(current)
                        normalized["contents"] = sentences
                    else:
                        normalized["contents"] = poem["content"]
            
            # 从 tags 中提取体裁信息
            if "tags" in poem and isinstance(poem["tags"], list):
                # 查找包含体裁信息的 tag
                for tag in poem["tags"]:
                    if "言" in tag and "诗" in tag:
                        normalized["strains"] = tag
                        break
                    elif "词" in tag:
                        normalized["strains"] = tag
                        break
            
            # 验证必需字段
            if not normalized["title"] or not normalized["author"]:
                return None
            
            return normalized
        except Exception as e:
            print(f"标准化诗歌数据失败: {e}")
            return None
    
    def search_by_author(self, author: str, poems: Optional[List[Dict]] = None) -> List[Dict]:
        """
        按作者搜索
        
        Args:
            author: 作者姓名
            poems: 诗歌数据列表，如果为 None 则加载全部
        
        Returns:
            匹配的诗歌列表
        """
        if poems is None:
            poems = self.load_poems()
        
        results = []
        for poem in poems:
            if author in poem["author"]:
                results.append(poem)
        return results
    
    def search_by_title(self, title: str, poems: Optional[List[Dict]] = None) -> List[Dict]:
        """
        按标题搜索
        
        Args:
            title: 诗歌标题
            poems: 诗歌数据列表，如果为 None 则加载全部
        
        Returns:
            匹配的诗歌列表
        """
        if poems is None:
            poems = self.load_poems()
        
        results = []
        for poem in poems:
            if title in poem["title"]:
                results.append(poem)
        return results
    
    def search_by_keyword(self, keyword: str, poems: Optional[List[Dict]] = None) -> List[Dict]:
        """
        按关键词搜索
        
        Args:
            keyword: 关键词
            poems: 诗歌数据列表，如果为 None 则加载全部
        
        Returns:
            匹配的诗歌列表
        """
        if poems is None:
            poems = self.load_poems()
        
        results = []
        for poem in poems:
            # 搜索标题
            if keyword in poem["title"]:
                results.append(poem)
                continue
            
            # 搜索内容
            content_text = "".join(poem["contents"])
            if keyword in content_text:
                results.append(poem)
        
        return results
    
    def search_by_dynasty(self, dynasty: str) -> List[Dict]:
        """
        按朝代搜索
        
        Args:
            dynasty: 朝代（tang, song, song_ci）
        
        Returns:
            匹配的诗歌列表
        """
        return self.load_poems(dynasty=dynasty)
    
    def search_by_type(self, poem_type: str, poems: Optional[List[Dict]] = None) -> List[Dict]:
        """
        按体裁搜索
        
        Args:
            poem_type: 诗歌体裁（如"五言绝句"、"七言律诗"、"宋词"等）
            poems: 诗歌数据列表，如果为 None 则加载全部
        
        Returns:
            匹配的诗歌列表
        """
        if poems is None:
            poems = self.load_poems()
        
        results = []
        for poem in poems:
            if poem_type in poem["strains"]:
                results.append(poem)
        
        return results


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="中国古诗词数据加载器")
    parser.add_argument("--author", help="按作者搜索")
    parser.add_argument("--title", help="按标题搜索")
    parser.add_argument("--keyword", help="按关键词搜索")
    parser.add_argument("--dynasty", choices=["tang", "song", "song_ci"], help="按朝代搜索")
    parser.add_argument("--type", help="按体裁搜索")
    parser.add_argument("--limit", type=int, default=5, help="返回结果数量限制")
    parser.add_argument("--force-reload", action="store_true", help="强制重新加载数据")
    parser.add_argument("--pull", action="store_true", help="从 GitHub 拉取最新数据")
    parser.add_argument("--local-data", help="本地数据目录路径")
    
    args = parser.parse_args()
    
    # 创建加载器
    loader = PoetryLoader(local_data_dir=args.local_data)
    
    # 拉取最新数据
    if args.pull:
        loader.pull_latest_data()
    
    # 加载数据
    poems = loader.load_poems(dynasty=args.dynasty or "all", force_reload=args.force_reload)
    
    # 执行搜索
    results = []
    if args.author:
        results = loader.search_by_author(args.author, poems)
    elif args.title:
        results = loader.search_by_title(args.title, poems)
    elif args.keyword:
        results = loader.search_by_keyword(args.keyword, poems)
    elif args.type:
        results = loader.search_by_type(args.type, poems)
    else:
        results = poems
    
    # 应用体裁筛选
    if args.type and results:
        filtered = []
        for poem in results:
            if args.type in poem["strains"]:
                filtered.append(poem)
        results = filtered
    
    # 限制返回数量
    results = results[:args.limit]
    
    # 输出结果
    output = {
        "poems": results,
        "total": len(results)
    }
    
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()