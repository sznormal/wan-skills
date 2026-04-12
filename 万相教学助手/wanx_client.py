"""
万相教学助手 - 通义万相Wan 2.7 API客户端
调用阿里通义万相API生成教学视频和图片素材
"""

import os
import json
import time
import requests
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path


class WanXClient:
    """通义万相Wan 2.7 API客户端"""
    
    BASE_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
    
    def __init__(self, api_key: str, workspace: str = "./output"):
        """
        初始化客户端
        
        Args:
            api_key: 阿里云DashScope API密钥
            workspace: 输出目录
        """
        self.api_key = api_key
        self.workspace = Path(workspace)
        self.workspace.mkdir(parents=True, exist_ok=True)
        
    def _get_headers(self) -> Dict[str, str]:
        """构建请求头"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "true"  # 启用异步模式
        }
    
    def _save_result(self, task_id: str, result: Dict, filename: str) -> str:
        """保存API返回结果"""
        output_path = self.workspace / f"{task_id}_{filename}"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        return str(output_path)
    
    # ==================== 文生图 API ====================
    
    def text_to_image(
        self,
        prompt: str,
        model: str = "wan2.7-image-pro",
        negative_prompt: Optional[str] = None,
        resolution: str = "1024x1024",
        style: Optional[str] = None,
        extra_params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        调用文生图API生成教学图片
        
        Args:
            prompt: 英文提示词
            model: 使用的模型
            negative_prompt: 负面提示词
            resolution: 图片分辨率
            style: 风格选项
            extra_params: 额外参数
            
        Returns:
            包含任务ID和状态信息的字典
        """
        payload = {
            "model": model,
            "input": {
                "prompt": prompt,
                "negative_prompt": negative_prompt or "blurry, low quality, distorted",
                "resolution": resolution
            },
            "parameters": {
                "response_mode": "blocking"
            }
        }
        
        if style:
            payload["parameters"]["style"] = style
            
        if extra_params:
            payload["parameters"].update(extra_params)
        
        try:
            response = requests.post(
                self.BASE_URL,
                headers=self._get_headers(),
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            
            task_id = result.get("output", {}).get("task_id", "")
            self._save_result(task_id, result, "text_to_image_result.json")
            
            return {
                "success": True,
                "task_id": task_id,
                "status": result.get("output", {}).get("task_status", "PROCESSING"),
                "result": result
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"API请求失败: {e}"
            }
    
    # ==================== 文生视频 API ====================
    
    def text_to_video(
        self,
        prompt: str,
        duration: int = 5,
        resolution: str = "1280x720",
        negative_prompt: Optional[str] = None,
        extra_params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        调用文生视频API生成教学视频
        
        Args:
            prompt: 英文提示词（建议包含运动描述）
            duration: 视频时长（秒），支持5-10秒
            resolution: 视频分辨率
            negative_prompt: 负面提示词
            extra_params: 额外参数
            
        Returns:
            包含任务ID和状态信息的字典
        """
        payload = {
            "model": "wan2.7-t2v",
            "input": {
                "prompt": prompt,
                "duration": duration
            },
            "parameters": {
                "resolution": resolution
            }
        }
        
        if negative_prompt:
            payload["input"]["negative_prompt"] = negative_prompt
            
        if extra_params:
            payload["parameters"].update(extra_params)
        
        try:
            response = requests.post(
                self.BASE_URL,
                headers=self._get_headers(),
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            result = response.json()
            
            task_id = result.get("output", {}).get("task_id", "")
            self._save_result(task_id, result, "text_to_video_result.json")
            
            return {
                "success": True,
                "task_id": task_id,
                "status": result.get("output", {}).get("task_status", "PROCESSING"),
                "result": result
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"API请求失败: {e}"
            }
    
    # ==================== 图生视频 API ====================
    
    def image_to_video(
        self,
        image_url: str,
        prompt: str,
        duration: int = 5,
        extra_params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        调用图生视频API将教学图片动画化
        
        Args:
            image_url: 图片URL或本地路径
            prompt: 视频描述提示词
            duration: 视频时长（秒）
            extra_params: 额外参数
            
        Returns:
            包含任务ID和状态信息的字典
        """
        payload = {
            "model": "wan2.7-i2v",
            "input": {
                "prompt": prompt,
                "image_url": image_url
            },
            "parameters": {
                "duration": duration
            }
        }
        
        if extra_params:
            payload["parameters"].update(extra_params)
        
        try:
            response = requests.post(
                self.BASE_URL,
                headers=self._get_headers(),
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            result = response.json()
            
            task_id = result.get("output", {}).get("task_id", "")
            self._save_result(task_id, result, "image_to_video_result.json")
            
            return {
                "success": True,
                "task_id": task_id,
                "status": result.get("output", {}).get("task_status", "PROCESSING"),
                "result": result
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"API请求失败: {e}"
            }
    
    # ==================== 任务查询 ====================
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        查询异步任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务状态和结果
        """
        status_url = f"{self.BASE_URL}/query"
        
        try:
            payload = {"task_id": task_id}
            response = requests.post(
                status_url,
                headers=self._get_headers(),
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            return {
                "success": True,
                "task_id": task_id,
                "status": result.get("output", {}).get("task_status", "UNKNOWN"),
                "result": result
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "task_id": task_id
            }
    
    # ==================== 教学素材批量生成 ====================
    
    def generate_teaching_series(
        self,
        prompts: List[str],
        output_prefix: str = "teaching_series"
    ) -> List[Dict[str, Any]]:
        """
        批量生成教学素材
        
        Args:
            prompts: 提示词列表
            output_prefix: 输出文件前缀
            
        Returns:
            所有任务的结果列表
        """
        results = []
        
        for i, prompt in enumerate(prompts):
            print(f"正在生成第 {i+1}/{len(prompts)} 个素材...")
            
            # 根据提示词内容判断生成类型
            if any(keyword in prompt.lower() for keyword in ['video', 'animation', 'motion']):
                result = self.text_to_video(prompt)
            else:
                result = self.text_to_image(prompt)
            
            results.append({
                "index": i + 1,
                "prompt": prompt,
                "result": result
            })
            
            # 避免请求过快
            if i < len(prompts) - 1:
                time.sleep(2)
        
        # 保存批量生成结果
        output_path = self.workspace / f"{output_prefix}_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        return results


def main():
    """示例用法"""
    # 从环境变量获取API密钥
    api_key = os.getenv("DASHSCOPE_API_KEY")
    
    if not api_key:
        print("请设置 DASHSCOPE_API_KEY 环境变量")
        return
    
    # 初始化客户端
    client = WanXClient(api_key, workspace="./teaching_output")
    
    # 示例：生成教学图片
    print("=== 文生图示例 ===")
    image_result = client.text_to_image(
        prompt="Educational science animation, plant photosynthesis process, 
                green leaves with sunlight, clear educational style, 
                labeled arrows showing energy flow, vibrant colors",
        resolution="1024x1024"
    )
    print(f"图片生成任务: {image_result}")
    
    # 示例：生成教学视频
    print("\n=== 文生视频示例 ===")
    video_result = client.text_to_video(
        prompt="Educational animation showing cell division process, 
                gradual splitting of cell, visible chromosomes, 
                smooth animation, professional teaching style",
        duration=5
    )
    print(f"视频生成任务: {video_result}")


if __name__ == "__main__":
    main()
