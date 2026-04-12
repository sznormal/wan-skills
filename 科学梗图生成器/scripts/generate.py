#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
科学梗图生成器 - 核心脚本
把科学知识变成爆笑梗图，寓教于乐
"""

import os
import json
import time
import random
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# ============ 配置 ============
DEFAULT_OUTPUT_DIR = os.getenv("MEME_OUTPUT_DIR", "./science_memes")
WAN_API_KEY = os.getenv("WAN_API_KEY", "")
WAN_BASE_URL = os.getenv("WAN_BASE_URL", "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation")


class MemeType(Enum):
    """梗图类型"""
    WHEN_YOU_UNDERSTAND = "当你终于理解时"      # 上下对比
    TEACHER_VS_ME = "老师眼中的我"              # 左右对比
    IDEAL_VS_REALITY = "理想vs现实"             # 左右对比
    SCIENTIST_SAYS = "科学家说vs我听到"         # 对话框
    SCHOLAR_VS_SLACKER = "学霸vs学渣"          # 人物对比
    SUBJECT_PERSONIFIED = "学科拟人化"          # 角色设计
    MICRO_WORLD = "微观世界的日常"              # 生活场景
    EXAM_STATUS = "考试状态"                    # 三连对比


class ScienceSubject(Enum):
    """科学学科"""
    PHYSICS = "物理"
    CHEMISTRY = "化学"
    BIOLOGY = "生物"
    MATH = "数学"


class MemeStyle(Enum):
    """梗图风格"""
    CARTOON = "cartoon"      # 卡通可爱风
    MANGA = "manga"          # 日漫夸张风
    EMOJI = "emoji"          # 表情包风
    REALISTIC = "realistic"  # 写实风


@dataclass
class MemeContent:
    """梗图内容"""
    meme_type: MemeType              # 梗图类型
    subject: ScienceSubject          # 学科
    concept: str                     # 科学概念
    panels: List[Dict]               # 分格内容
    knowledge_point: str             # 知识点
    share_text: str                  # 分享文案


@dataclass
class GeneratedMeme:
    """生成的梗图"""
    success: bool
    image_url: str                   # 图片URL
    local_path: str                  # 本地路径
    knowledge_point: str             # 知识点
    share_text: str                  # 分享文案
    message: str


# ============ 科学概念数据库 ============
SCIENCE_CONCEPTS = {
    ScienceSubject.PHYSICS: {
        "相对论": {
            "description": "时间和空间可以弯曲",
            "knowledge": "爱因斯坦相对论：时间膨胀、空间弯曲、质能方程E=mc²",
            "confused_state": "时间和空间是绝对的？",
            "understood_state": "原来时间和空间可以弯曲！引力是时空弯曲的表现"
        },
        "量子力学": {
            "description": "粒子可以同时存在于多个状态",
            "knowledge": "量子叠加态、量子纠缠、测不准原理",
            "confused_state": "粒子就是一个确定的东西吧？",
            "understood_state": "薛定谔的猫既是活的又是死的！观测决定状态"
        },
        "牛顿定律": {
            "description": "力是改变运动状态的原因",
            "knowledge": "牛顿三大定律：惯性定律、F=ma、作用力与反作用力",
            "confused_state": "力是什么？为什么物体会动？",
            "understood_state": "没有力就不会改变运动状态！F=ma太优雅了"
        },
        "电磁感应": {
            "description": "变化的磁场产生电场",
            "knowledge": "法拉第电磁感应定律、楞次定律",
            "confused_state": "电和磁有啥关系？",
            "understood_state": "变化的磁场能产生电流！发电机就是这个原理"
        },
        "热力学第二定律": {
            "description": "熵总是增加的",
            "knowledge": "熵增原理、不可逆过程、热机效率",
            "confused_state": "为什么热量不会自动从低温传到高温？",
            "understood_state": "宇宙的混乱度一直在增加！时间是有方向的"
        }
    },
    ScienceSubject.CHEMISTRY: {
        "化学键": {
            "description": "原子之间的连接方式",
            "knowledge": "离子键、共价键、金属键",
            "confused_state": "原子怎么连在一起的？",
            "understood_state": "电子云的重叠形成化学键！分子是有形状的"
        },
        "氧化还原": {
            "description": "电子的转移反应",
            "knowledge": "氧化剂、还原剂、电子得失",
            "confused_state": "为什么铁会生锈？",
            "understood_state": "失去电子=氧化，得到电子=还原！电子在跳舞"
        },
        "化学平衡": {
            "description": "正逆反应速率相等",
            "knowledge": "平衡常数、勒夏特列原理",
            "confused_state": "反应不是应该进行到底吗？",
            "understood_state": "反应会达到平衡！改变条件平衡会移动"
        },
        "元素周期律": {
            "description": "元素性质的周期性变化",
            "knowledge": "原子结构、电负性、原子半径",
            "confused_state": "这么多元素怎么记？",
            "understood_state": "有规律！同族元素性质相似，周期性变化"
        }
    },
    ScienceSubject.BIOLOGY: {
        "DNA复制": {
            "description": "遗传信息的传递",
            "knowledge": "半保留复制、碱基配对、DNA聚合酶",
            "confused_state": "DNA怎么复制自己？",
            "understood_state": "双螺旋解开，每条链作为模板！半保留复制"
        },
        "自然选择": {
            "description": "适者生存的进化机制",
            "knowledge": "变异、选择、适应、进化",
            "confused_state": "物种是怎么进化的？",
            "understood_state": "有利的变异被保留，不利的被淘汰！自然选择"
        },
        "光合作用": {
            "description": "植物制造有机物的过程",
            "knowledge": "光反应、暗反应、叶绿体",
            "confused_state": "植物怎么吃饭？",
            "understood_state": "光能转化为化学能！CO₂+H₂O→葡萄糖+O₂"
        },
        "细胞分裂": {
            "description": "细胞的繁殖方式",
            "knowledge": "有丝分裂、减数分裂、细胞周期",
            "confused_state": "一个细胞怎么变成两个？",
            "understood_state": "DNA复制后均分！精准的分裂过程"
        }
    },
    ScienceSubject.MATH: {
        "微积分": {
            "description": "研究变化率的数学工具",
            "knowledge": "导数、积分、极限",
            "confused_state": "无限小的变化是什么？",
            "understood_state": "导数是瞬时变化率！积分是求和的极限"
        },
        "概率论": {
            "description": "研究随机现象的数学",
            "knowledge": "概率、期望、方差、正态分布",
            "confused_state": "随机事件也能预测？",
            "understood_state": "大数定律！概率趋近于期望"
        },
        "线性代数": {
            "description": "研究向量空间的数学",
            "knowledge": "矩阵、向量、线性变换",
            "confused_state": "矩阵有什么用？",
            "understood_state": "矩阵是变换！特征值是变换的本质"
        }
    }
}


# ============ 梗图模板库 ============
MEME_TEMPLATES = {
    MemeType.WHEN_YOU_UNDERSTAND: {
        "name": "当你终于理解时",
        "layout": "vertical",  # 上下布局
        "panels": 2,
        "style_prompt": "上下两格对比图，表情包风格，卡通可爱，中文文字标注"
    },
    MemeType.TEACHER_VS_ME: {
        "name": "老师眼中的我",
        "layout": "horizontal",  # 左右布局
        "panels": 2,
        "style_prompt": "左右对比图，日漫风格，夸张表情，中文文字标注"
    },
    MemeType.IDEAL_VS_REALITY: {
        "name": "理想vs现实",
        "layout": "horizontal",
        "panels": 2,
        "style_prompt": "左右对比图，写实风格，对比强烈，中文文字标注"
    },
    MemeType.SCHOLAR_VS_SLACKER: {
        "name": "学霸vs学渣",
        "layout": "horizontal",
        "panels": 2,
        "style_prompt": "人物对比图，卡通风格，表情夸张，中文文字标注"
    },
    MemeType.EXAM_STATUS: {
        "name": "考试状态",
        "layout": "triple",  # 三连
        "panels": 3,
        "style_prompt": "三连对比图，表情包风格，情感递进，中文文字标注"
    },
    MemeType.SUBJECT_PERSONIFIED: {
        "name": "学科拟人化",
        "layout": "character",  # 角色设计
        "panels": 1,
        "style_prompt": "动漫角色设计，拟人化，个性鲜明，中文文字标注"
    },
    MemeType.MICRO_WORLD: {
        "name": "微观世界的日常",
        "layout": "scene",  # 场景
        "panels": 1,
        "style_prompt": "微观世界场景，粒子拟人化，可爱卡通，中文文字标注"
    }
}


# ============ 内容生成器 ============
class MemeContentGenerator:
    """梗图内容生成器"""
    
    # 文案模板
    CAPTION_TEMPLATES = {
        MemeType.WHEN_YOU_UNDERSTAND: {
            "top": "当你第一次听{concept}时",
            "bottom": "当你终于理解{concept}时"
        },
        MemeType.TEACHER_VS_ME: {
            "left": "{subject}老师眼中的我",
            "right": "我眼中的{subject}课"
        },
        MemeType.IDEAL_VS_REALITY: {
            "left": "理想中的{experiment}结果",
            "right": "实际的{experiment}结果"
        },
        MemeType.SCHOLAR_VS_SLACKER: {
            "left": "学霸做{concept}时",
            "right": "我做{concept}时"
        },
        MemeType.EXAM_STATUS: {
            "first": "考试前：稳了！",
            "second": "考试中：这是啥？",
            "third": "考试后：明年再来"
        }
    }
    
    # 学科拟人化设定
    SUBJECT_PERSONALITIES = {
        ScienceSubject.PHYSICS: {
            "name": "物理君",
            "personality": "高冷男神，话少但句句真理",
            "appearance": "戴眼镜，穿白大褂，手持公式",
            "catchphrase": "万物皆有规律"
        },
        ScienceSubject.CHEMISTRY: {
            "name": "化学酱",
            "personality": "暴躁少女，一言不合就爆炸",
            "appearance": "彩色头发，手持试管，表情生动",
            "catchphrase": "反应了！反应了！"
        },
        ScienceSubject.BIOLOGY: {
            "name": "生物学姐",
            "personality": "温柔学姐，关心生命万物",
            "appearance": "绿色系服装，手持显微镜",
            "catchphrase": "生命真奇妙"
        },
        ScienceSubject.MATH: {
            "name": "数学大师",
            "personality": "神秘智者，只有少数人能懂",
            "appearance": "深邃眼神，身边漂浮符号",
            "catchphrase": "一切都是数"
        }
    }
    
    def generate(self, meme_type: MemeType, subject: ScienceSubject, 
                 concept: str) -> MemeContent:
        """生成梗图内容"""
        concept_data = SCIENCE_CONCEPTS.get(subject, {}).get(concept, {})
        
        panels = self._generate_panels(meme_type, subject, concept, concept_data)
        knowledge_point = concept_data.get("knowledge", f"{subject.value}：{concept}")
        share_text = self._generate_share_text(meme_type, subject, concept)
        
        return MemeContent(
            meme_type=meme_type,
            subject=subject,
            concept=concept,
            panels=panels,
            knowledge_point=knowledge_point,
            share_text=share_text
        )
    
    def _generate_panels(self, meme_type: MemeType, subject: ScienceSubject,
                         concept: str, concept_data: Dict) -> List[Dict]:
        """生成分格内容"""
        panels = []
        
        if meme_type == MemeType.WHEN_YOU_UNDERSTAND:
            panels = [
                {
                    "caption": f"当你第一次听{concept}时",
                    "emotion": "困惑",
                    "description": concept_data.get("confused_state", "这是什么？"),
                    "scene": "学生面对课本，表情迷茫，头顶问号"
                },
                {
                    "caption": f"当你终于理解{concept}时",
                    "emotion": "顿悟",
                    "description": concept_data.get("understood_state", "原来如此！"),
                    "scene": "学生恍然大悟，眼睛发光，头顶灯泡"
                }
            ]
        
        elif meme_type == MemeType.TEACHER_VS_ME:
            panels = [
                {
                    "caption": f"{subject.value}老师眼中的我",
                    "emotion": "专注",
                    "description": "认真听讲的好学生",
                    "scene": "学生坐姿端正，认真记笔记，眼神专注"
                },
                {
                    "caption": f"我眼中的{subject.value}课",
                    "emotion": "放空",
                    "description": "在想中午吃什么",
                    "scene": "学生发呆，脑中浮现美食，眼神空洞"
                }
            ]
        
        elif meme_type == MemeType.IDEAL_VS_REALITY:
            panels = [
                {
                    "caption": "理想的实验结果",
                    "emotion": "完美",
                    "description": "数据整齐，曲线优美",
                    "scene": "完美的实验曲线，数据点精确落在曲线上"
                },
                {
                    "caption": "实际的实验结果",
                    "emotion": "崩溃",
                    "description": "数据乱七八糟",
                    "scene": "杂乱的数据点，曲线歪七扭八"
                }
            ]
        
        elif meme_type == MemeType.SCHOLAR_VS_SLACKER:
            panels = [
                {
                    "caption": f"学霸做{concept}时",
                    "emotion": "轻松",
                    "description": "一眼看出答案",
                    "scene": "学霸自信微笑，笔尖飞快移动"
                },
                {
                    "caption": f"我做{concept}时",
                    "emotion": "崩溃",
                    "description": "完全看不懂",
                    "scene": "学生抓耳挠腮，脑中一片空白"
                }
            ]
        
        elif meme_type == MemeType.EXAM_STATUS:
            panels = [
                {
                    "caption": "考试前",
                    "emotion": "自信",
                    "description": "稳了！",
                    "scene": "学生自信满满，比V手势"
                },
                {
                    "caption": "考试中",
                    "emotion": "崩溃",
                    "description": "这是啥？",
                    "scene": "学生看着试卷，表情崩溃"
                },
                {
                    "caption": "考试后",
                    "emotion": "躺平",
                    "description": "明年再来",
                    "scene": "学生躺平，生无可恋"
                }
            ]
        
        elif meme_type == MemeType.SUBJECT_PERSONIFIED:
            personality = self.SUBJECT_PERSONALITIES.get(subject, {})
            panels = [
                {
                    "caption": f"{subject.value}拟人化",
                    "emotion": personality.get("personality", ""),
                    "description": personality.get("catchphrase", ""),
                    "scene": f"{personality.get('name', subject.value)}，{personality.get('appearance', '')}"
                }
            ]
        
        elif meme_type == MemeType.MICRO_WORLD:
            panels = [
                {
                    "caption": f"{concept}的微观世界",
                    "emotion": "活泼",
                    "description": "粒子们的日常",
                    "scene": f"可爱的{concept}粒子在互动，表情生动，卡通风格"
                }
            ]
        
        return panels
    
    def _generate_share_text(self, meme_type: MemeType, subject: ScienceSubject,
                              concept: str) -> str:
        """生成分享文案"""
        templates = [
            f"当你终于理解{concept}时... 😂 #科学梗图 #{subject.value}",
            f"{subject.value}老师的痛谁懂？🤣 #学习日常 #{subject.value}",
            f"理想vs现实，做实验太难了！😭 #实验日常 #科研",
            f"学霸和我之间隔着整个银河系... 🌌 #学习 #{subject.value}",
            f"考试三连：自信→崩溃→躺平 💀 #考试 #{subject.value}"
        ]
        return random.choice(templates)


# ============ 图像生成器 ============
class ImageGenerator:
    """调用Wan API生成图像"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or WAN_API_KEY
        
        if not self.api_key:
            raise ValueError("请设置WAN_API_KEY环境变量")
    
    def generate_meme(self, content: MemeContent, style: MemeStyle = MemeStyle.CARTOON) -> str:
        """生成梗图"""
        prompt = self._build_prompt(content, style)
        return self._call_api(prompt)
    
    def _build_prompt(self, content: MemeContent, style: MemeStyle) -> str:
        """构建提示词"""
        template = MEME_TEMPLATES.get(content.meme_type, {})
        style_prompt = template.get("style_prompt", "")
        
        # 根据布局构建提示词
        layout = template.get("layout", "")
        panels = content.panels
        
        if layout == "vertical":
            prompt = f"""
            上下两格对比图，{style_prompt}：
            上格：{panels[0]['scene']}，表情{panels[0]['emotion']}
            文字标注：" {panels[0]['caption']} "
            下格：{panels[1]['scene']}，表情{panels[1]['emotion']}
            文字标注：" {panels[1]['caption']} "
            科学主题：{content.subject.value} - {content.concept}
            """
        
        elif layout == "horizontal":
            prompt = f"""
            左右对比图，{style_prompt}：
            左格：{panels[0]['scene']}，表情{panels[0]['emotion']}
            文字标注：" {panels[0]['caption']} "
            右格：{panels[1]['scene']}，表情{panels[1]['emotion']}
            文字标注：" {panels[1]['caption']} "
            科学主题：{content.subject.value} - {content.concept}
            """
        
        elif layout == "triple":
            prompt = f"""
            三连对比图，{style_prompt}：
            第一格：{panels[0]['scene']}，表情{panels[0]['emotion']}
            文字标注：" {panels[0]['caption']} "
            第二格：{panels[1]['scene']}，表情{panels[1]['emotion']}
            文字标注：" {panels[1]['caption']} "
            第三格：{panels[2]['scene']}，表情{panels[2]['emotion']}
            文字标注：" {panels[2]['caption']} "
            科学主题：{content.subject.value} - {content.concept}
            """
        
        elif layout == "character":
            prompt = f"""
            动漫角色设计，{style_prompt}：
            角色：{panels[0]['caption']}
            外观：{panels[0]['scene']}
            性格：{panels[0]['emotion']}
            口头禅："{panels[0]['description']}"
            风格：可爱、个性鲜明
            """
        
        else:
            prompt = f"""
            科学梗图，{style_prompt}：
            场景：{panels[0]['scene']}
            文字标注：" {panels[0]['caption']} "
            科学主题：{content.subject.value} - {content.concept}
            """
        
        return prompt.strip()
    
    def _call_api(self, prompt: str) -> str:
        """调用Wan API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "wan2.7-image-pro",
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": [{"text": prompt}]
                    }
                ]
            },
            "parameters": {
                "size": "1K",
                "n": 1
            }
        }
        
        try:
            response = requests.post(WAN_BASE_URL, headers=headers, json=payload, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                if "output" in result and "results" in result["output"]:
                    return result["output"]["results"][0].get("url", "")
            
            return ""
        except Exception as e:
            print(f"图像生成失败: {e}")
            return ""


# ============ 主生成器 ============
class ScienceMemeGenerator:
    """科学梗图生成器主类"""
    
    def __init__(self, api_key: str = None, output_dir: str = None):
        self.api_key = api_key or WAN_API_KEY
        self.output_dir = Path(output_dir or DEFAULT_OUTPUT_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.content_generator = MemeContentGenerator()
        self.image_generator = ImageGenerator(self.api_key) if self.api_key else None
    
    def generate(self, concept: str, meme_type: str = None, 
                 subject: str = None, style: str = "cartoon") -> GeneratedMeme:
        """生成科学梗图"""
        # 识别学科和概念
        detected_subject, detected_concept = self._detect_concept(concept, subject)
        
        if not detected_concept:
            return GeneratedMeme(
                success=False,
                image_url="",
                local_path="",
                knowledge_point="",
                share_text="",
                message=f"未找到科学概念：{concept}，请尝试：相对论、量子力学、DNA复制等"
            )
        
        # 选择梗图类型
        if meme_type:
            meme_type_enum = MemeType(meme_type)
        else:
            meme_type_enum = MemeType.WHEN_YOU_UNDERSTAND
        
        # 生成内容
        content = self.content_generator.generate(
            meme_type_enum, detected_subject, detected_concept
        )
        
        # 生成图像
        image_url = ""
        if self.image_generator:
            style_enum = MemeStyle(style)
            image_url = self.image_generator.generate_meme(content, style_enum)
        
        return GeneratedMeme(
            success=True,
            image_url=image_url,
            local_path="",
            knowledge_point=content.knowledge_point,
            share_text=content.share_text,
            message=f"成功生成{detected_concept}的梗图！"
        )
    
    def _detect_concept(self, concept: str, subject_hint: str = None) -> Tuple[ScienceSubject, str]:
        """识别科学概念"""
        # 如果指定了学科
        if subject_hint:
            for subject in ScienceSubject:
                if subject_hint in subject.value:
                    concepts = SCIENCE_CONCEPTS.get(subject, {})
                    if concept in concepts:
                        return subject, concept
        
        # 遍历所有学科查找
        for subject, concepts in SCIENCE_CONCEPTS.items():
            if concept in concepts:
                return subject, concept
        
        return None, None
    
    def list_concepts(self, subject: str = None) -> List[str]:
        """列出可用概念"""
        if subject:
            for s in ScienceSubject:
                if subject in s.value:
                    return list(SCIENCE_CONCEPTS.get(s, {}).keys())
        
        all_concepts = []
        for concepts in SCIENCE_CONCEPTS.values():
            all_concepts.extend(concepts.keys())
        return all_concepts
    
    def list_meme_types(self) -> List[str]:
        """列出梗图类型"""
        return [t.value for t in MemeType]


# ============ CLI入口 ============
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="科学梗图生成器")
    parser.add_argument("--concept", help="科学概念")
    parser.add_argument("--type", choices=[t.value for t in MemeType], 
                       help="梗图类型")
    parser.add_argument("--subject", help="学科")
    parser.add_argument("--style", choices=["cartoon", "manga", "emoji", "realistic"],
                       default="cartoon", help="风格")
    parser.add_argument("--list-concepts", action="store_true", help="列出所有概念")
    parser.add_argument("--list-types", action="store_true", help="列出梗图类型")
    parser.add_argument("--output", default=DEFAULT_OUTPUT_DIR, help="输出目录")
    
    args = parser.parse_args()
    
    generator = ScienceMemeGenerator(output_dir=args.output)
    
    if args.list_concepts:
        print("可用科学概念：")
        for concept in generator.list_concepts(args.subject):
            print(f"  - {concept}")
        return
    
    if args.list_types:
        print("可用梗图类型：")
        for meme_type in generator.list_meme_types():
            print(f"  - {meme_type}")
        return
    
    if not args.concept:
        print("请指定 --concept 参数")
        return
    
    result = generator.generate(
        concept=args.concept,
        meme_type=args.type,
        subject=args.subject,
        style=args.style
    )
    
    print(json.dumps({
        "success": result.success,
        "message": result.message,
        "image_url": result.image_url,
        "knowledge_point": result.knowledge_point,
        "share_text": result.share_text
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
