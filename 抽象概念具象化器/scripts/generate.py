#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抽象概念具象化器 - 核心生成脚本
Abstract Concept Visualizer - Core Generation Script

功能：将抽象技术概念转化为生活场景可视化图像
"""

import os
import sys
import json
import argparse
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

# ===== 概念映射数据库 =====

class ConceptCategory(Enum):
    """概念类别"""
    DATA_STRUCTURE = "数据结构"
    HARDWARE = "硬件接口"
    COMMUNICATION = "通信协议"
    CONTROL = "控制流程"
    ERROR = "错误类型"
    OS = "操作系统"
    ROS = "机器人系统"
    GENERAL = "通用概念"


@dataclass
class ConceptMapping:
    """概念映射"""
    concept: str
    category: ConceptCategory
    metaphor: str
    description: str
    prompt_template: str
    key_points: List[str]
    common_mistakes: List[str]


# 内置概念映射库
CONCEPT_DATABASE: Dict[str, ConceptMapping] = {
    # ===== 嵌入式系统概念 =====
    "指针": ConceptMapping(
        concept="指针",
        category=ConceptCategory.DATA_STRUCTURE,
        metaphor="导航APP",
        description="指针存储的是地址，就像导航APP告诉你目的地位置",
        prompt_template="A cartoon-style illustration showing a smartphone with GPS navigation app, the screen displays a map with a route leading to a destination marked with a memory address like '0x7FFFAA00', friendly and educational style, bright colors, clear labels in Chinese",
        key_points=[
            "指针存储的是地址，不是值",
            "解引用 = 到达目的地",
            "空指针 = 导航到虚无"
        ],
        common_mistakes=[
            "混淆指针和指针指向的值",
            "忘记初始化指针",
            "野指针访问"
        ]
    ),
    
    "GPIO": ConceptMapping(
        concept="GPIO",
        category=ConceptCategory.HARDWARE,
        metaphor="水龙头",
        description="GPIO控制输入输出，就像水龙头控制水流",
        prompt_template="A cartoon-style illustration comparing GPIO to a water faucet, showing a faucet that can be turned on/off to control water flow, with labels showing 'Input' and 'Output' modes, educational diagram style, clear and simple",
        key_points=[
            "GPIO可以配置为输入或输出",
            "输出模式控制外设",
            "输入模式读取传感器"
        ],
        common_mistakes=[
            "忘记配置引脚方向",
            "电平配置错误",
            "未考虑驱动能力"
        ]
    ),
    
    "中断": ConceptMapping(
        concept="中断",
        category=ConceptCategory.CONTROL,
        metaphor="门铃",
        description="中断打断当前工作，处理紧急事件后返回",
        prompt_template="A cartoon-style illustration showing a person working at a desk, suddenly interrupted by a doorbell ringing, the person pauses work to answer the door, then returns to continue working, storytelling comic style with clear sequence",
        key_points=[
            "中断有优先级",
            "ISR要简短快速",
            "保存和恢复上下文"
        ],
        common_mistakes=[
            "ISR中做耗时操作",
            "忘记清除中断标志",
            "中断嵌套处理不当"
        ]
    ),
    
    "I2C": ConceptMapping(
        concept="I2C",
        category=ConceptCategory.COMMUNICATION,
        metaphor="邮件系统",
        description="I2C是主从通信，像邮件系统一样按地址收发",
        prompt_template="A cartoon-style illustration showing I2C communication as a mail system, with a master device sending letters to multiple slave devices, each slave has a unique address mailbox, organized and clear communication diagram",
        key_points=[
            "两线制：SDA和SCL",
            "每个设备有唯一地址",
            "主从模式通信"
        ],
        common_mistakes=[
            "地址配置冲突",
            "上拉电阻缺失",
            "时钟速率不匹配"
        ]
    ),
    
    "SPI": ConceptMapping(
        concept="SPI",
        category=ConceptCategory.COMMUNICATION,
        metaphor="高速公路",
        description="SPI是高速并行通信，像多车道高速公路",
        prompt_template="A cartoon-style illustration comparing SPI to a multi-lane highway, with separate lanes for MOSI, MISO, SCK, and CS signals, cars traveling in parallel lanes representing data, fast and efficient communication visualization",
        key_points=[
            "四线制全双工",
            "高速传输",
            "支持多从机"
        ],
        common_mistakes=[
            "时钟极性配置错误",
            "片选管理不当",
            "速率过高导致错误"
        ]
    ),
    
    "UART": ConceptMapping(
        concept="UART",
        category=ConceptCategory.COMMUNICATION,
        metaphor="打电话",
        description="UART是点对点通信，像两个人打电话",
        prompt_template="A cartoon-style illustration showing UART communication as a telephone call between two people, with TX and RX lines shown as telephone wires, simple point-to-point communication, friendly educational style",
        key_points=[
            "异步通信",
            "需要约定波特率",
            "单对单通信"
        ],
        common_mistakes=[
            "波特率不匹配",
            "TX/RX接反",
            "缺少共地"
        ]
    ),
    
    "PWM": ConceptMapping(
        concept="PWM",
        category=ConceptCategory.CONTROL,
        metaphor="调光灯",
        description="PWM通过占空比控制功率，像调光灯旋钮",
        prompt_template="A cartoon-style illustration showing PWM as a dimmer switch controlling light bulb brightness, with different duty cycles shown as different brightness levels, clear percentage labels like 25%, 50%, 75%, 100%",
        key_points=[
            "占空比决定平均功率",
            "频率影响响应速度",
            "可用于电机控制、LED调光"
        ],
        common_mistakes=[
            "频率选择不当",
            "占空比计算错误",
            "负载驱动能力不足"
        ]
    ),
    
    "DMA": ConceptMapping(
        concept="DMA",
        category=ConceptCategory.HARDWARE,
        metaphor="快递员",
        description="DMA后台搬运数据，像快递员送货",
        prompt_template="A cartoon-style illustration showing DMA as a delivery person carrying boxes of data between memory locations while the CPU continues working on other tasks, showing parallel processing concept",
        key_points=[
            "解放CPU，提高效率",
            "需要配置源和目的地址",
            "传输完成有中断通知"
        ],
        common_mistakes=[
            "缓冲区地址对齐问题",
            "传输长度配置错误",
            "未等待传输完成"
        ]
    ),
    
    "栈溢出": ConceptMapping(
        concept="栈溢出",
        category=ConceptCategory.ERROR,
        metaphor="杯子溢水",
        description="栈空间不足，像杯子倒水溢出",
        prompt_template="A cartoon-style illustration showing stack overflow as a cup overflowing with water, the cup represents stack memory, water represents data being pushed onto the stack, clear warning visual",
        key_points=[
            "栈空间有限",
            "递归深度过大",
            "局部变量占用太多"
        ],
        common_mistakes=[
            "递归无终止条件",
            "大数组定义在栈上",
            "忘记栈大小限制"
        ]
    ),
    
    "内存泄漏": ConceptMapping(
        concept="内存泄漏",
        category=ConceptCategory.ERROR,
        metaphor="水池漏水",
        description="内存只申请不释放，像水池慢慢漏水",
        prompt_template="A cartoon-style illustration showing memory leak as a leaking water pool/tank, the water level slowly drops representing available memory decreasing over time, clear visual metaphor for resource depletion",
        key_points=[
            "申请后要释放",
            "指针丢失导致无法释放",
            "长期运行必须检查"
        ],
        common_mistakes=[
            "malloc后忘记free",
            "指针覆盖导致内存丢失",
            "异常分支未释放"
        ]
    ),
    
    "死锁": ConceptMapping(
        concept="死锁",
        category=ConceptCategory.ERROR,
        metaphor="互相等门",
        description="死锁是互相等待，像两个人互相等对方开门",
        prompt_template="A cartoon-style illustration showing deadlock as two people each standing at a door waiting for the other to open first, circular waiting situation, humorous but educational style",
        key_points=[
            "互斥资源竞争",
            "循环等待条件",
            "需要破坏死锁条件"
        ],
        common_mistakes=[
            "锁的获取顺序不一致",
            "忘记释放锁",
            "锁的粒度过大"
        ]
    ),
    
    "竞态条件": ConceptMapping(
        concept="竞态条件",
        category=ConceptCategory.ERROR,
        metaphor="同时抢座",
        description="竞态条件是时序冲突，像两个人同时抢一个座位",
        prompt_template="A cartoon-style illustration showing race condition as two people trying to sit in the same chair at the same time, causing confusion, timing conflict visualization",
        key_points=[
            "共享资源访问冲突",
            "需要同步机制",
            "时序敏感"
        ],
        common_mistakes=[
            "多线程无保护访问",
            "临界区未加锁",
            "假设执行顺序"
        ]
    ),
    
    # ===== 操作系统概念 =====
    "进程": ConceptMapping(
        concept="进程",
        category=ConceptCategory.OS,
        metaphor="工厂车间",
        description="进程是独立执行单元，像独立的工厂车间",
        prompt_template="A cartoon-style illustration showing processes as separate factory workshops, each workshop has its own resources and workers, independent but managed by a central supervisor",
        key_points=[
            "独立内存空间",
            "资源隔离",
            "进程间需要IPC通信"
        ],
        common_mistakes=[
            "直接访问其他进程内存",
            "进程创建过多",
            "IPC选择不当"
        ]
    ),
    
    "线程": ConceptMapping(
        concept="线程",
        category=ConceptCategory.OS,
        metaphor="车间工人",
        description="线程是并发执行单元，像车间里的多个工人",
        prompt_template="A cartoon-style illustration showing threads as workers in a factory, multiple workers share the same workshop (process) resources but work on different tasks concurrently",
        key_points=[
            "共享进程资源",
            "轻量级创建切换",
            "需要同步机制"
        ],
        common_mistakes=[
            "共享变量无保护",
            "线程数量过多",
            "死锁问题"
        ]
    ),
    
    "信号量": ConceptMapping(
        concept="信号量",
        category=ConceptCategory.OS,
        metaphor="通行证",
        description="信号量控制资源访问，像有限通行证",
        prompt_template="A cartoon-style illustration showing semaphore as limited tickets/passes being distributed, a counter showing available passes, people waiting when no passes available",
        key_points=[
            "计数器机制",
            "P操作申请V操作释放",
            "可用于同步和互斥"
        ],
        common_mistakes=[
            "P/V操作不配对",
            "信号量初始值错误",
            "死锁风险"
        ]
    ),
    
    # ===== ROS概念 =====
    "Node": ConceptMapping(
        concept="ROS Node",
        category=ConceptCategory.ROS,
        metaphor="工人",
        description="节点是执行单元，像工厂里的工人",
        prompt_template="A cartoon-style illustration showing ROS nodes as workers in a robot factory, each worker has a specific job and communicates with others through message boards",
        key_points=[
            "独立执行单元",
            "单一职责原则",
            "通过Topic/Service通信"
        ],
        common_mistakes=[
            "节点功能过于复杂",
            "忘记ros::spin()",
            "节点命名冲突"
        ]
    ),
    
    "Topic": ConceptMapping(
        concept="ROS Topic",
        category=ConceptCategory.ROS,
        metaphor="广播频道",
        description="Topic是消息广播，像电台频道",
        prompt_template="A cartoon-style illustration showing ROS Topic as a radio broadcast channel, one node broadcasts messages like a DJ, multiple nodes tune in to listen, one-way communication",
        key_points=[
            "异步通信",
            "一对多广播",
            "发布者-订阅者模式"
        ],
        common_mistakes=[
            "消息类型不匹配",
            "忘记advertise/subscribe",
            "QoS配置不当"
        ]
    ),
    
    "Service": ConceptMapping(
        concept="ROS Service",
        category=ConceptCategory.ROS,
        metaphor="服务窗口",
        description="Service是请求响应，像办事窗口",
        prompt_template="A cartoon-style illustration showing ROS Service as a service counter/window, a client node approaches with a request form, the server node processes and returns a result, synchronous communication",
        key_points=[
            "同步通信",
            "请求-响应模式",
            "适合一次性任务"
        ],
        common_mistakes=[
            "长时间阻塞",
            "忘记return response",
            "服务名称冲突"
        ]
    ),
}


# ===== 风格模板 =====

STYLE_TEMPLATES = {
    "cartoon": {
        "name": "卡通风格",
        "style_prompt": "cartoon style, friendly and cute, bright colors, simple shapes, educational illustration",
        "description": "适合课堂教学，亲切可爱"
    },
    "tech": {
        "name": "科技风格",
        "style_prompt": "modern tech style, blue and white color scheme, clean lines, professional diagram, futuristic",
        "description": "适合技术文档，专业现代"
    },
    "handdrawn": {
        "name": "手绘风格",
        "style_prompt": "hand-drawn style, sketch-like, pencil drawing, natural and approachable, notebook illustration",
        "description": "适合笔记课件，自然亲切"
    },
    "comic": {
        "name": "漫画风格",
        "style_prompt": "comic book style, dynamic action, speech bubbles, expressive characters, fun storytelling",
        "description": "适合社交传播，生动有趣"
    }
}


# ===== 核心类 =====

class ConceptVisualizer:
    """抽象概念具象化器"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("WAN_API_KEY")
        self.concept_db = CONCEPT_DATABASE
        self.style_templates = STYLE_TEMPLATES
    
    def get_concept(self, concept_name: str) -> Optional[ConceptMapping]:
        """获取概念映射"""
        return self.concept_db.get(concept_name)
    
    def list_concepts(self, category: ConceptCategory = None) -> List[str]:
        """列出所有概念"""
        if category:
            return [k for k, v in self.concept_db.items() if v.category == category]
        return list(self.concept_db.keys())
    
    def list_categories(self) -> List[str]:
        """列出所有类别"""
        return [c.value for c in ConceptCategory]
    
    def list_styles(self) -> Dict[str, str]:
        """列出所有风格"""
        return {k: v["name"] for k, v in self.style_templates.items()}
    
    def build_prompt(self, concept_name: str, style: str = "cartoon", 
                     custom_metaphor: str = None) -> str:
        """构建生成Prompt"""
        concept = self.get_concept(concept_name)
        
        if not concept:
            # 未知概念，使用通用模板
            return self._build_generic_prompt(concept_name, style)
        
        style_template = self.style_templates.get(style, self.style_templates["cartoon"])
        
        # 构建完整prompt
        prompt = f"{concept.prompt_template}, {style_template['style_prompt']}"
        
        # 如果有自定义比喻，调整prompt
        if custom_metaphor:
            prompt = f"A {style_template['style_prompt']} illustration showing {concept_name} as {custom_metaphor}, educational and clear"
        
        return prompt
    
    def _build_generic_prompt(self, concept_name: str, style: str) -> str:
        """构建通用概念Prompt"""
        style_template = self.style_templates.get(style, self.style_templates["cartoon"])
        return f"A {style_template['style_prompt']} illustration explaining the concept of {concept_name} in embedded systems or programming, using a real-life metaphor, educational and clear"
    
    def generate(self, concept_name: str, style: str = "cartoon",
                 custom_metaphor: str = None) -> Dict:
        """生成概念可视化"""
        concept = self.get_concept(concept_name)
        prompt = self.build_prompt(concept_name, style, custom_metaphor)
        
        result = {
            "concept": concept_name,
            "prompt": prompt,
            "style": self.style_templates.get(style, {}).get("name", style),
        }
        
        if concept:
            result.update({
                "metaphor": custom_metaphor or concept.metaphor,
                "description": concept.description,
                "key_points": concept.key_points,
                "common_mistakes": concept.common_mistakes,
                "category": concept.category.value
            })
        else:
            result.update({
                "metaphor": custom_metaphor or "待定义",
                "description": f"未找到概念'{concept_name}'的预设映射，使用通用模板",
                "key_points": [],
                "common_mistakes": [],
                "category": "通用概念"
            })
        
        # 调用Wan API（实际实现）
        # image_url = self._call_wan_api(prompt)
        # result["image_url"] = image_url
        
        # 模拟返回
        result["status"] = "prompt_generated"
        result["message"] = "Prompt已生成，可调用Wan API生成图像"
        
        return result
    
    def _call_wan_api(self, prompt: str) -> str:
        """调用Wan API生成图像"""
        # 实际API调用
        import requests
        
        url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "wan2.7-image-pro",
            "input": {"prompt": prompt},
            "parameters": {"style": "<auto>"}
        }
        
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        
        if result.get("output"):
            return result["output"]["results"][0]["url"]
        
        return None


# ===== 命令行接口 =====

def main():
    parser = argparse.ArgumentParser(
        description="抽象概念具象化器 - 将抽象概念转化为可视化图像"
    )
    
    # 主要操作
    parser.add_argument("--concept", "-c", type=str, help="要可视化的概念")
    parser.add_argument("--style", "-s", type=str, default="cartoon",
                       choices=["cartoon", "tech", "handdrawn", "comic"],
                       help="输出风格 (默认: cartoon)")
    parser.add_argument("--metaphor", "-m", type=str, help="自定义比喻")
    
    # 列表操作
    parser.add_argument("--list-concepts", action="store_true", help="列出所有概念")
    parser.add_argument("--list-categories", action="store_true", help="列出所有类别")
    parser.add_argument("--list-styles", action="store_true", help="列出所有风格")
    parser.add_argument("--category", type=str, help="按类别筛选概念")
    
    # 批量操作
    parser.add_argument("--batch", "-b", type=str, help="批量生成（指定概念列表文件）")
    parser.add_argument("--output", "-o", type=str, help="输出目录")
    
    args = parser.parse_args()
    
    visualizer = ConceptVisualizer()
    
    # 列表操作
    if args.list_concepts:
        category = None
        if args.category:
            try:
                category = ConceptCategory(args.category)
            except ValueError:
                print(f"无效类别: {args.category}")
                print(f"可用类别: {visualizer.list_categories()}")
                return
        
        concepts = visualizer.list_concepts(category)
        print(f"\n📋 概念列表 ({len(concepts)}个):")
        for c in concepts:
            info = visualizer.get_concept(c)
            print(f"  • {c} → {info.metaphor} ({info.category.value})")
        return
    
    if args.list_categories:
        print("\n📂 类别列表:")
        for cat in visualizer.list_categories():
            print(f"  • {cat}")
        return
    
    if args.list_styles:
        print("\n🎨 风格列表:")
        for k, v in visualizer.list_styles().items():
            desc = visualizer.style_templates[k]["description"]
            print(f"  • {k}: {v} - {desc}")
        return
    
    # 生成操作
    if args.concept:
        result = visualizer.generate(args.concept, args.style, args.metaphor)
        
        print(f"\n🎨 概念可视化生成结果")
        print(f"="*50)
        print(f"📌 概念: {result['concept']}")
        print(f"📂 类别: {result['category']}")
        print(f"🔗 比喻: {result['metaphor']}")
        print(f"🎭 风格: {result['style']}")
        print(f"\n📖 说明: {result['description']}")
        
        if result['key_points']:
            print(f"\n✨ 核心要点:")
            for p in result['key_points']:
                print(f"  • {p}")
        
        if result['common_mistakes']:
            print(f"\n⚠️ 常见误区:")
            for m in result['common_mistakes']:
                print(f"  • {m}")
        
        print(f"\n📝 生成Prompt:")
        print(f"  {result['prompt'][:200]}...")
        return
    
    # 批量操作
    if args.batch:
        with open(args.batch, 'r', encoding='utf-8') as f:
            concepts = [line.strip() for line in f if line.strip()]
        
        print(f"\n🔄 批量生成 {len(concepts)} 个概念...")
        results = []
        for concept in concepts:
            result = visualizer.generate(concept, args.style)
            results.append(result)
            print(f"  ✓ {concept} → {result['metaphor']}")
        
        if args.output:
            output_file = os.path.join(args.output, "batch_results.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n💾 结果已保存到: {output_file}")
        return
    
    # 无参数时显示帮助
    parser.print_help()


if __name__ == "__main__":
    main()
