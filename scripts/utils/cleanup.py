import os
import shutil
from pathlib import Path

def cleanup_temp_files():
    """清理临时文件和分析过程中生成的中间文件"""
    # 需要清理的目录
    cleanup_dirs = [
        'output/analysis/text',
        'output/analysis/rules',
        'output/temp',
        'logs'
    ]
    
    # 需要保留的目录
    keep_dirs = [
        'output/analysis/report'
    ]
    
    try:
        # 清理指定目录
        for dir_path in cleanup_dirs:
            path = Path(dir_path)
            if path.exists():
                print(f"正在清理目录：{dir_path}")
                shutil.rmtree(path)
                path.mkdir(parents=True, exist_ok=True)
                
        # 确保需要保留的目录存在
        for dir_path in keep_dirs:
            path = Path(dir_path)
            if not path.exists():
                print(f"创建目录：{dir_path}")
                path.mkdir(parents=True, exist_ok=True)
                
        print("清理完成！")
        return True
        
    except Exception as e:
        print(f"清理过程中出错：{str(e)}")
        return False

if __name__ == "__main__":
    cleanup_temp_files() 