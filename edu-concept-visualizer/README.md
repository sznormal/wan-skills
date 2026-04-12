# 教学概念可视化器 (Edu Concept Visualizer)

> **参赛项目**：WaytoAGI整活计划第十二期「万相妙思+」快闪赛
> **主题**：「万相皆可Skill」
> **开发者**：Normal老师团队

## 🎯 项目简介

**教学概念可视化器** 是一款专为教育工作者设计的智能视觉创作工具，能够将抽象的教学概念一键转化为生动的可视化素材（图片/视频），让课堂讲解更直观、更吸引学生。

基于阿里通义万相 **Wan 2.7** 多模态大模型的强大能力，结合教育教学场景的深度优化，为教师提供备课、授课的全新工作流。

## ✨ 核心创新

### 1. 比喻式可视化
用生活化场景解释抽象概念，如"电流=水流"、"原子结构=太阳系"等，让学生秒懂。

### 2. 多维度输出
- **静态图**：概念比喻图、原理分解图、对比图
- **动态视频**：过程演示、实验模拟
- **故事板**：情境化知识讲解

### 3. 教学场景优化
针对课堂展示设计输出格式，支持4K高清输出，3K Token文字渲染能力，适合投影展示。

### 4. 学科全覆盖
支持数学、物理、化学、生物、历史、地理等多学科概念可视化。

## 🔧 技术实现

### 核心技术栈
- **模型**：阿里通义万相 Wan 2.7
  - `wan2.7-image-pro`：高质量图像生成，支持4K输出
  - `wan2.7-t2v`：文生视频，支持动态过程演示

### 关键能力利用
| Wan 2.7 能力 | 本项目应用 |
|-------------|-----------|
| 3K Token文字渲染 | 生成带完整标注的教学图 |
| 4K高清输出 | 适合大屏幕投影展示 |
| 分组图生成 | 一次生成多步骤讲解图 |
| 动态视频生成 | 实验过程、化学反应演示 |
| 多风格支持 | 卡通/写实/科学插图风格 |

### 项目结构
```
edu-concept-visualizer/
├── SKILL.md              # Skill定义文件
├── README.md             # 本文档
├── scripts/
│   └── visualize.py      # 核心Python脚本
├── references/
│   ├── wan-api-guide.md  # API调用指南
│   └── prompt-library.md # 提示词库
└── examples/
    ├── physics/          # 物理学科示例
    ├── chemistry/        # 化学学科示例
    └── math/             # 数学学科示例
```

## 📖 使用指南

### 环境配置
```bash
# 设置API Key
export WAN_API_KEY="your-api-key"

# 安装依赖
pip install requests
```

### 快速开始
```bash
# 生成概念比喻图
python scripts/visualize.py --concept "电流" --type definition --subject 物理

# 生成原理分解图
python scripts/visualize.py --concept "光合作用" --type principle --subject 生物

# 生成动态视频
python scripts/visualize.py --concept "水循环" --type process --format video --subject 地理

# 生成故事板
python scripts/visualize.py --concept "勾股定理" --type story --format storyboard --subject 数学
```

### 智能体调用示例
```
用户：帮我把"牛顿第一定律"做成教学图
触发：Edu Concept Visualizer
执行：
1. 识别概念类型：原理类
2. 学科：物理
3. 构建提示词：分步骤展示惯性定律
4. 调用wan2.7-image-pro生成
输出：带标注的牛顿第一定律示意图
```

## 🎬 效果展示

### 示例1：电流概念比喻图
**输入**：帮我把"电流"这个概念做成图，让学生更好理解
**输出**：展示水流管道系统与电路系统对比的示意图，用阀门比喻开关，水压比喻电压

### 示例2：光合作用分解图
**输入**：光合作用的过程怎么画更清晰？分步骤展示
**输出**：3张分步骤讲解图（光反应阶段→暗反应阶段→整体循环）

### 示例3：水循环动态视频
**输入**：帮我做一个"水循环"的动态讲解视频，30秒左右
**输出**：展示蒸发→凝结→降水的动态过程视频

## 🌟 应用场景

| 场景 | 使用方式 | 效果 |
|------|---------|------|
| 导入新课 | 用比喻图引发兴趣 | 学生快速建立认知 |
| 概念讲解 | 用分解图逐步展开 | 逻辑清晰易理解 |
| 实验演示 | 用动态视频模拟 | 突破时空限制 |
| 易混淆辨析 | 用对比图区分 | 强化记忆 |
| 情境教学 | 用故事板创设情境 | 沉浸式学习 |

## 🔄 可复用性

### 为什么是Skill而非一次性工具？

1. **模板化提示词**：针对5种概念类型设计专属模板，可反复调用
2. **参数化配置**：学科、风格、受众等参数灵活调整
3. **工作流集成**：可嵌入智能体工作流，与其他Skill协同
4. **持续迭代**：提示词库可持续优化，效果越来越好

### 复用示例
```python
# 第一次调用
visualizer.visualize(VisualizationRequest(
    concept="电流",
    concept_type=ConceptType.DEFINITION,
    subject=Subject.PHYSICS
))

# 第二次调用 - 同样的模板，不同的概念
visualizer.visualize(VisualizationRequest(
    concept="电压",
    concept_type=ConceptType.DEFINITION,
    subject=Subject.PHYSICS
))

# 第三次调用 - 同样的概念，不同的输出形式
visualizer.visualize(VisualizationRequest(
    concept="电流",
    concept_type=ConceptType.PRINCIPLE,  # 改为原理分解
    subject=Subject.PHYSICS
))
```

## 📊 教育价值

### 对教师的价值
- ⏱️ **节省备课时间**：从数小时缩短到数分钟
- 🎨 **提升视觉质量**：专业级教学素材
- 🔄 **灵活调整**：根据学生反馈快速迭代

### 对学生的价值
- 👁️ **直观理解**：抽象概念可视化
- 🧠 **深度记忆**：多感官学习体验
- 🎯 **精准认知**：减少误解和混淆

## 🛣️ 未来规划

### v1.1 计划
- [ ] 支持批量生成（整章知识点）
- [ ] 添加配音功能（wan2.7语音合成）
- [ ] 支持个性化风格训练

### v2.0 愿景
- [ ] 与教材章节联动
- [ ] 学情分析驱动的内容推荐
- [ ] 学生自主创作入口

## 📝 参赛信息

- **比赛名称**：WaytoAGI整活计划第十二期「万相妙思+」快闪赛
- **项目名称**：教学概念可视化器 (Edu Concept Visualizer)
- **开发团队**：Normal老师团队
- **开发时间**：2026年4月12日
- **核心技术**：阿里通义万相 Wan 2.7 API

## 📄 许可证

MIT License

---

**让每一个抽象概念都能被看见** ✨
