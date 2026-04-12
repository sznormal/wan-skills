"""
故事板生成器 - 自动生成教学视频分镜脚本
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class Scene:
    """单个场景"""
    number: int
    name: str
    duration: int  # 秒
    description: str
    visual_elements: List[str] = field(default_factory=list)
    audio_notes: str = ""
    animation_notes: str = ""
    prompt: str = ""
    teaching_point: str = ""


@dataclass
class Storyboard:
    """完整故事板"""
    title: str
    subject: str
    topic: str
    grade: str
    total_duration: int
    scenes: List[Scene] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "title": self.title,
            "subject": self.subject,
            "topic": self.topic,
            "grade": self.grade,
            "total_duration": self.total_duration,
            "scenes": [
                {
                    "number": s.number,
                    "name": s.name,
                    "duration": s.duration,
                    "description": s.description,
                    "visual_elements": s.visual_elements,
                    "audio_notes": s.audio_notes,
                    "animation_notes": s.animation_notes,
                    "prompt": s.prompt,
                    "teaching_point": s.teaching_point
                }
                for s in self.scenes
            ],
            "created_at": self.created_at
        }
    
    def save_to_file(self, filepath: str):
        """保存到JSON文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)


class StoryboardGenerator:
    """故事板生成器"""
    
    # 标准教学视频结构模板
    STRUCTURE_TEMPLATES = {
        "概念讲解": [
            {"name": "开场引入", "ratio": 0.15, "focus": "吸引注意"},
            {"name": "概念定义", "ratio": 0.25, "focus": "核心知识"},
            {"name": "案例展示", "ratio": 0.30, "focus": "应用举例"},
            {"name": "要点总结", "ratio": 0.20, "focus": "巩固记忆"},
            {"name": "课后思考", "ratio": 0.10, "focus": "延伸思考"}
        ],
        "实验演示": [
            {"name": "实验目的", "ratio": 0.10, "focus": "明确目标"},
            {"name": "材料准备", "ratio": 0.15, "focus": "介绍器材"},
            {"name": "实验步骤", "ratio": 0.40, "focus": "过程演示"},
            {"name": "结果分析", "ratio": 0.20, "focus": "数据解读"},
            {"name": "结论总结", "ratio": 0.15, "focus": "归纳结论"}
        ],
        "历史叙事": [
            {"name": "时代背景", "ratio": 0.15, "focus": "历史环境"},
            {"name": "事件经过", "ratio": 0.40, "focus": "详细过程"},
            {"name": "人物刻画", "ratio": 0.20, "focus": "关键人物"},
            {"name": "历史意义", "ratio": 0.15, "focus": "影响分析"},
            {"name": "现实启示", "ratio": 0.10, "focus": "当代价值"}
        ],
        "文学赏析": [
            {"name": "作品引入", "ratio": 0.10, "focus": "背景介绍"},
            {"name": "精彩片段", "ratio": 0.35, "focus": "内容展示"},
            {"name": "艺术手法", "ratio": 0.25, "focus": "写作技巧"},
            {"name": "情感分析", "ratio": 0.20, "focus": "情感解读"},
            {"name": "推荐阅读", "ratio": 0.10, "focus": "延伸推荐"}
        ],
        "复习总结": [
            {"name": "知识框架", "ratio": 0.25, "focus": "整体脉络"},
            {"name": "重点回顾", "ratio": 0.35, "focus": "核心要点"},
            {"name": "易错提示", "ratio": 0.20, "focus": "常见错误"},
            {"name": "练习巩固", "ratio": 0.20, "focus": "应用练习"}
        ]
    }
    
    # 视觉元素模板
    VISUAL_ELEMENTS = {
        "开场": ["标题文字", "背景图案", "装饰元素"],
        "定义": ["概念图", "关键词标注", "示意图"],
        "讲解": ["示意图", "流程图", "对比表格"],
        "案例": ["情境图", "案例照片", "示意图"],
        "总结": ["思维导图", "要点列表", "关键词"],
        "过渡": ["箭头", "时间线", "分节符"]
    }
    
    # 动画效果模板
    ANIMATION_TEMPLATES = {
        "引入": "fade in, gentle zoom in",
        "展开": "smooth transition, gradual reveal",
        "强调": "highlight pulse, color shift",
        "切换": "slide transition, cross fade",
        "总结": "zoom out, fade out"
    }
    
    def __init__(self):
        """初始化生成器"""
        self.default_template = "概念讲解"
    
    def generate(
        self,
        topic: str,
        subject: str,
        grade: str,
        template: Optional[str] = None,
        total_duration: int = 30,
        custom_scenes: Optional[List[Dict]] = None
    ) -> Storyboard:
        """
        生成故事板
        
        Args:
            topic: 知识点名称
            subject: 学科
            grade: 年级
            template: 模板类型
            total_duration: 总时长（秒）
            custom_scenes: 自定义场景列表
            
        Returns:
            完整的故事板对象
        """
        template = template or self.default_template
        template_scenes = self.STRUCTURE_TEMPLATES.get(template, self.STRUCTURE_TEMPLATES["概念讲解"])
        
        scenes = []
        
        if custom_scenes:
            # 使用自定义场景
            for i, scene_config in enumerate(custom_scenes):
                scene = self._create_scene(
                    number=i + 1,
                    config=scene_config,
                    topic=topic
                )
                scenes.append(scene)
        else:
            # 使用模板生成
            for i, scene_config in enumerate(template_scenes):
                duration = max(3, int(total_duration * scene_config["ratio"]))
                
                scene = Scene(
                    number=i + 1,
                    name=scene_config["name"],
                    duration=duration,
                    description=f"{topic} - {scene_config['focus']}",
                    teaching_point=scene_config["focus"],
                    visual_elements=self._get_visual_elements(scene_config["name"]),
                    animation_notes=self._get_animation_notes(scene_config["name"])
                )
                scenes.append(scene)
        
        # 计算实际总时长
        actual_duration = sum(s.duration for s in scenes)
        
        return Storyboard(
            title=f"{subject} - {topic}",
            subject=subject,
            topic=topic,
            grade=grade,
            total_duration=actual_duration,
            scenes=scenes
        )
    
    def _create_scene(
        self,
        number: int,
        config: Dict,
        topic: str
    ) -> Scene:
        """创建单个场景"""
        return Scene(
            number=number,
            name=config.get("name", f"场景{number}"),
            duration=config.get("duration", 5),
            description=config.get("description", ""),
            teaching_point=config.get("focus", ""),
            visual_elements=config.get("visual_elements", []),
            animation_notes=config.get("animation", "")
        )
    
    def _get_visual_elements(self, scene_name: str) -> List[str]:
        """获取场景对应的视觉元素"""
        for key, elements in self.VISUAL_ELEMENTS.items():
            if key in scene_name:
                return elements
        return ["示意图", "标注文字"]
    
    def _get_animation_notes(self, scene_name: str) -> str:
        """获取场景对应的动画效果"""
        for key, animation in self.ANIMATION_TEMPLATES.items():
            if key in scene_name:
                return animation
        return "smooth transition"
    
    def generate_prompts(
        self,
        storyboard: Storyboard,
        prompt_generator
    ) -> Storyboard:
        """
        为故事板生成提示词
        
        Args:
            storyboard: 故事板对象
            prompt_generator: 提示词生成器实例
            
        Returns:
            带有完整提示词的故事板
        """
        for scene in storyboard.scenes:
            # 构建场景特定的提示词
            scene_prompt = prompt_generator.generate_video_prompt(
                type('Config', (), {
                    'subject': storyboard.subject,
                    'topic': f"{storyboard.topic} - {scene.name}",
                    'grade': storyboard.grade,
                    'style': 'animation',
                    'duration': scene.duration,
                    'include_labels': True,
                    'show_process': scene.number == 2
                })()
            )
            scene.prompt = scene_prompt
        
        return storyboard
    
    def export_to_script(self, storyboard: Storyboard) -> str:
        """
        导出为标准分镜脚本格式
        
        Args:
            storyboard: 故事板对象
            
        Returns:
            格式化的脚本文本
        """
        script_lines = [
            "=" * 60,
            f"分镜脚本: {storyboard.title}",
            "=" * 60,
            f"学科: {storyboard.subject}",
            f"年级: {storyboard.grade}",
            f"总时长: {storyboard.total_duration}秒",
            f"生成时间: {storyboard.created_at}",
            "-" * 60,
            ""
        ]
        
        for scene in storyboard.scenes:
            script_lines.extend([
                f"【场景 {scene.number}】{scene.name}",
                f"  时长: {scene.duration}秒",
                f"  描述: {scene.description}",
                f"  教学重点: {scene.teaching_point}",
                f"  视觉元素: {', '.join(scene.visual_elements)}",
                f"  动画效果: {scene.animation_notes}",
                f"  画面提示: {scene.prompt}",
                ""
            ])
        
        script_lines.append("=" * 60)
        script_lines.append("脚本结束")
        
        return "\n".join(script_lines)


def main():
    """示例用法"""
    generator = StoryboardGenerator()
    
    # 生成故事板
    storyboard = generator.generate(
        topic="DNA复制过程",
        subject="生物",
        grade="高中",
        template="实验演示",
        total_duration=30
    )
    
    print("=== 生成的故事板 ===")
    print(f"标题: {storyboard.title}")
    print(f"总时长: {storyboard.total_duration}秒")
    print(f"场景数量: {len(storyboard.scenes)}")
    
    print("\n=== 分镜详情 ===")
    for scene in storyboard.scenes:
        print(f"\n场景{scene.number}: {scene.name} ({scene.duration}秒)")
        print(f"  描述: {scene.description}")
        print(f"  教学重点: {scene.teaching_point}")
        print(f"  视觉元素: {scene.visual_elements}")
    
    # 导出脚本
    script = generator.export_to_script(storyboard)
    print("\n=== 导出脚本 ===")
    print(script)
    
    # 保存到文件
    storyboard.save_to_file("./output/dna_replication_storyboard.json")
    print("\n故事板已保存到 ./output/dna_replication_storyboard.json")


if __name__ == "__main__":
    main()
