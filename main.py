#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
医院管理培训课件生成系统
多Agent协作，多源知识库检索
"""

import json
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from agents.intent_agent import IntentAgent
from agents.retrieval_agent import MultiSourceRetrievalAgent
from agents.generator_agent import GeneratorAgent
from config import KNOWLEDGE_SOURCES, OUTPUT_CONFIG


class CoursewareSystem:
    """课件生成系统主类"""
    
    def __init__(self):
        self.intent_agent = IntentAgent()
        self.retrieval_agent = MultiSourceRetrievalAgent()
        self.generator_agent = GeneratorAgent()
    
    def run(self, user_input: str, save_output: bool = True) -> dict:
        """
        运行完整流程
        
        Args:
            user_input: 用户输入
            save_output: 是否保存输出
            
        Returns:
            最终结果
        """
        print("=" * 60)
        print("医院管理培训课件生成系统")
        print("=" * 60)
        
        # Step 1: 意图识别
        print("\n[Step 1/3] 意图识别...")
        intent = self.intent_agent.parse(user_input)
        print(f"✓ 主题：{intent.get('topic', '待确认')}")
        print(f"✓ 受众：{intent.get('audience', '待确认')}")
        print(f"✓ 时长：{intent.get('duration', 45)}分钟")
        
        # Step 2: 知识检索
        print("\n[Step 2/3] 多源知识检索...")
        knowledge_fragments = self.retrieval_agent.search(
            topic=intent.get('topic', ''),
            max_per_source=3
        )
        print(f"✓ 检索到 {len(knowledge_fragments)} 条知识片段")
        for k in knowledge_fragments[:3]:
            print(f"  - [{k.get('source_type', '?')}] {k.get('title', '?')[:30]}...")
        
        # Step 3: 课件生成
        print("\n[Step 3/3] 课件生成...")
        result = self.generator_agent.generate(intent, knowledge_fragments)
        print("✓ 课件生成完成")
        print(f"  - 课件大纲：{len(result.get('outline', ''))} 字")
        print(f"  - 演讲稿：{len(result.get('speech', ''))} 字")
        print(f"  - 学员手册：{len(result.get('handout', ''))} 字")
        
        # 保存输出
        if save_output:
            self._save_output(intent, knowledge_fragments, result)
        
        print("\n" + "=" * 60)
        print("完成！")
        print("=" * 60)
        
        return {
            'intent': intent,
            'knowledge': knowledge_fragments,
            'courseware': result
        }
    
    def _save_output(self, intent: dict, knowledge: list, result: dict):
        """保存输出到文件"""
        output_dir = OUTPUT_CONFIG['output_dir']
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        topic = intent.get('topic', '未知主题').replace('/', '-')
        
        # 保存意图
        intent_file = output_dir / f"01_intent_{topic}.json"
        with open(intent_file, 'w', encoding='utf-8') as f:
            json.dump(intent, f, ensure_ascii=False, indent=2)
        
        # 保存知识片段
        knowledge_file = output_dir / f"02_knowledge_{topic}.md"
        with open(knowledge_file, 'w', encoding='utf-8') as f:
            f.write("# 知识片段\n\n")
            for i, k in enumerate(knowledge, 1):
                f.write(f"## 片段{i}\n")
                f.write(f"- 标题：{k.get('title', '')}\n")
                f.write(f"- 来源：{k.get('source_type', '')}\n")
                f.write(f"- 摘要：{k.get('summary', '')[:200]}...\n\n")
        
        # 保存课件
        courseware_file = output_dir / f"03_courseware_{topic}.md"
        with open(courseware_file, 'w', encoding='utf-8') as f:
            f.write(result.get('outline', ''))
            f.write("\n\n---\n\n")
            f.write(result.get('speech', ''))
            f.write("\n\n---\n\n")
            f.write(result.get('handout', ''))
        
        print(f"\n输出已保存到：{output_dir}")


def main():
    """主函数"""
    # 创建系统
    system = CoursewareSystem()
    
    # 用户输入
    user_input = input("\n请输入培训需求：\n> ").strip()
    
    if not user_input:
        # 使用默认示例
        user_input = "给心内科主任讲45分钟低倍率病组管理，重点讲怎么识别"
        print(f"使用默认示例：{user_input}")
    
    # 运行
    result = system.run(user_input)
    
    # 显示结果
    print("\n生成的课件大纲预览：")
    print("-" * 60)
    print(result['courseware']['outline'][:500])
    print("...")


if __name__ == "__main__":
    main()
