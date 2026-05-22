#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识检索Agent（多源）
从多个知识源并行检索，筛选最相关的知识片段
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed


class LocalWikiSource:
    """本地Wiki知识源"""
    
    def __init__(self, path: Path):
        self.path = Path(path)
        self.documents = []
        self._load_documents()
    
    def _load_documents(self):
        """加载文档"""
        if not self.path.exists():
            return
        
        for md_file in self.path.rglob("*.md"):
            try:
                content = md_file.read_text(encoding='utf-8')
                self.documents.append({
                    'file': str(md_file.relative_to(self.path)),
                    'title': self._extract_title(content),
                    'content': content,
                    'length': len(content)
                })
            except Exception as e:
                print(f"[WARN] 加载文档失败 {md_file}: {e}")
    
    def _extract_title(self, content: str) -> str:
        """提取标题"""
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                return line.replace('# ', '').strip()
        return "无标题"
    
    def search(self, keyword: str, max_results: int = 3) -> List[Dict]:
        """检索文档"""
        results = []
        
        for doc in self.documents:
            # 简单关键词匹配
            if keyword in doc['content'] or keyword in doc['title']:
                # 提取摘要
                summary = self._extract_summary(doc['content'], keyword)
                
                results.append({
                    'title': doc['title'],
                    'file': doc['file'],
                    'summary': summary,
                    'relevance': doc['content'].count(keyword)
                })
        
        # 按相关度排序
        results.sort(key=lambda x: x['relevance'], reverse=True)
        return results[:max_results]
    
    def _extract_summary(self, content: str, keyword: str, max_length: int = 200) -> str:
        """提取包含关键词的摘要"""
        idx = content.find(keyword)
        if idx == -1:
            return content[:max_length]
        
        start = max(0, idx - 50)
        end = min(len(content), idx + max_length)
        return content[start:end].replace('\n', ' ')


class MultiSourceRetrievalAgent:
    """多源检索Agent"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.sources = {}
        self._init_sources()
    
    def _init_sources(self):
        """初始化知识源"""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from config import KNOWLEDGE_SOURCES
        
        for source_name, source_config in KNOWLEDGE_SOURCES.items():
            if not source_config.get('enabled', False):
                continue
            
            try:
                if source_config['type'] == 'local':
                    if source_config['format'] == 'markdown':
                        self.sources[source_name] = LocalWikiSource(
                            Path(source_config['path'])
                        )
                    elif source_config['format'] == 'obsidian_vault':
                        self.sources[source_name] = LocalWikiSource(
                            Path(source_config['path'])
                        )
                    # 其他格式...
                
                elif source_config['type'] == 'api':
                    # API知识源需要额外实现
                    print(f"[INFO] API知识源 {source_name} 需要配置API key")
                    continue
                
                print(f"[INFO] 知识源 {source_name} 初始化成功")
            
            except Exception as e:
                print(f"[WARN] 知识源 {source_name} 初始化失败: {e}")
    
    def search(self, topic: str, max_per_source: int = 3) -> List[Dict]:
        """
        多源并行检索
        
        Args:
            topic: 检索主题
            max_per_source: 每个知识源最大返回数
            
        Returns:
            合并后的检索结果
        """
        all_results = []
        
        # 并行检索
        with ThreadPoolExecutor(max_workers=len(self.sources)) as executor:
            futures = {}
            
            for source_name, source in self.sources.items():
                future = executor.submit(source.search, topic, max_per_source)
                futures[future] = source_name
            
            for future in as_completed(futures):
                source_name = futures[future]
                try:
                    results = future.result()
                    for r in results:
                        r['source_type'] = source_name
                    all_results.extend(results)
                    print(f"[INFO] {source_name} 检索到 {len(results)} 条结果")
                except Exception as e:
                    print(f"[WARN] {source_name} 检索失败: {e}")
        
        # 去重（按标题）
        seen_titles = set()
        unique_results = []
        for r in all_results:
            if r['title'] not in seen_titles:
                seen_titles.add(r['title'])
                unique_results.append(r)
        
        # 按相关度排序
        unique_results.sort(key=lambda x: x.get('relevance', 0), reverse=True)
        
        return unique_results[:10]  # 返回Top 10
    
    def format_for_prompt(self, results: List[Dict]) -> str:
        """格式化为Prompt可用的文本"""
        lines = []
        
        for i, r in enumerate(results, 1):
            lines.append(f"[来源:{r['source_type']}] {r['file'] or r['title']}")
            lines.append(f"标题：{r['title']}")
            lines.append(f"摘要：{r['summary'][:150]}...")
            lines.append("")
        
        return "\n".join(lines)


# 测试
if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from config import KNOWLEDGE_SOURCES
    
    # 启用本地Wiki用于测试
    KNOWLEDGE_SOURCES['local_wiki']['enabled'] = True
    KNOWLEDGE_SOURCES['local_wiki']['path'] = Path(__file__).parent.parent / 'wiki-samples'
    
    agent = MultiSourceRetrievalAgent()
    
    # 测试检索
    results = agent.search("低倍率病组", max_per_source=3)
    
    print(f"\n检索结果：{len(results)} 条")
    for r in results:
        print(f"\n[{r['source_type']}] {r['title']}")
        print(f"  摘要：{r['summary'][:100]}...")
