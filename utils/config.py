import os
import yaml
from typing import Dict, Any

class ConfigManager:
    """配置管理类"""
    
    _instance = None
    _configs: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._configs:
            self.load_configs()
    
    def load_configs(self):
        """加载所有配置文件"""
        config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
        
        # 配置文件映射：实际文件 -> 示例文件
        config_files = {
            'batch_config.yaml': 'batch_config.example.yaml',
            'path_config.yaml': 'path_config.example.yaml',
            'ai_config.yaml': 'ai_config.example.yaml'
        }
        
        for config_file, example_file in config_files.items():
            config_name = config_file.replace('.yaml', '')
            file_path = os.path.join(config_dir, config_file)
            example_path = os.path.join(config_dir, example_file)
            
            # 优先使用实际配置文件，如果不存在则使用示例配置
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    self._configs[config_name] = yaml.safe_load(f)
            elif os.path.exists(example_path):
                with open(example_path, 'r', encoding='utf-8') as f:
                    self._configs[config_name] = yaml.safe_load(f)
                print(f"警告: 使用示例配置文件 {example_file}，建议创建实际配置文件 {config_file}")
    
    def get_ai_config(self, service_name: str) -> Dict[str, Any]:
        """
        获取指定AI服务的配置
        
        Args:
            service_name: 服务名称（如 'grok'）
            
        Returns:
            服务配置字典
            
        Raises:
            ValueError: 如果服务配置不存在
        """
        try:
            return self._configs['ai_config']['services'][service_name]
        except KeyError:
            raise ValueError(f"AI服务 {service_name} 的配置不存在")
    
    def get_config(self, config_name: str) -> Dict[str, Any]:
        """
        获取指定配置
        
        Args:
            config_name: 配置名称
            
        Returns:
            配置字典
            
        Raises:
            ValueError: 如果配置不存在
        """
        try:
            return self._configs[config_name]
        except KeyError:
            raise ValueError(f"配置 {config_name} 不存在") 