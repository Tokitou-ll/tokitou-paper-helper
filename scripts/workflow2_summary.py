import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from pathlib import Path
from datetime import datetime
import yaml
from scripts.utils.update_summary import update_paper_summary

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

def scan_papers():
    """扫描论文目录，获取基本信息"""
    try:
        # 加载配置
        config = load_config()
        if not config:
            return False
        
        papers_dir = Path(config["directories"]["papers"])
        if not papers_dir.exists():
            print(f"论文目录不存在：{papers_dir}")
            return False
            
        pdf_files = list(papers_dir.glob("*.pdf"))
        if not pdf_files:
            print("未找到PDF文件！")
            return False
            
        print(f"\n找到 {len(pdf_files)} 个PDF文件：")
        for pdf_file in pdf_files:
            size_mb = pdf_file.stat().st_size / (1024 * 1024)
            mod_time = datetime.fromtimestamp(pdf_file.stat().st_mtime)
            print(f"- {pdf_file.name}")
            print(f"  大小：{size_mb:.2f}MB")
            print(f"  修改时间：{mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
        return True
        
    except Exception as e:
        print(f"扫描论文目录时出错：{str(e)}")
        return False

def generate_summary():
    """生成论文汇总文档"""
    try:
        # 调用更新汇总文件的函数
        update_paper_summary()
        return True
        
    except Exception as e:
        print(f"生成汇总文档时出错：{str(e)}")
        return False

def main():
    """工作流2：论文信息汇总"""
    print("开始执行工作流2：论文信息汇总...\n")
    
    # 扫描论文目录
    if not scan_papers():
        return False
    
    # 生成汇总文档
    if not generate_summary():
        return False
    
    print("\n工作流2执行完成！")
    print("\n执行结果汇总：")
    print("1. 扫描结果：")
    print(f"   - 扫描目录：{config['directories']['papers']}")
    print(f"   - 文件类型：PDF")
    print("\n2. 生成的文件：")
    print("   - 汇总文档：output/paper_summary.md")
    print("   - 文档内容：")
    print("     * 论文基本信息")
    print("     * 统计数据")
    print("     * 分析进度")
    print("     * 更新记录")
    return True

if __name__ == "__main__":
    main() 