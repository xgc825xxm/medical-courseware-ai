#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
意图识别Agent
解析用户自然语言输入，提取结构化培训意图
"""

import json
import re
from typing import Dict, Any, Optional


class IntentAgent:
    """意图识别Agent"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.prompt_template = self._load_prompt()
    
    def _load_prompt(self) -> str:
        """加载Prompt模板"""
        return """# 角色
你是医院培训需求分析专家，拥有10年三甲医院培训策划经验。

# 任务
解析用户的自然语言输入，提取关键的培训意图信息。
如果信息缺失，标注为"待确认"，不猜测。

# 输入
用户说：{user_input}

# 输出格式（严格JSON）
{{
  "topic": "培训主题（必填）",
  "audience": "受众：科室主任/护士长/全院职工/医保办（必填）",
  "duration": "时长分钟数，数字（必填，默认45）",
  "department": "重点科室，如心内科/骨科/全院（可选）",
  "focus": "重点方向，如识别方法/管理策略/案例分析（可选）",
  "language_style": "语言风格：专业严谨/通俗接地气/互动讨论（默认通俗接地气）",
  "output_format": ["课件大纲", "演讲稿", "学员手册"],
  "missing_info": ["缺失的信息列表，用于追问"],
  "confidence": "置信度：high/medium/low"
}}

# 解析规则

## 主题识别
- 从输入中提取核心培训内容
- 如果是简称或口语，转换为标准术语
- 示例："低倍率" → "低倍率病组管理"

## 受众识别
- 根据称呼判断：主任→科室主任，护士长→护士，科长→职能科室
- 未明确时，根据主题推断

## 时长识别
- 明确数字：直接用
- 模糊描述："短时间"→30分钟，"详细讲"→60分钟，未提→45分钟

## 重点识别
- "重点讲..." → focus字段
- "特别是..." → focus字段

# 示例

## 示例1：信息完整
输入："给心内科主任讲45分钟低倍率病组管理，重点讲怎么识别"
输出：
{{
  "topic": "低倍率病组管理",
  "audience": "科室主任",
  "duration": 45,
  "department": "心内科",
  "focus": "识别方法",
  "language_style": "通俗接地气",
  "output_format": ["课件大纲", "演讲稿", "学员手册"],
  "missing_info": [],
  "confidence": "high"
}}

# 约束
- 必须输出合法JSON，不要有任何额外文字
- 不确定的信息标注"待确认"，绝不猜测
- 主题必须转换为标准医院管理术语
- 时长必须是数字，不要带"分钟"字样
"""
    
    def parse(self, user_input: str) -> Dict[str, Any]:
        """
        解析用户输入
        
        Args:
            user_input: 用户的自然语言需求
            
        Returns:
            结构化的意图字典
        """
        # 填充Prompt
        prompt = self.prompt_template.format(user_input=user_input)
        
        # 调用LLM
        if self.llm_client:
            response = self.llm_client.chat(prompt)
        else:
            # 模拟LLM响应（实际使用时替换为真实调用）
            response = self._mock_parse(user_input)
        
        # 解析JSON
        try:
            intent = json.loads(response)
            return intent
        except json.JSONDecodeError:
            # 如果LLM输出不是纯JSON，尝试提取
            return self._extract_json(response)
    
    def _mock_parse(self, user_input: str) -> str:
        """模拟解析（用于测试）"""
        # 简单的规则匹配
        intent = {
            "topic": "低倍率病组管理",
            "audience": "科室主任",
            "duration": 45,
            "department": "心内科",
            "focus": "识别方法",
            "language_style": "通俗接地气",
            "output_format": ["课件大纲", "演讲稿", "学员手册"],
            "missing_info": [],
            "confidence": "high"
        }
        return json.dumps(intent, ensure_ascii=False)
    
    def _extract_json(self, text: str) -> Dict[str, Any]:
        """从文本中提取JSON"""
        # 查找JSON代码块
        pattern = r'```(?:json)?\s*(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        
        if matches:
            try:
                return json.loads(matches[0])
            except:
                pass
        
        # 查找花括号包裹的内容
        pattern = r'\{.*?\}'
        matches = re.findall(pattern, text, re.DOTALL)
        
        for match in matches:
            try:
                return json.loads(match)
            except:
                continue
        
        # 返回默认值
        return {
            "topic": "待确认",
            "audience": "待确认",
            "duration": 45,
            "confidence": "low",
            "missing_info": ["无法解析输入，请明确培训主题和受众"]
        }


# 测试
if __name__ == "__main__":
    agent = IntentAgent()
    
    test_input = "给心内科主任讲45分钟低倍率病组管理，重点讲怎么识别"
    result = agent.parse(test_input)
    
    print("输入：", test_input)
    print("输出：")
    print(json.dumps(result, ensure_ascii=False, indent=2))
