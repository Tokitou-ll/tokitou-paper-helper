from typing import List, Dict, Any, Optional, Iterator
from openai import OpenAI
from .base import AIService

class GrokService(AIService):
    """Grok AI服务实现类"""
    
    def __init__(
        self,
        api_key: str,
        api_base: str = "https://api.groq.com/openai/v1",
        model: str = "grok-2",
        timeout: int = 60
    ):
        """
        初始化Grok服务
        
        Args:
            api_key: Grok API密钥
            api_base: API基础URL
            model: 默认使用的模型
            timeout: 请求超时时间（秒）
        """
        self.client = OpenAI(
            api_key=api_key,
            base_url=api_base,
            timeout=timeout
        )
        self.default_model = model

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行聊天完成请求
        
        Args:
            messages: 消息列表
            model: 模型名称，如果未指定则使用默认模型
            temperature: 温度参数
            max_tokens: 最大输出token数
            **kwargs: 其他OpenAI API支持的参数
            
        Returns:
            返回AI响应的字典
        """
        try:
            response = self.client.chat.completions.create(
                model=model or self.default_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            return {
                "content": response.choices[0].message.content,
                "role": response.choices[0].message.role,
                "finish_reason": response.choices[0].finish_reason,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
        except Exception as e:
            raise Exception(f"Grok API调用失败: {str(e)}")
            
    def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Iterator[Dict[str, Any]]:
        """
        执行流式聊天完成请求
        
        Args:
            messages: 消息列表
            model: 模型名称，如果未指定则使用默认模型
            temperature: 温度参数
            max_tokens: 最大输出token数
            **kwargs: 其他OpenAI API支持的参数
            
        Yields:
            返回AI响应的流式数据
        """
        try:
            response = self.client.chat.completions.create(
                model=model or self.default_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs
            )
            
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    yield {
                        "content": chunk.choices[0].delta.content,
                        "role": chunk.choices[0].delta.role if hasattr(chunk.choices[0].delta, 'role') else None,
                        "finish_reason": chunk.choices[0].finish_reason
                    }
                    
        except Exception as e:
            raise Exception(f"Grok流式API调用失败: {str(e)}") 