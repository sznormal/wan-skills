"""
万相教学助手 - 主入口
整合提示词生成、故事板生成和Wan 2.7 API调用
"""

import os
import json
from typing import Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass

from wanx_client import WanXClient
from generate_prompt import PromptGenerator, TeachingPromptConfig, Subject, TeachingStyle
from storyboard_generator import StoryboardGenerator


@dataclass
class LessonVideoResult:
    """教学视频生成结果"""
    success: bool
    storyboard: Optional[Dict]
    video_urls: List[str]
    image_urls: List[str]
    prompts: List[str]
    teaching_notes: str
    error: Optional[str] = None


class WanxTeachingAssistant:
    """万相教学助手主类"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        workspace: str = "./teaching_output"
    ):
        """
        初始化教学助手
        
        Args:
            api_key: 阿里云API密钥，默认从环境变量获取
            workspace: 工作目录
        """
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("请提供API密钥或设置DASHSCOPE_API_KEY环境变量")
        
        self.workspace = Path(workspace)
        self.workspace.mkdir(parents=True, exist_ok=True)
        
        # 初始化各个模块
        self.wanx_client = WanXClient(self.api_key, str(self.workspace))
        self.prompt_generator = PromptGenerator()
        self.storyboard_generator = StoryboardGenerator()
        
        # 加载配置
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """加载配置文件"""
        config_path = Path(__file__).parent / "config.json"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def generate_lesson_video(
        self,
        subject: str,
        topic: str,
        grade: str = "高中",
        style: str = "知识动画风",
        duration: int = 30,
        template: Optional[str] = None
    ) -> LessonVideoResult:
        """
        生成完整的教学视频
        
        Args:
            subject: 学科（如"生物"、"物理"）
            topic: 知识点（如"细胞分裂"）
            grade: 年级（如"高中"、"初中"）
            style: 教学风格（如"知识动画风"）
            duration: 视频总时长（秒）
            template: 故事板模板
            
        Returns:
            包含视频URL、分镜信息和教学笔记的结果对象
        """
        try:
            # Step 1: 创建提示词配置
            config = TeachingPromptConfig(
                subject=self._get_subject_enum(subject),
                topic=topic,
                grade=grade,
                style=self._get_style_enum(style),
                duration=duration,
                include_labels=True
            )
            
            # Step 2: 生成故事板
            print(f"正在为「{topic}」生成故事板...")
            storyboard = self.storyboard_generator.generate(
                topic=topic,
                subject=subject,
                grade=grade,
                template=template,
                total_duration=duration
            )
            
            # Step 3: 生成各场景的提示词
            storyboard = self.storyboard_generator.generate_prompts(
                storyboard,
                self.prompt_generator
            )
            
            # Step 4: 调用API生成视频
            print("正在调用Wan 2.7 API生成视频...")
            video_results = []
            image_results = []
            
            for scene in storyboard.scenes:
                if scene.prompt:
                    print(f"  生成场景{scene.number}: {scene.name}")
                    
                    # 文生视频
                    result = self.wanx_client.text_to_video(
                        prompt=scene.prompt,
                        duration=scene.duration
                    )
                    
                    if result.get("success"):
                        video_results.append({
                            "scene": scene.number,
                            "task_id": result.get("task_id"),
                            "status": result.get("status")
                        })
                    else:
                        print(f"  场景{scene.number}生成失败: {result.get('error')}")
            
            # Step 5: 生成配套图片素材
            print("生成配套教学图片...")
            image_prompt = self.prompt_generator.generate_image_prompt(config)
            image_result = self.wanx_client.text_to_image(
                prompt=image_prompt,
                resolution="1024x1024"
            )
            
            if image_result.get("success"):
                image_results.append({
                    "type": "cover",
                    "task_id": image_result.get("task_id")
                })
            
            # Step 6: 生成教学笔记
            teaching_notes = self._generate_teaching_notes(
                subject, topic, grade, storyboard
            )
            
            # 保存结果
            self._save_results(storyboard, video_results, image_results)
            
            return LessonVideoResult(
                success=True,
                storyboard=storyboard.to_dict(),
                video_urls=[v["task_id"] for v in video_results],
                image_urls=[i["task_id"] for i in image_results],
                prompts=[s.prompt for s in storyboard.scenes if s.prompt],
                teaching_notes=teaching_notes
            )
            
        except Exception as e:
            return LessonVideoResult(
                success=False,
                storyboard=None,
                video_urls=[],
                image_urls=[],
                prompts=[],
                teaching_notes="",
                error=str(e)
            )
    
    def generate_quick_image(
        self,
        subject: str,
        topic: str,
        grade: str = "高中",
        style: str = "知识动画风"
    ) -> Dict:
        """
        快速生成教学图片
        
        Args:
            subject: 学科
            topic: 知识点
            grade: 年级
            style: 风格
            
        Returns:
            生成结果
        """
        config = TeachingPromptConfig(
            subject=self._get_subject_enum(subject),
            topic=topic,
            grade=grade,
            style=self._get_style_enum(style),
            duration=5,
            include_labels=True
        )
        
        prompt = self.prompt_generator.generate_image_prompt(config)
        negative = self.prompt_generator.generate_negative_prompt(config)
        
        return self.wanx_client.text_to_image(
            prompt=prompt,
            negative_prompt=negative,
            resolution="1024x1024"
        )
    
    def generate_storyboard_only(
        self,
        subject: str,
        topic: str,
        grade: str = "高中",
        duration: int = 30,
        template: str = "概念讲解"
    ) -> Dict:
        """
        仅生成故事板（不调用API）
        
        Args:
            subject: 学科
            topic: 知识点
            grade: 年级
            duration: 总时长
            template: 模板类型
            
        Returns:
            故事板内容
        """
        storyboard = self.storyboard_generator.generate(
            topic=topic,
            subject=subject,
            grade=grade,
            template=template,
            total_duration=duration
        )
        
        # 生成提示词
        storyboard = self.storyboard_generator.generate_prompts(
            storyboard,
            self.prompt_generator
        )
        
        # 导出脚本
        script = self.storyboard_generator.export_to_script(storyboard)
        
        return {
            "storyboard": storyboard.to_dict(),
            "script": script
        }
    
    def _get_subject_enum(self, subject: str) -> Subject:
        """将字符串转换为Subject枚举"""
        mapping = {
            "生物": Subject.BIOLOGY,
            "物理": Subject.PHYSICS,
            "化学": Subject.CHEMISTRY,
            "历史": Subject.HISTORY,
            "地理": Subject.GEOGRAPHY,
            "语文": Subject.LITERATURE,
            "数学": Subject.MATH,
            "通用": Subject.GENERAL
        }
        return mapping.get(subject, Subject.GENERAL)
    
    def _get_style_enum(self, style: str) -> TeachingStyle:
        """将字符串转换为TeachingStyle枚举"""
        mapping = {
            "知识动画风": TeachingStyle.ANIMATION,
            "科幻科技风": TeachingStyle.TECH_SCI_FI,
            "历史复古风": TeachingStyle.HISTORICAL,
            "自然写实风": TeachingStyle.NATURAL,
            "简约线条风": TeachingStyle.MINIMALIST,
            "多彩插画风": TeachingStyle.COLORFUL
        }
        return mapping.get(style, TeachingStyle.ANIMATION)
    
    def _generate_teaching_notes(
        self,
        subject: str,
        topic: str,
        grade: str,
        storyboard
    ) -> str:
        """生成教学笔记"""
        notes = f"""# 《{topic}》教学视频制作说明

## 基本信息
- **学科**: {subject}
- **知识点**: {topic}
- **年级**: {grade}
- **总时长**: {storyboard.total_duration}秒
- **场景数量**: {len(storyboard.scenes)}

## 分镜概览
"""
        for scene in storyboard.scenes:
            notes += f"""
### 场景{scene.number}: {scene.name}（{scene.duration}秒）
- **教学重点**: {scene.teaching_point}
- **视觉元素**: {', '.join(scene.visual_elements)}
- **动画效果**: {scene.animation_notes}

"""

        notes += """
## 使用建议

1. **课前准备**: 提前测试视频播放，确保画面清晰
2. **课堂节奏**: 根据讲解进度控制视频播放
3. **互动结合**: 在视频播放后进行提问互动
4. **课后复习**: 可将视频分享给学生用于复习

## 注意事项

- 确保教室投影设备支持MP4格式
- 建议音量适中，配合讲解
- 如需暂停讲解，可使用视频播放器的暂停功能
"""
        return notes
    
    def _save_results(self, storyboard, video_results, image_results):
        """保存生成结果"""
        timestamp = Path().stat().st_ctime if False else "output"
        
        # 保存故事板
        storyboard.save_to_file(
            self.workspace / f"{subject}_{topic}_storyboard.json"
        )
        
        # 保存元数据
        metadata = {
            "storyboard": storyboard.to_dict(),
            "video_tasks": video_results,
            "image_tasks": image_results,
            "generated_at": str(Path().stat().st_ctime)
        }
        
        with open(
            self.workspace / f"{topic}_metadata.json",
            'w',
            encoding='utf-8'
        ) as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)


def main():
    """命令行示例"""
    import argparse
    
    parser = argparse.ArgumentParser(description="万相教学助手")
    parser.add_argument("--subject", required=True, help="学科")
    parser.add_argument("--topic", required=True, help="知识点")
    parser.add_argument("--grade", default="高中", help="年级")
    parser.add_argument("--style", default="知识动画风", help="风格")
    parser.add_argument("--duration", type=int, default=30, help="时长(秒)")
    parser.add_argument("--mode", default="full", choices=["full", "storyboard", "image"], 
                        help="生成模式")
    
    args = parser.parse_args()
    
    # 初始化助手
    assistant = WanxTeachingAssistant()
    
    if args.mode == "storyboard":
        # 仅生成故事板
        result = assistant.generate_storyboard_only(
            subject=args.subject,
            topic=args.topic,
            grade=args.grade,
            duration=args.duration
        )
        print(result["script"])
        
    elif args.mode == "image":
        # 快速生成图片
        result = assistant.generate_quick_image(
            subject=args.subject,
            topic=args.topic,
            grade=args.grade,
            style=args.style
        )
        print(f"图片生成任务: {result}")
        
    else:
        # 完整流程
        result = assistant.generate_lesson_video(
            subject=args.subject,
            topic=args.topic,
            grade=args.grade,
            style=args.style,
            duration=args.duration
        )
        print(f"生成结果: {result}")


if __name__ == "__main__":
    main()
