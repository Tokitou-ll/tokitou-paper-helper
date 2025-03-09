from typing import Dict, Type
from .base import AIService
from .grok import GrokService
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from utils.config import ConfigManager

class AIServiceFactory:
    """AI服务工厂类"""
    
    _services: Dict[str, Type[AIService]] = {
        "grok": GrokService
    }
    
    @classmethod
    def create(cls, service_type: str, **kwargs) -> AIService:
        """
        创建AI服务实例
        
        Args:
            service_type: 服务类型（如 'grok'）
            **kwargs: 可选的服务初始化参数，会覆盖配置文件中的参数
            
        Returns:
            AIService实例
            
        Raises:
            ValueError: 如果服务类型不存在
        """
        if service_type not in cls._services:
            raise ValueError(f"不支持的AI服务类型: {service_type}")
        
        # 获取配置
        config = ConfigManager().get_ai_config(service_type)
        
        # 提取构造函数需要的参数
        service_params = {
            "api_key": config.get("api_key"),
            "api_base": config.get("api_base", "https://api.groq.com/openai/v1"),
            "model": config.get("model", "grok-2"),
            "timeout": config.get("timeout", 60)
        }
        
        # 更新传入的参数（只更新构造函数支持的参数）
        for key in ["api_key", "api_base", "model", "timeout"]:
            if key in kwargs:
                service_params[key] = kwargs[key]
            
        return cls._services[service_type](**service_params) 