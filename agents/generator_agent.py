#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
课件生成Agent
基于意图和知识片段，生成完整的培训课件
"""

import json
from typing import Dict, Any, List


class GeneratorAgent:
    """课件生成Agent"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.prompt_template = self._load_prompt()
    
    def _load_prompt(self) -> str:
        """加载Prompt模板"""
        return """# 角色
你是医院运营管理培训专家，拥有10年三甲医院培训经验。
你擅长把复杂的运营数据，翻译成临床主任听得懂的"人话"。

# 任务
基于提供的培训意图和知识片段，生成一份完整的培训课件。

# 输入

## 培训意图
{intent}

## 知识片段
{knowledge_fragments}

# 输出格式（Markdown）

---

# 第一部分：课件大纲（PPT结构）

## 封面
- 主标题：（吸引人，不超过15字）
- 副标题：（补充说明）
- 讲师/日期

## Part 1：为什么关注低倍率？（占时长15%）
- 学习目标
- 核心数据（2-3个关键数字）
- 四大影响
- 一句话总结

## Part 2：低倍率是什么？（占时长20%）
- 学习目标
- 核心定义
- 判定公式（DRG vs DIP）
- 对比表格
- 常见误区

## Part 3：低倍率病例长什么样？（占时长15%）
- 学习目标
- 典型病种举例
- 识别方法（3种）
- 实用工具

## Part 4：低倍率从哪来？（占时长10%）
- 学习目标
- 四大来源（编码/路径/患者/其他）

## Part 5：低倍率怎么管？（占时长25%）
- 学习目标
- 事前预防：三道防线
- 事中监控：4个要点
- 事后分析：四步法

## Part 6：实战案例解析（占时长15%）
- 学习目标
- 案例1：详细展开
- 案例2：简要说明

## Part 7：政策趋势与应对（占时长10%）
- 学习目标
- 政策演进
- 科室应对五步法
- 辩证思考

## 结尾页
- 核心要点回顾
- Q&A

---

# 第二部分：演讲稿（逐字稿）

## 说明
- 每页PPT对应2-3分钟讲解
- 包含：开场白、过渡语、互动提问、重点强调
- 语言风格：像主任们聊天，不是汇报工作

## 格式
【第X页：页面标题】

（开场白）
各位主任，...

（内容讲解）
这里我要重点讲的是...

（互动）
大家有没有遇到过...

（过渡）
好，概念讲完了，接下来我们看看...

---

# 第三部分：学员手册（1页）

## 核心要点（不超过5条）
1. ...
2. ...

## 行动清单
- [ ] 本周：...
- [ ] 本月：...
- [ ] 持续：...

## 延伸阅读（2-3篇）
1. 《...》
2. 《...》

---

# 语言约束（必须遵守）

## 必须做 ✅
- 用"你"而不是"你们科室"
- 每个数据配解释："这意味着..."
- 每个策略配案例："比如心内科张主任..."
- 结尾给具体行动："回去后先做这件事..."
- 用类比解释概念："就像..."

## 不能做 ❌
- 用"费用消耗指数"而不解释
- 用"加强管控"这种空话
- 超过3个数字连续出现
- 一句话超过30个字
- 只说问题不给方案

## 风格要求
- 口语化："咱们""说白了""说白了"
- 有节奏：短句为主，长短交替
- 有互动：每5分钟一个提问或举手
- 有温度：理解主任的难处，不说教

---

# 示例对比

## ❌ 差的表达
"低倍率病组的费用消耗指数低于0.7，需要加强临床路径管理，优化诊疗行为规范。"

## ✅ 好的表达
"各位主任，你们科室有没有这种情况：一个病组，医保标准是1万块，你只花了7000？

这就是低倍率——花的比标准少了30%以上。

心内科张主任上个月查了一下，他们科有25%的病例都是低倍率。什么意思？每4个病人就有1个'花少了'。

花少了不是节约，可能该做的检查没做，该用的药没用。医保飞检查出来，照样罚你。

回去后，先做这件事：把你们科前10个病种的诊疗步骤写下来，看看哪些该做没做。"
"""
    
    def generate(self, intent: Dict[str, Any], knowledge_fragments: List[Dict]) -> Dict[str, str]:
        """
        生成课件
        
        Args:
            intent: 结构化意图
            knowledge_fragments: 知识片段列表
            
        Returns:
            包含课件大纲、演讲稿、学员手册的字典
        """
        # 格式化知识片段
        knowledge_text = self._format_knowledge(knowledge_fragments)
        
        # 格式化意图
        intent_text = json.dumps(intent, ensure_ascii=False, indent=2)
        
        # 填充Prompt
        prompt = self.prompt_template.format(
            intent=intent_text,
            knowledge_fragments=knowledge_text
        )
        
        # 调用LLM
        if self.llm_client:
            response = self.llm_client.chat(prompt)
        else:
            # 模拟LLM响应
            response = self._mock_generate(intent, knowledge_fragments)
        
        # 解析输出
        return self._parse_output(response)
    
    def _format_knowledge(self, fragments: List[Dict]) -> str:
        """格式化知识片段"""
        lines = []
        
        for i, f in enumerate(fragments, 1):
            lines.append(f"## 知识片段{i}")
            lines.append(f"- 内容：{f.get('summary', '')[:200]}")
            lines.append(f"- 来源：{f.get('source_type', '未知')}")
            lines.append(f"- 可信度：{f.get('credibility', '中')}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _mock_generate(self, intent: Dict, knowledge_fragments: List[Dict]) -> str:
        """模拟生成（用于测试）"""
        # 返回简化的课件结构
        return f"""# 课件大纲

## 封面
**低倍率病种管理**
——DRG/DIP付费下的科室应对策略

## Part 1：为什么关注低倍率？（8分钟）
- 核心数据：15-25%占比，2000-5000元/例亏损
- 四大影响：经济损失、CMI值、绩效奖金、运营压力

## Part 2：低倍率是什么？（10分钟）
- 判定公式：DRG（0.4~0.5）、DIP（0.5）
- DRG vs DIP对比表格

## Part 3：低倍率病例长什么样？（8分钟）
- 典型病种：肺炎、心梗、阑尾炎
- 识别方法：费用对比、天数对比、路径检查

## Part 4：低倍率从哪来？（5分钟）
- 编码问题、路径问题、患者因素、其他

## Part 5：低倍率怎么管？（10分钟）
- 事前预防：三道防线（编码培训、路径规范、入院评估）
- 事中监控：费用日监控、天数跟踪、路径检查、预警干预
- 事后分析：四步法（收集→归因→定位→改进）

## Part 6：实战案例解析（8分钟）
- 心内科案例：急性心梗，标杆18000 vs 实际7200
- 呼吸科案例：社区肺炎

## Part 7：政策趋势与应对（5分钟）
- 科室应对五步法

## 结尾页
- 核心要点回顾
- Q&A

---

# 演讲稿（节选）

【封面页】
各位主任，今天咱们聊一个扎心的话题：低倍率病种管理...

---

# 学员手册（1页）

## 核心要点
1. 低倍率不是省钱，是可能没治好
2. 判定：费用<标杆×0.5
3. 管理：三道防线+四步法
4. 应对：五步法

## 行动清单
- [ ] 本周：统计科室低倍率病例数
- [ ] 本月：写前3个病种的诊疗清单
- [ ] 持续：每月核对10份病历编码
"""
    
    def _parse_output(self, response: str) -> Dict[str, str]:
        """解析LLM输出"""
        # 简单分割
        parts = response.split('---')
        
        result = {
            'outline': '',
            'speech': '',
            'handout': ''
        }
        
        for part in parts:
            if '课件大纲' in part:
                result['outline'] = part.strip()
            elif '演讲稿' in part:
                result['speech'] = part.strip()
            elif '学员手册' in part:
                result['handout'] = part.strip()
        
        return result


# 测试
if __name__ == "__main__":
    agent = GeneratorAgent()
    
    intent = {
        "topic": "低倍率病组管理",
        "audience": "科室主任",
        "duration": 45
    }
    
    knowledge = [
        {
            'summary': '低倍率病组的定义（费用<标准70%）、3个识别标准',
            'source_type': '本地Wiki',
            'credibility': '高'
        }
    ]
    
    result = agent.generate(intent, knowledge)
    
    print("课件大纲：")
    print(result['outline'][:500])
    print("\n...")
