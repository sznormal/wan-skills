"""
智能提示词生成器 - 根据教学知识点自动生成高质量提示词
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class Subject(Enum):
    """学科枚举"""
    BIOLOGY = "生物"
    PHYSICS = "物理"
    CHEMISTRY = "化学"
    HISTORY = "历史"
    GEOGRAPHY = "地理"
    LITERATURE = "语文"
    MATH = "数学"
    GENERAL = "通用"


class TeachingStyle(Enum):
    """教学风格枚举"""
    ANIMATION = "知识动画风"  # 简洁扁平，适合概念讲解
    TECH_SCI_FI = "科幻科技风"  # 适合物理、化学
    HISTORICAL = "历史复古风"  # 适合历史、文学
    NATURAL = "自然写实风"  # 适合生物、地理
    MINIMALIST = "简约线条风"  # 适合数学、抽象概念
    COLORFUL = "多彩插画风"  # 适合小学、初中


@dataclass
class TeachingPromptConfig:
    """教学提示词配置"""
    subject: Subject
    topic: str
    grade: str  # 小学/初中/高中/大学
    style: TeachingStyle
    duration: int = 5  # 秒
    include_labels: bool = True  # 是否包含标注
    show_process: bool = True  # 是否展示过程


class PromptGenerator:
    """教学提示词生成器"""
    
    # 学科特定提示词模板
    SUBJECT_TEMPLATES = {
        Subject.BIOLOGY: {
            "prefix": "Biology educational animation",
            "elements": ["cell structure", "biological process", "scientific illustration"],
            "details": "clear cell boundaries, color-coded organelles, accurate biological structures"
        },
        Subject.PHYSICS: {
            "prefix": "Physics experiment demonstration",
            "elements": ["scientific visualization", "vector diagrams", "measurement tools"],
            "details": "clear force arrows, labeled measurements, professional physics diagram style"
        },
        Subject.CHEMISTRY: {
            "prefix": "Chemistry molecular animation",
            "elements": ["molecular structure", "reaction process", "electron flow"],
            "details": "ball-and-stick models, color-coded atoms, reaction arrows clearly shown"
        },
        Subject.HISTORY: {
            "prefix": "Historical scene recreation",
            "elements": ["period-accurate costumes", "historical architecture", "cultural details"],
            "details": "authentic historical atmosphere, documentary film style, educational context"
        },
        Subject.GEOGRAPHY: {
            "prefix": "Geography visualization",
            "elements": ["map elements", "terrain features", "climate patterns"],
            "details": "accurate geographical features, compass rose, scale indicators"
        },
        Subject.LITERATURE: {
            "prefix": "Literary scene illustration",
            "elements": ["narrative scene", "emotional atmosphere", "cultural elements"],
            "details": "expressive character poses, vivid scene description, artistic composition"
        },
        Subject.MATH: {
            "prefix": "Mathematics concept visualization",
            "elements": ["geometric shapes", "coordinate systems", "formula diagrams"],
            "details": "clean lines, clear labels, step-by-step progression"
        },
        Subject.GENERAL: {
            "prefix": "Educational illustration",
            "elements": ["concept diagram", "step-by-step process", "clear visual hierarchy"],
            "details": "professional teaching materials style, engaging visuals"
        }
    }
    
    # 风格特定提示词
    STYLE_TEMPLATES = {
        TeachingStyle.ANIMATION: {
            "suffix": "flat design, vector graphics, clean lines, modern educational animation",
            "negative": "photorealistic, cluttered, complex background"
        },
        TeachingStyle.TECH_SCI_FI: {
            "suffix": "futuristic technology style, holographic displays, sci-fi aesthetics, blue glow effects",
            "negative": "retro, vintage, outdated technology"
        },
        TeachingStyle.HISTORICAL: {
            "suffix": "period painting style, classical art techniques, warm nostalgic tones, museum quality",
            "negative": "modern elements, cartoon style, contemporary design"
        },
        TeachingStyle.NATURAL: {
            "suffix": "nature documentary style, realistic textures, environmental harmony, wildlife photography",
            "negative": "artificial, synthetic, sterile environment"
        },
        TeachingStyle.MINIMALIST: {
            "suffix": "minimalist design, clean white background, simple geometric shapes, elegant typography",
            "negative": "busy background, excessive details, cluttered composition"
        },
        TeachingStyle.COLORFUL: {
            "suffix": "vibrant colors, playful illustration, friendly characters, engaging for young learners",
            "negative": "dull colors, scary imagery, complex diagrams"
        }
    }
    
    # 年级适配关键词
    GRADE_ADAPTATIONS = {
        "小学": {
            "complexity": "simple and clear, big elements, limited colors, easy to understand",
            "characters": "friendly cartoon characters, relatable examples"
        },
        "初中": {
            "complexity": "moderate detail, balanced information density, clear labels",
            "characters": "some illustrative characters, age-appropriate visuals"
        },
        "高中": {
            "complexity": "detailed and accurate, scientific precision, comprehensive information",
            "characters": "professional diagrams, technical illustrations"
        },
        "大学": {
            "complexity": "highly detailed, academic level accuracy, professional documentation",
            "characters": "schematic diagrams, technical schematics"
        }
    }
    
    def generate_image_prompt(self, config: TeachingPromptConfig) -> str:
        """
        生成文生图提示词
        
        Args:
            config: 教学提示词配置
            
        Returns:
            优化的英文提示词
        """
        # 获取学科模板
        subject_tpl = self.SUBJECT_TEMPLATES.get(config.subject, self.SUBJECT_TEMPLATES[Subject.GENERAL])
        
        # 获取风格模板
        style_tpl = self.STYLE_TEMPLATES.get(config.style)
        
        # 获取年级适配
        grade_tpl = self.GRADE_ADAPTATIONS.get(config.grade, self.GRADE_ADAPTATIONS["高中"])
        
        # 构建提示词
        prompt_parts = [
            subject_tpl["prefix"],  # 学科前缀
            config.topic,  # 具体知识点
            f"{config.grade} level",  # 年级
            subject_tpl["elements"][0] if subject_tpl["elements"] else "",  # 元素
            subject_tpl["details"],  # 细节
            grade_tpl["complexity"],  # 年级适配
            style_tpl["suffix"] if style_tpl else "",  # 风格后缀
            "high quality, 4K resolution, professional teaching materials"  # 质量要求
        ]
        
        if config.include_labels:
            prompt_parts.append("clearly labeled text, educational annotations")
        
        return ", ".join(filter(None, prompt_parts))
    
    def generate_video_prompt(self, config: TeachingPromptConfig) -> str:
        """
        生成文生视频提示词
        
        Args:
            config: 教学提示词配置
            
        Returns:
            优化的英文视频提示词
        """
        # 首先生成图片提示词作为基础
        base_prompt = self.generate_image_prompt(config)
        
        # 添加运动描述
        motion_descriptions = self._get_motion_description(config)
        
        video_prompt = f"{base_prompt}, {motion_descriptions}"
        
        return video_prompt
    
    def _get_motion_description(self, config: TeachingPromptConfig) -> str:
        """根据知识点生成运动描述"""
        topic_lower = config.topic.lower()
        
        # 通用运动关键词
        motion_templates = {
            "process": "gradual transformation, step-by-step animation, smooth transitions between stages",
            "cycle": "continuous loop animation, circular motion, seamless repeating cycle",
            "structure": "rotating view, 360-degree examination, detailed component zoom-in",
            "interaction": "dynamic interaction between elements, particle flow visualization",
            "reaction": "before and after comparison, energy release visualization, timing sequence"
        }
        
        # 根据知识点关键词匹配运动类型
        for key, motion in motion_templates.items():
            if key in topic_lower:
                return motion
        
        # 默认运动描述
        return "smooth educational animation, professional pacing, clear visual transitions"
    
    def generate_negative_prompt(self, config: TeachingPromptConfig) -> str:
        """
        生成负面提示词
        
        Args:
            config: 教学提示词配置
            
        Returns:
            负面提示词
        """
        style_tpl = self.STYLE_TEMPLATES.get(config.style, {})
        grade_tpl = self.GRADE_ADAPTATIONS.get(config.grade, self.GRADE_ADAPTATIONS["高中"])
        
        common_negatives = [
            "blurry, low quality, distorted",
            "incorrect information, misleading content",
            "violent, inappropriate for educational context",
            "watermark, text overlay, copyright symbols"
        ]
        
        style_negative = style_tpl.get("negative", "")
        grade_negative = grade_tpl.get("characters", "").replace("friendly cartoon characters", "")
        
        negatives = [n for n in [common_negatives, style_negative, grade_negative] if n]
        return ", ".join(filter(None, negatives))
    
    def generate_storyboard_prompts(
        self, 
        config: TeachingPromptConfig,
        num_scenes: int = 4
    ) -> List[Dict[str, str]]:
        """
        生成分镜提示词
        
        Args:
            config: 教学提示词配置
            num_scenes: 场景数量
            
        Returns:
            分镜列表，每个包含scene_description和prompt
        """
        topic = config.topic
        duration_per_scene = max(3, config.duration // num_scenes)
        
        # 标准教学视频结构
        scene_structures = [
            {
                "name": "概念引入",
                "duration": duration_per_scene,
                "description": f"Introduction to {topic}, establishing context",
                "focus": "吸引注意力，建立知识背景"
            },
            {
                "name": "核心讲解",
                "duration": duration_per_scene * 2,
                "description": f"Detailed explanation of {topic}, main content",
                "focus": "详细展示知识点内容"
            },
            {
                "name": "关键强调",
                "duration": duration_per_scene,
                "description": f"Key points of {topic}, important highlights",
                "focus": "强调重点和难点"
            },
            {
                "name": "总结回顾",
                "duration": duration_per_scene,
                "description": f"Summary of {topic}, review and recap",
                "focus": "梳理知识点脉络"
            }
        ]
        
        storyboard = []
        for i, scene in enumerate(scene_structures[:num_scenes]):
            scene_config = TeachingPromptConfig(
                subject=config.subject,
                topic=f"{config.topic} - {scene['name']}",
                grade=config.grade,
                style=config.style,
                duration=scene['duration'],
                include_labels=True,
                show_process=(i == 1)  # 核心讲解时展示过程
            )
            
            storyboard.append({
                "scene_number": i + 1,
                "scene_name": scene['name'],
                "duration": scene['duration'],
                "description": scene['description'],
                "teaching_focus": scene['focus'],
                "prompt": self.generate_video_prompt(scene_config)
            })
        
        return storyboard


def main():
    """示例用法"""
    generator = PromptGenerator()
    
    # 创建配置
    config = TeachingPromptConfig(
        subject=Subject.BIOLOGY,
        topic="mitosis cell division",
        grade="高中",
        style=TeachingStyle.ANIMATION,
        duration=20,
        include_labels=True
    )
    
    print("=== 配置信息 ===")
    print(f"学科: {config.subject.value}")
    print(f"知识点: {config.topic}")
    print(f"年级: {config.grade}")
    print(f"风格: {config.style.value}")
    
    print("\n=== 生成的图片提示词 ===")
    print(generator.generate_image_prompt(config))
    
    print("\n=== 生成的视频提示词 ===")
    print(generator.generate_video_prompt(config))
    
    print("\n=== 生成分镜提示词 ===")
    storyboard = generator.generate_storyboard_prompts(config, num_scenes=4)
    for scene in storyboard:
        print(f"\n场景 {scene['scene_number']}: {scene['scene_name']}")
        print(f"时长: {scene['duration']}秒")
        print(f"教学重点: {scene['teaching_focus']}")
        print(f"提示词: {scene['prompt']}")


if __name__ == "__main__":
    main()
