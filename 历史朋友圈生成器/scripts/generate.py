#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
历史朋友圈生成器 - 核心脚本
让历史人物"活起来"，用朋友圈的方式学历史
"""

import os
import json
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

# ============ 配置 ============
DEFAULT_OUTPUT_DIR = os.getenv("HISTORY_OUTPUT_DIR", "./history_moments")
WAN_API_KEY = os.getenv("WAN_API_KEY", "")
WAN_BASE_URL = os.getenv("WAN_BASE_URL", "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation")


class Dynasty(Enum):
    """朝代"""
    PRE_QIN = "先秦"
    QIN_HAN = "秦汉"
    THREE_KINGDOMS = "三国"
    TANG = "唐朝"
    SONG = "宋朝"
    MING_QING = "明清"
    MODERN = "近现代"


class PersonType(Enum):
    """人物类型"""
    EMPEROR = "帝王"
    POET = "诗人"
    GENERAL = "将军"
    SCHOLAR = "文人"
    POLITICIAN = "政治家"
    PHILOSOPHER = "思想家"
    BEAUTY = "才女"
    REFORMER = "改革家"


@dataclass
class HistoricalPerson:
    """历史人物"""
    name: str                    # 姓名
    dynasty: Dynasty             # 朝代
    person_type: PersonType      # 类型
    personality: str             # 性格特点
    famous_quotes: List[str]     # 名言
    friends: List[str]           # 好友/同僚
    rivals: List[str]            # 对手/敌人


@dataclass
class MomentContent:
    """朋友圈内容"""
    author: HistoricalPerson     # 发布者
    text: str                    # 文案
    images: List[str]            # 配图描述
    location: str                # 地点
    time_desc: str               # 时间描述
    likes: List[str]             # 点赞列表
    comments: List[Dict]         # 评论列表


@dataclass
class GeneratedMoment:
    """生成的朋友圈"""
    success: bool
    avatar_url: str              # 头像URL
    image_urls: List[str]        # 配图URL
    moment_screenshot: str       # 朋友圈截图路径
    knowledge_points: List[str]  # 知识点
    message: str


# ============ 历史人物数据库 ============
HISTORICAL_FIGURES = {
    # 唐朝诗人
    "李白": HistoricalPerson(
        name="李白",
        dynasty=Dynasty.TANG,
        person_type=PersonType.POET,
        personality="豪放不羁、浪漫洒脱、爱喝酒、诗仙",
        famous_quotes=["天生我材必有用", "长风破浪会有时", "举杯邀明月"],
        friends=["杜甫", "王维", "孟浩然", "高适"],
        rivals=[]
    ),
    "杜甫": HistoricalPerson(
        name="杜甫",
        dynasty=Dynasty.TANG,
        person_type=PersonType.POET,
        personality="忧国忧民、沉郁顿挫、诗圣",
        famous_quotes=["安得广厦千万间", "国破山河在", "会当凌绝顶"],
        friends=["李白", "高适"],
        rivals=[]
    ),
    "王维": HistoricalPerson(
        name="王维",
        dynasty=Dynasty.TANG,
        person_type=PersonType.POET,
        personality="清静淡泊、诗中有画、诗佛",
        famous_quotes=["行到水穷处", "空山新雨后", "红豆生南国"],
        friends=["李白", "杜甫", "孟浩然"],
        rivals=[]
    ),
    
    # 三国人物
    "曹操": HistoricalPerson(
        name="曹操",
        dynasty=Dynasty.THREE_KINGDOMS,
        person_type=PersonType.POLITICIAN,
        personality="奸雄、多疑、雄才大略、爱才",
        famous_quotes=["宁教我负天下人", "对酒当歌", "老骥伏枥"],
        friends=["郭嘉", "荀彧", "夏侯惇"],
        rivals=["刘备", "孙权", "袁绍"]
    ),
    "刘备": HistoricalPerson(
        name="刘备",
        dynasty=Dynasty.THREE_KINGDOMS,
        person_type=PersonType.POLITICIAN,
        personality="仁德、善用人、以德服人",
        famous_quotes=["勿以善小而不为", "汉室宗亲"],
        friends=["关羽", "张飞", "诸葛亮", "赵云"],
        rivals=["曹操"]
    ),
    "诸葛亮": HistoricalPerson(
        name="诸葛亮",
        dynasty=Dynasty.THREE_KINGDOMS,
        person_type=PersonType.SCHOLAR,
        personality="足智多谋、鞠躬尽瘁、忠臣",
        famous_quotes=["鞠躬尽瘁死而后已", "非淡泊无以明志"],
        friends=["刘备", "周瑜"],
        rivals=["司马懿"]
    ),
    
    # 秦汉
    "秦始皇": HistoricalPerson(
        name="秦始皇",
        dynasty=Dynasty.QIN_HAN,
        person_type=PersonType.EMPEROR,
        personality="雄才大略、暴虐、千古一帝",
        famous_quotes=["书同文车同轨", "朕即天下"],
        friends=["李斯"],
        rivals=["六国贵族"]
    ),
    
    # 宋朝
    "苏轼": HistoricalPerson(
        name="苏轼",
        dynasty=Dynasty.SONG,
        person_type=PersonType.POET,
        personality="乐观豁达、美食家、全才",
        famous_quotes=["大江东去", "但愿人长久", "一蓑烟雨任平生"],
        friends=["黄庭坚", "佛印"],
        rivals=["王安石（政见不合）"]
    ),
    
    # 明清
    "李清照": HistoricalPerson(
        name="李清照",
        dynasty=Dynasty.MING_QING,
        person_type=PersonType.BEAUTY,
        personality="才情横溢、忧国忧民、易安居士",
        famous_quotes=["帘卷西风", "此情无计可消除", "至今思项羽"],
        friends=["赵明诚"],
        rivals=[]
    ),
}


# ============ 内容生成器 ============
class MomentGenerator:
    """朋友圈内容生成器"""
    
    # 文案模板
    TEXT_TEMPLATES = {
        PersonType.POET: {
            "日常": [
                "今天{活动}，忽有所感，提笔写下{诗名}，各位品鉴一下 ✍️",
                "{地点}的风光真是绝了，灵感来了挡都挡不住，{诗名}问世！",
                "酒后作诗，{诗名}，哈哈哈，好诗好诗！🍶"
            ],
            "感慨": [
                "{感慨内容}，人生如此，夫复何求？",
                "今日{事件}，心中百感交集，赋诗一首以记之"
            ]
        },
        PersonType.EMPEROR: {
            "功绩": [
                "{功绩内容}，朕心甚慰！{hashtag}",
                "大秦（唐/汉）万岁！今天完成了{大事}，历史会记住这一刻 👑"
            ],
            "日常": [
                "今日{活动}，{评价}",
                "{政策}今日实施，期待国富民强 💪"
            ]
        },
        PersonType.POLITICIAN: {
            "政治": [
                "{政治内容}，天下大势，合久必分分久必合",
                "今日{事件}，{感悟}"
            ],
            "招揽": [
                "{人才}果然名不虚传，得此人如虎添翼！",
                "天下英雄，唯{对手}与我耳"
            ]
        },
        PersonType.GENERAL: {
            "战争": [
                "今日{战役}，{战果}！将士们辛苦了！⚔️",
                "虽{困境}，但{信念}，必胜！"
            ],
            "凯旋": [
                "凯旋归来！{战利品}，不虚此行！",
                "{战役}大捷，感谢将士们的浴血奋战！"
            ]
        },
        PersonType.BEAUTY: {
            "日常": [
                "{日常内容}，{感慨}",
                "{季节}已至，{景物}触景生情"
            ],
            "怀念": [
                "{怀念对象}，{怀念内容}",
                "往事如烟，{感慨}"
            ]
        }
    }
    
    # 评论模板
    COMMENT_TEMPLATES = {
        "好友": [
            "兄台{评价}！",
            "佩服佩服，{赞美内容}",
            "哈哈，{调侃内容}"
        ],
        "对手": [
            "呵呵，{阴阳怪气}",
            "哼，{不屑}",
            "{挑衅内容}"
        ],
        "下属": [
            "{称呼}英明！",
            "{赞美}，{马屁}",
            "{表态}"
        ]
    }
    
    def generate_moment(self, person: HistoricalPerson, event: str = None) -> MomentContent:
        """生成朋友圈内容"""
        import random
        
        # 根据人物类型选择文案模板
        templates = self.TEXT_TEMPLATES.get(person.person_type, self.TEXT_TEMPLATES[PersonType.POET])
        category = random.choice(list(templates.keys()))
        text_template = random.choice(templates[category])
        
        # 填充文案
        text = self._fill_template(text_template, person, event)
        
        # 生成配图描述
        images = self._generate_image_prompts(person, event)
        
        # 生成评论
        comments = self._generate_comments(person)
        
        # 点赞列表
        likes = person.friends[:3] if person.friends else []
        
        return MomentContent(
            author=person,
            text=text,
            images=images,
            location=self._get_location(person),
            time_desc=self._get_time_desc(person),
            likes=likes,
            comments=comments
        )
    
    def _fill_template(self, template: str, person: HistoricalPerson, event: str = None) -> str:
        """填充文案模板"""
        # 简单的模板填充逻辑
        text = template
        
        if "{活动}" in text:
            activities = ["登高望远", "游山玩水", "饮酒作诗", "会友论道"]
            text = text.replace("{活动}", activities[0])
        
        if "{诗名}" in text:
            poems = ["一首小诗", "一首绝句", "新作一首"]
            text = text.replace("{诗名}", poems[0])
        
        if "{地点}" in text:
            text = text.replace("{地点}", "长安")
        
        if "{hashtag}" in text:
            text = text.replace("{hashtag}", "#千古一帝")
        
        if "{功绩内容}" in text:
            text = text.replace("{功绩内容}", "六国统一")
        
        if "{大事}" in text:
            text = text.replace("{大事}", "统一大业")
        
        # 添加人物名言
        if person.famous_quotes:
            text += f"\n\n📝 {random.choice(person.famous_quotes)}"
        
        return text
    
    def _generate_image_prompts(self, person: HistoricalPerson, event: str = None) -> List[str]:
        """生成配图描述"""
        prompts = []
        
        dynasty_style = {
            Dynasty.TANG: "唐代风格，繁华盛世，色彩明丽",
            Dynasty.SONG: "宋代风格，雅致清幽，文人气息",
            Dynasty.THREE_KINGDOMS: "三国时期风格，战争场面或英雄气概",
            Dynasty.QIN_HAN: "秦汉风格，恢弘大气，古朴厚重",
            Dynasty.MING_QING: "明清风格，精致典雅"
        }
        
        style = dynasty_style.get(person.dynasty, "中国古典风格")
        
        # 根据人物类型生成场景
        if person.person_type == PersonType.POET:
            prompts.append(f"{person.name}在月下独酌的场景，{style}，水墨画风格")
        elif person.person_type == PersonType.EMPEROR:
            prompts.append(f"{person.name}站在宫殿之上俯瞰天下，{style}，气势恢宏")
        elif person.person_type == PersonType.POLITICIAN:
            prompts.append(f"{person.name}运筹帷幄的场景，{style}，智谋深远")
        elif person.person_type == PersonType.BEAUTY:
            prompts.append(f"{person.name}倚窗沉思的场景，{style}，婉约动人")
        
        return prompts
    
    def _generate_comments(self, person: HistoricalPerson) -> List[Dict]:
        """生成评论"""
        comments = []
        
        # 好友评论
        for friend in person.friends[:2]:
            comments.append({
                "author": friend,
                "content": f"兄台好文采！佩服佩服 👍",
                "type": "好友"
            })
        
        # 对手评论
        for rival in person.rivals[:1]:
            comments.append({
                "author": rival,
                "content": f"呵呵，有意思 😏",
                "type": "对手"
            })
        
        return comments
    
    def _get_location(self, person: HistoricalPerson) -> str:
        """获取地点"""
        locations = {
            Dynasty.TANG: "长安",
            Dynasty.SONG: "开封",
            Dynasty.THREE_KINGDOMS: "许都",
            Dynasty.QIN_HAN: "咸阳"
        }
        return locations.get(person.dynasty, "中原")
    
    def _get_time_desc(self, person: HistoricalPerson) -> str:
        """获取时间描述"""
        dynasty_years = {
            Dynasty.TANG: "贞观年间",
            Dynasty.SONG: "熙宁年间",
            Dynasty.THREE_KINGDOMS: "建安年间",
            Dynasty.QIN_HAN: "秦始皇统一六国后"
        }
        return dynasty_years.get(person.dynasty, "古代")


# ============ 图像生成器 ============
class ImageGenerator:
    """调用Wan API生成图像"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or WAN_API_KEY
        
        if not self.api_key:
            raise ValueError("请设置WAN_API_KEY环境变量")
    
    def generate_avatar(self, person: HistoricalPerson) -> str:
        """生成人物头像"""
        prompt = f"""
        中国古代人物头像，{person.name}，
        {person.dynasty.value}服饰风格，
        {person.personality}的气质，
        古典水墨画风格，
        正面肖像，背景简洁
        """
        
        return self._call_image_api(prompt.strip())
    
    def generate_scene(self, prompt: str) -> str:
        """生成场景图"""
        return self._call_image_api(prompt)
    
    def _call_image_api(self, prompt: str) -> str:
        """调用图像生成API"""
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
class HistoryMomentsGenerator:
    """历史朋友圈生成器主类"""
    
    def __init__(self, api_key: str = None, output_dir: str = None):
        self.api_key = api_key or WAN_API_KEY
        self.output_dir = Path(output_dir or DEFAULT_OUTPUT_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.moment_generator = MomentGenerator()
        self.image_generator = ImageGenerator(self.api_key) if self.api_key else None
    
    def generate(self, person_name: str, event: str = None) -> GeneratedMoment:
        """生成历史朋友圈"""
        # 1. 查找历史人物
        person = HISTORICAL_FIGURES.get(person_name)
        if not person:
            return GeneratedMoment(
                success=False,
                avatar_url="",
                image_urls=[],
                moment_screenshot="",
                knowledge_points=[],
                message=f"未找到历史人物：{person_name}，请尝试：李白、杜甫、曹操、秦始皇等"
            )
        
        # 2. 生成朋友圈内容
        moment = self.moment_generator.generate_moment(person, event)
        
        # 3. 生成图像（如果有API Key）
        avatar_url = ""
        image_urls = []
        
        if self.image_generator:
            avatar_url = self.image_generator.generate_avatar(person)
            for img_prompt in moment.images:
                img_url = self.image_generator.generate_scene(img_prompt)
                if img_url:
                    image_urls.append(img_url)
        
        # 4. 提取知识点
        knowledge_points = self._extract_knowledge(person, event)
        
        return GeneratedMoment(
            success=True,
            avatar_url=avatar_url,
            image_urls=image_urls,
            moment_screenshot="",  # 朋友圈截图需要前端渲染
            knowledge_points=knowledge_points,
            message=f"成功生成{person_name}的朋友圈！"
        )
    
    def _extract_knowledge(self, person: HistoricalPerson, event: str = None) -> List[str]:
        """提取知识点"""
        points = [
            f"【人物】{person.name}，{person.dynasty.value}{person.person_type.value}",
            f"【性格】{person.personality}",
            f"【名言】{', '.join(person.famous_quotes[:2])}"
        ]
        
        if person.friends:
            points.append(f"【好友/同僚】{', '.join(person.friends)}")
        
        if person.rivals:
            points.append(f"【对手/敌人】{', '.join(person.rivals)}")
        
        return points
    
    def list_available_figures(self) -> List[str]:
        """列出所有可用历史人物"""
        return list(HISTORICAL_FIGURES.keys())


# ============ CLI入口 ============
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="历史朋友圈生成器")
    parser.add_argument("--person", required=True, help="历史人物名称")
    parser.add_argument("--event", help="历史事件")
    parser.add_argument("--list", action="store_true", help="列出所有可用人物")
    parser.add_argument("--output", default=DEFAULT_OUTPUT_DIR, help="输出目录")
    
    args = parser.parse_args()
    
    if args.list:
        generator = HistoryMomentsGenerator(output_dir=args.output)
        print("可用历史人物：")
        for name in generator.list_available_figures():
            print(f"  - {name}")
        return
    
    generator = HistoryMomentsGenerator(output_dir=args.output)
    result = generator.generate(args.person, args.event)
    
    print(json.dumps({
        "success": result.success,
        "message": result.message,
        "knowledge_points": result.knowledge_points,
        "avatar_url": result.avatar_url,
        "image_urls": result.image_urls
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
