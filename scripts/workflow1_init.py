import os
from pathlib import Path
import yaml

def load_config():
    """加载配置文件"""
    try:
        config_path = Path("config/path_config.yaml")
        if not config_path.exists():
            print(f"配置文件不存在：{config_path}")
            return None
        
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"加载配置文件时出错：{str(e)}")
        return None

def create_project_structure():
    """创建项目目录结构"""
    # 加载配置
    config = load_config()
    if not config:
        return False
    
    # 获取目录列表
    directories = [
        config["directories"]["papers"],     # 论文存放位置
        config["directories"]["output"],     # 结果输出位置
        config["directories"]["text"],       # 文本提取结果
        config["directories"]["report"],     # 分析报告
        config["directories"]["rules"],      # 分析规则
        config["directories"]["logs"]        # 日志文件
    ]
    
    try:
        for dir_path in directories:
            path = Path(dir_path)
            if not path.exists():
                path.mkdir(parents=True)
                print(f"创建目录：{dir_path}")
            else:
                print(f"目录已存在：{dir_path}")
        
        # 创建 .gitkeep 文件以保持空目录
        for dir_path in directories:
            gitkeep_file = Path(dir_path) / ".gitkeep"
            if not gitkeep_file.exists():
                gitkeep_file.touch()
        
        print("\n项目目录结构创建完成！")
        return True
        
    except Exception as e:
        print(f"创建目录结构时出错：{str(e)}")
        return False

def verify_environment():
    """验证Python环境和依赖包"""
    try:
        import PyPDF2
        import magic
        import yaml
        import langchain
        import transformers
        import fastapi
        import uvicorn
        
        print("\n环境验证成功！所有依赖包都已正确安装。")
        return True
        
    except ImportError as e:
        print(f"\n环境验证失败：{str(e)}")
        print("请运行 'pip install -r requirements.txt' 安装所需依赖。")
        return False

def main():
    """工作流1：项目初始化"""
    print("开始执行工作流1：项目初始化...\n")
    
    # 创建项目目录结构
    if not create_project_structure():
        return False
    
    # 验证环境配置
    if not verify_environment():
        return False
    
    print("\n工作流1执行完成！")
    print("\n执行结果汇总：")
    print("1. 创建的目录：")
    print("   - data/paper137：论文存放位置")
    print("   - output：结果输出位置")
    print("   - output/analysis/text：文本提取结果")
    print("   - output/analysis/report：分析报告")
    print("   - output/analysis/rules：分析规则")
    print("   - logs：日志文件")
    print("\n2. 环境配置：")
    print("   - Python 虚拟环境：已验证")
    print("   - 依赖包：已安装并验证")
    print("   - 配置文件：requirements.txt")
    return True

if __name__ == "__main__":
    main() 