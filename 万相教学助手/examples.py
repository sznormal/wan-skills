"""
使用示例脚本 - 展示万相教学助手的各种用法
"""

from main import WanxTeachingAssistant
import json


def example_1_full_video():
    """示例1：生成完整的教学视频"""
    print("=" * 60)
    print("示例1：生成完整的教学视频")
    print("=" * 60)
    
    assistant = WanxTeachingAssistant()
    
    result = assistant.generate_lesson_video(
        subject="生物",
        topic="DNA复制过程",
        grade="高中",
        style="知识动画风",
        duration=25
    )
    
    print(f"\n生成结果:")
    print(f"  成功: {result.success}")
    print(f"  视频任务数: {len(result.video_urls)}")
    print(f"  图片任务数: {len(result.image_urls)}")
    print(f"  分镜数量: {len(result.storyboard.get('scenes', [])) if result.storyboard else 0}")
    
    if result.teaching_notes:
        print(f"\n教学笔记预览:")
        print(result.teaching_notes[:500] + "...")


def example_2_quick_image():
    """示例2：快速生成教学图片"""
    print("\n" + "=" * 60)
    print("示例2：快速生成教学图片")
    print("=" * 60)
    
    assistant = WanxTeachingAssistant()
    
    result = assistant.generate_quick_image(
        subject="物理",
        topic="牛顿第三定律",
        grade="初中",
        style="科幻科技风"
    )
    
    print(f"\n生成结果:")
    print(f"  成功: {result.get('success', False)}")
    print(f"  任务ID: {result.get('task_id', 'N/A')}")


def example_3_storyboard_only():
    """示例3：仅生成分镜脚本"""
    print("\n" + "=" * 60)
    print("示例3：仅生成分镜脚本（不调用API）")
    print("=" * 60)
    
    assistant = WanxTeachingAssistant()
    
    result = assistant.generate_storyboard_only(
        subject="历史",
        topic="唐朝盛世",
        grade="初中",
        duration=40,
        template="历史叙事"
    )
    
    print(f"\n分镜脚本:")
    print(result["script"])


def example_4_multi_subject():
    """示例4：多学科对比"""
    print("\n" + "=" * 60)
    print("示例4：不同学科的风格对比")
    print("=" * 60)
    
    assistant = WanxTeachingAssistant()
    
    subjects = [
        {"subject": "生物", "topic": "细胞结构", "style": "知识动画风"},
        {"subject": "物理", "topic": "光的折射", "style": "科幻科技风"},
        {"subject": "历史", "topic": "秦始皇统一六国", "style": "历史复古风"},
        {"subject": "地理", "topic": "板块构造", "style": "自然写实风"},
        {"subject": "数学", "topic": "三角函数图像", "style": "简约线条风"},
    ]
    
    print("\n各学科推荐配置:")
    print("-" * 60)
    
    for item in subjects:
        storyboard = assistant.generate_storyboard_only(
            subject=item["subject"],
            topic=item["topic"],
            grade="高中",
            duration=20
        )
        
        scenes = storyboard["storyboard"]["scenes"]
        total_time = sum(s["duration"] for s in scenes)
        
        print(f"\n{item['subject']} - {item['topic']}")
        print(f"  风格: {item['style']}")
        print(f"  场景数: {len(scenes)}")
        print(f"  总时长: {total_time}秒")
        print(f"  分镜: {' → '.join([s['name'] for s in scenes])}")


def example_5_grade_comparison():
    """示例5：年级适配对比"""
    print("\n" + "=" * 60)
    print("示例5：同一知识点不同年级的适配")
    print("=" * 60)
    
    assistant = WanxTeachingAssistant()
    
    grades = ["小学", "初中", "高中", "大学"]
    
    for grade in grades:
        storyboard = assistant.generate_storyboard_only(
            subject="生物",
            topic="光合作用",
            grade=grade,
            duration=20
        )
        
        first_scene_prompt = storyboard["storyboard"]["scenes"][0]["prompt"]
        word_count = len(first_scene_prompt.split())
        
        print(f"\n{grade}级:")
        print(f"  提示词长度: {word_count} 词")
        print(f"  场景数: {len(storyboard['storyboard']['scenes'])}")


def run_all_examples():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("万相教学助手 - 使用示例集")
    print("=" * 60)
    print("\n注意: 运行完整示例需要有效的API密钥")
    print("-" * 60)
    
    # 示例3和4、5不需要API，可直接运行
    try:
        example_3_storyboard_only()
    except Exception as e:
        print(f"示例3执行出错: {e}")
    
    try:
        example_4_multi_subject()
    except Exception as e:
        print(f"示例4执行出错: {e}")
    
    try:
        example_5_grade_comparison()
    except Exception as e:
        print(f"示例5执行出错: {e}")
    
    print("\n" + "=" * 60)
    print("示例运行完成")
    print("=" * 60)
    print("\n如需运行完整示例（包括API调用），请确保:")
    print("1. 已配置有效的 DASHSCOPE_API_KEY")
    print("2. 运行 example_1_full_video() 或 example_2_quick_image()")


if __name__ == "__main__":
    run_all_examples()
