# Wan 2.7 API 调用指南

## API 端点

### 图像生成
```
POST https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation
```

### 视频生成
```
POST https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation
```

## 认证

所有请求需要在Header中携带API Key：

```python
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
```

## 请求格式

### 图像生成请求
```json
{
    "model": "wan2.7-image-pro",
    "input": {
        "messages": [
            {
                "role": "user",
                "content": [
                    {"text": "你的提示词"}
                ]
            }
        ]
    },
    "parameters": {
        "size": "2K",
        "n": 1
    }
}
```

### 视频生成请求
```json
{
    "model": "wan2.7-t2v",
    "input": {
        "messages": [
            {
                "role": "user",
                "content": [
                    {"text": "你的提示词"}
                ]
            }
        ]
    },
    "parameters": {
        "duration": 15
    }
}
```

## 参数说明

### 图像生成参数

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| size | string | 输出分辨率：1K/2K/4K | 2K |
| n | int | 生成图片数量（1-4） | 1 |
| enable_sequential | bool | 是否开启组图模式 | false |

### 视频生成参数

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| duration | int | 视频时长（秒） | 15 |

## 响应格式

### 成功响应
```json
{
    "output": {
        "results": [
            {
                "url": "https://xxx.com/generated_file.png"
            }
        ]
    },
    "usage": {
        "total_tokens": 100
    }
}
```

### 错误响应
```json
{
    "code": "InvalidParameter",
    "message": "错误描述"
}
```

## 最佳实践

### 1. 提示词优化
- 使用具体的描述，避免模糊表述
- 明确指定风格、视角、构图
- 包含文字标注需求时，利用3K Token能力

### 2. 质量控制
- 教学图推荐使用2K分辨率
- 需要投影展示时使用4K
- 批量生成时使用组图模式

### 3. 成本控制
- 测试时使用1K分辨率
- 设置n=1减少生成数量
- 缓存成功的提示词模板

## 错误处理

| 错误码 | 原因 | 解决方案 |
|--------|------|----------|
| 401 | API Key无效 | 检查Key是否正确 |
| 429 | 请求频率限制 | 降低调用频率 |
| 500 | 服务器错误 | 稍后重试 |

## 获取API Key

1. 访问阿里云百炼平台：https://dashscope.console.aliyun.com/
2. 创建应用或使用已有应用
3. 在应用详情页获取API Key
