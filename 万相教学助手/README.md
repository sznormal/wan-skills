# 万相教学助手 - 快速上手指南

## 环境准备

### 1. 安装依赖

```bash
pip install requests pydantic python-dotenv
```

### 2. 配置API密钥

```bash
export DASHSCOPE_API_KEY="your_api_key_here"
```

或在代码中直接传入：

```python
assistant = WanxTeachingAssistant(api_key="your_api_key")
```

## 快速开始

### 示例1：生成完整的教学视频

```python
from main import WanxTeachingAssistant

# 初始化助手
assistant = WanxTeachingAssistant()

# 生成教学视频
result = assistant.generate_lesson_video(
    subject="生物",           # 学科
    topic="细胞的有丝分裂",    # 知识点
    grade="高中",              # 年级
    style="知识动画风",        # 风格
    duration=30               # 时长（秒）
)

print(f"成功: {result.success}")
print(f"教学笔记: {result.teaching_notes}")
```

### 示例2：快速生成教学图片

```python
# 仅生成配套图片素材
result = assistant.generate_quick_image(
    subject="物理",
    topic="电磁感应原理",
    grade="高中",
    style="科幻科技风"
)
```

### 示例3：生成分镜脚本（不调用API）

```python
# 用于教学设计，不消耗API配额
storyboard = assistant.generate_storyboard_only(
    subject="历史",
    topic="丝绸之路",
    grade="初中",
    duration=45,
    template="历史叙事"
)

# 打印分镜脚本
print(storyboard["script"])
```

## 学科与风格推荐

| 学科 | 推荐风格 | 说明 |
|------|---------|------|
| 生物 | 知识动画风、自然写实风 | 细胞、生物过程用动画清晰展示 |
| 物理 | 科幻科技风 | 实验原理用科技感呈现 |
| 化学 | 科幻科技风 | 分子结构用科技风展示 |
| 历史 | 历史复古风 | 历史场景用古典风格 |
| 地理 | 自然写实风 | 地貌、气候用写实风格 |
| 语文 | 历史复古风、艺术风格 | 文学场景用艺术风格 |
| 数学 | 简约线条风 | 几何、公式用极简风格 |

## 命令行使用

```bash
# 完整流程（生成视频）
python main.py --subject 生物 --topic 细胞分裂 --grade 高中 --duration 30

# 仅生成分镜
python main.py --subject 历史 --topic 丝绸之路 --mode storyboard

# 快速生成图片
python main.py --subject 物理 --topic 电磁感应 --mode image
```

## 输出文件

生成的内容会保存在 `./teaching_output/` 目录下：

```
teaching_output/
├── xxx_storyboard.json      # 分镜脚本
├── xxx_metadata.json        # 元数据
├── xxx_task_id.txt          # 任务ID记录
└── ...
```

## 常见问题

### Q: API调用失败怎么办？

A: 检查以下几点：
1. API密钥是否正确配置
2. 网络连接是否正常
3. 提示词是否符合长度限制
4. 查看返回的错误信息

### Q: 如何生成更长的视频？

A: Wan 2.7单次视频最长10秒，可通过以下方式实现长视频：
1. 将内容分成多个短片段
2. 后期使用视频剪辑工具拼接
3. 调整分镜数量和时长分配

### Q: 如何提高生成质量？

A: 建议：
1. 知识点描述尽量具体
2. 选择最匹配的教学风格
3. 根据年级调整复杂度
4. 使用"include_labels=True"添加标注

### Q: 如何导出教学笔记？

A: `generate_lesson_video()` 返回的 `teaching_notes` 字段包含完整的教学说明，可直接保存使用。

## 扩展开发

### 添加自定义风格

编辑 `config.json` 中的 `styles` 部分：

```json
"my_custom_style": {
    "description": "我的自定义风格",
    "prompt_suffix": "your custom prompt suffix",
    "negative_prompt": "things to avoid"
}
```

### 添加新的故事板模板

编辑 `config.json` 中的 `storyboard_templates` 部分，或修改 `storyboard_generator.py`。

## 技术支持

如有问题，请联系开发者。
