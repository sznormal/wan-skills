#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
教学概念可视化器 - 核心脚本
调用阿里万相Wan 2.7 API生成教学可视化素材
"""

import os
import sys
import json
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# ============ 配置 ============
DEFAULT_OUTPUT_DIR = os.getenv("EDU_OUTPUT_DIR", "./edu_visuals")
WAN_API_KEY = os.getenv("WAN_API_KEY", "")
WAN_BASE_URL = os.getenv("WAN_BASE_URL", "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation")


class ConceptType(Enum):
    """概念类型"""
    DEFINITION = "definition"  # 定义类
    PRINCIPLE = "principle"     # 原理类
    PROCESS = "process"         # 过程类
    COMPARISON = "comparison"   # 对比类
    STORY = "story"            # 故事类


class OutputFormat(Enum):
    """输出格式"""
    IMAGE = "image"   # 静态图
    VIDEO = "video"   # 动态视频
    STORYBOARD = "storyboard"  # 故事板


class Subject(Enum):
    """学科领域"""
    MATH = "数学"
    PHYSICS = "物理"
    CHEMISTRY = "化学"
    BIOLOGY = "生物"
    HISTORY = "历史"
    GEOGRAPHY = "地理"
    GENERAL = "通用"


@dataclass
class VisualizationRequest:
    """可视化请求"""
    concept: str                    # 概念描述
    concept_type: ConceptType       # 概念类型
    subject: Subject                # 学科
    output_format: OutputFormat     # 输出格式
    style: str = "illustration"     # 风格
    target_audience: str = "初中"   # 目标受众
    additional_context: str = ""    # 额外上下文


@dataclass
class VisualizationResult:
    """可视化结果"""
    success: bool
    file_paths: List[str]
    prompt_used: str
    message: str
    suggestions: str = ""


# ============ 提示词模板 ============
PROMPT_TEMPLATES = {
    ConceptType.DEFINITION: {
        "template": """
{concept_type_prompt}
请创建一张教学用的概念示意图，风格为{style}。

概念：{concept}
学科：{subject}
目标学生：{target_audience}

要求：
1. 使用生活化的比喻来解释这个概念，让学生容易理解
2. 画面清晰、重点突出，适合课堂展示
3. 包含简洁的文字标注（中文）
4. 色彩明快，适合学生观看
{additional_requirements}

请生成一张高质量的教学示意图。
""",
        "concept_type_prompt": "【概念比喻可视化】"
    },
    
    ConceptType.PRINCIPLE: {
        "template": """
{concept_type_prompt}
请创建一张分步骤讲解原理的教学图，风格为{style}。

原理：{concept}
学科：{subject}
目标学生：{target_audience}

要求：
1. 将原理分解为3-4个关键步骤
2. 每个步骤用编号标注
3. 用箭头或流程线连接各步骤
4. 包含简洁的中文说明文字
5. 突出关键变量和变化过程
{additional_requirements}

请生成一张清晰的原理分解图。
""",
        "concept_type_prompt": "【原理分解可视化】"
    },
    
    ConceptType.PROCESS: {
        "template": """
{concept_type_prompt}
请创建一段展示动态过程的教学视频，时长约15-30秒。

过程：{concept}
学科：{subject}
目标学生：{target_audience}

要求：
1. 清晰展示过程的各个阶段
2. 变化过程流畅自然
3. 关键节点有文字标注（中文）
4. 适合课堂播放展示
{additional_requirements}

请生成高质量的教学演示视频。
""",
        "concept_type_prompt": "【过程动态可视化】"
    },
    
    ConceptType.COMPARISON: {
        "template": """
{concept_type_prompt}
请创建一张概念对比图，风格为{style}。

对比概念：{concept}
学科：{subject}
目标学生：{target_audience}

要求：
1. 左右分栏或上下分栏对比
2. 突出两个概念的相同点和不同点
3. 用对比色区分不同概念
4. 包含清晰的中文标注
5. 适合学生记忆和理解
{additional_requirements}

请生成一张清晰的对比图。
""",
        "concept_type_prompt": "【概念对比可视化】"
    },
    
    ConceptType.STORY: {
        "template": """
{concept_type_prompt}
请创建一组故事板图片（4格），风格为{style}。

知识点：{concept}
学科：{subject}
目标学生：{target_audience}

要求：
1. 用故事化方式讲述知识点的发现或应用
2. 每格包含一个场景和简短文字说明
3. 故事连贯，有起承转合
4. 适合作为教学情境导入
{additional_requirements}

请生成4张连贯的故事板图片。
""",
        "concept_type_prompt": "【故事化讲解】"
    }
}

# 风格映射
STYLE_PROMPTS = {
    "illustration": "教育插图风格，线条清晰，色彩明快",
    "cartoon": "卡通风格，活泼有趣，适合低年级学生",
    "realistic": "写实风格，真实感强，适合高年级学生",
    "scientific": "科学插图风格，严谨专业，适合理科教学",
    "watercolor": "水彩手绘风格，艺术感强，适合文科教学",
    "minimal": "极简风格，重点突出，适合概念讲解"
}


# ============ 核心类 ============
class EduConceptVisualizer:
    """教学概念可视化器"""
    
    def __init__(self, api_key: str = None, output_dir: str = None):
        self.api_key = api_key or WAN_API_KEY
        self.output_dir = Path(output_dir or DEFAULT_OUTPUT_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.api_key:
            raise ValueError("请设置WAN_API_KEY环境变量或传入api_key参数")
    
    def visualize(self, request: VisualizationRequest) -> VisualizationResult:
        """执行可视化"""
        # 1. 构建提示词
        prompt = self._build_prompt(request)
        
        # 2. 选择模型
        model = self._select_model(request.output_format)
        
        # 3. 调用API
        try:
            if request.output_format == OutputFormat.VIDEO:
                result = self._call_video_api(prompt, model)
            else:
                result = self._call_image_api(prompt, model, request.output_format)
            
            return result
        except Exception as e:
            return VisualizationResult(
                success=False,
                file_paths=[],
                prompt_used=prompt,
                message=f"生成失败: {str(e)}"
            )
    
    def _build_prompt(self, request: VisualizationRequest) -> str:
        """构建提示词"""
        template_data = PROMPT_TEMPLATES.get(request.concept_type, PROMPT_TEMPLATES[ConceptType.DEFINITION])
        
        style_desc = STYLE_PROMPTS.get(request.style, STYLE_PROMPTS["illustration"])
        
        additional_requirements = ""
        if request.additional_context:
            additional_requirements = f"\n额外要求：{request.additional_context}"
        
        prompt = template_data["template"].format(
            concept_type_prompt=template_data["concept_type_prompt"],
            concept=request.concept,
            subject=request.subject.value,
            style=style_desc,
            target_audience=request.target_audience,
            additional_requirements=additional_requirements
        )
        
        return prompt.strip()
    
    def _select_model(self, output_format: OutputFormat) -> str:
        """选择模型"""
        if output_format == OutputFormat.VIDEO:
            return "wan2.7-t2v"
        else:
            return "wan2.7-image-pro"
    
    def _call_image_api(self, prompt: str, model: str, output_format: OutputFormat) -> VisualizationResult:
        """调用图像API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"text": prompt}
                        ]
                    }
                ]
            },
            "parameters": {
                "size": "2K",
                "n": 4 if output_format == OutputFormat.STORYBOARD else 1
            }
        }
        
        response = requests.post(
            WAN_BASE_URL,
            headers=headers,
            json=payload,
            timeout=120
        )
        
        if response.status_code != 200:
            raise Exception(f"API调用失败: {response.status_code} - {response.text}")
        
        result = response.json()
        
        # 处理返回结果
        file_paths = []
        if "output" in result and "results" in result["output"]:
            for i, item in enumerate(result["output"]["results"]):
                if "url" in item:
                    # 下载图片
                    img_url = item["url"]
                    timestamp = int(time.time())
                    file_name = f"edu_visual_{timestamp}_{i}.png"
                    file_path = self.output_dir / file_name
                    self._download_file(img_url, file_path)
                    file_paths.append(str(file_path))
        
        return VisualizationResult(
            success=True,
            file_paths=file_paths,
            prompt_used=prompt,
            message=f"成功生成{len(file_paths)}张图片",
            suggestions="可用于课堂导入、概念讲解、板书展示等场景"
        )
    
    def _call_video_api(self, prompt: str, model: str) -> VisualizationResult:
        """调用视频API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"text": prompt}
                        ]
                    }
                ]
            },
            "parameters": {
                "duration": 15
            }
        }
        
        response = requests.post(
            WAN_BASE_URL,
            headers=headers,
            json=payload,
            timeout=300
        )
        
        if response.status_code != 200:
            raise Exception(f"API调用失败: {response.status_code} - {response.text}")
        
        result = response.json()
        
        file_paths = []
        if "output" in result and "results" in result["output"]:
            for item in result["output"]["results"]:
                if "url" in item:
                    video_url = item["url"]
                    timestamp = int(time.time())
                    file_name = f"edu_visual_{timestamp}.mp4"
                    file_path = self.output_dir / file_name
                    self._download_file(video_url, file_path)
                    file_paths.append(str(file_path))
        
        return VisualizationResult(
            success=True,
            file_paths=file_paths,
            prompt_used=prompt,
            message=f"成功生成{len(file_paths)}个视频",
            suggestions="可用于实验演示、过程讲解等动态场景"
        )
    
    def _download_file(self, url: str, file_path: Path):
        """下载文件"""
        response = requests.get(url, timeout=60)
        with open(file_path, "wb") as f:
            f.write(response.content)


# ============ CLI入口 ============
def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="教学概念可视化器")
    parser.add_argument("--concept", required=True, help="概念描述")
    parser.add_argument("--type", choices=["definition", "principle", "process", "comparison", "story"], 
                       default="definition", help="概念类型")
    parser.add_argument("--subject", default="通用", help="学科领域")
    parser.add_argument("--format", choices=["image", "video", "storyboard"], 
                       default="image", help="输出格式")
    parser.add_argument("--style", default="illustration", help="风格")
    parser.add_argument("--audience", default="初中", help="目标受众")
    parser.add_argument("--output", default=DEFAULT_OUTPUT_DIR, help="输出目录")
    
    args = parser.parse_args()
    
    # 映射类型
    concept_type_map = {
        "definition": ConceptType.DEFINITION,
        "principle": ConceptType.PRINCIPLE,
        "process": ConceptType.PROCESS,
        "comparison": ConceptType.COMPARISON,
        "story": ConceptType.STORY
    }
    
    subject_map = {
        "数学": Subject.MATH,
        "物理": Subject.PHYSICS,
        "化学": Subject.CHEMISTRY,
        "生物": Subject.BIOLOGY,
        "历史": Subject.HISTORY,
        "地理": Subject.GEOGRAPHY,
        "通用": Subject.GENERAL
    }
    
    format_map = {
        "image": OutputFormat.IMAGE,
        "video": OutputFormat.VIDEO,
        "storyboard": OutputFormat.STORYBOARD
    }
    
    request = VisualizationRequest(
        concept=args.concept,
        concept_type=concept_type_map[args.type],
        subject=subject_map.get(args.subject, Subject.GENERAL),
        output_format=format_map[args.format],
        style=args.style,
        target_audience=args.audience
    )
    
    visualizer = EduConceptVisualizer(output_dir=args.output)
    result = visualizer.visualize(request)
    
    print(json.dumps({
        "success": result.success,
        "files": result.file_paths,
        "message": result.message,
        "suggestions": result.suggestions
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
