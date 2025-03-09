from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class AIService(ABC):
    """AI服务的基础接口类"""
    
    @abstractmethod
    async def chat_completion(
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
            messages: 消息列表，格式为 [{"role": "user", "content": "消息内容"}, ...]
            model: 模型名称
            temperature: 温度参数，控制输出的随机性
            max_tokens: 最大输出token数
            **kwargs: 其他参数
            
        Returns:
            返回AI响应的字典
        """
        pass 