import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from pathlib import Path
from scripts.batch.batch_process import BatchProcessor
from scripts.utils.cleanup import cleanup_temp_files

def prepare_batch_environment():
    """准备批处理环境"""
    try:
        # 清理临时文件
        if not cleanup_temp_files():
            print("清理临时文件失败！")
            return False
            
        # 检查配置文件
        config_file = Path("config/batch_config.yaml")
        if not config_file.exists():
            print(f"配置文件不存在：{config_file}")
            return False
            
        print("批处理环境准备完成！")
        return True
        
    except Exception as e:
        print(f"准备批处理环境时出错：{str(e)}")
        return False

def run_batch_process():
    """运行批处理任务"""
    try:
        # 创建批处理器实例
        processor = BatchProcessor()
        
        # 扫描PDF目录
        pdf_files = processor.scan_pdf_directory()
        if not pdf_files:
            print("未找到需要处理的PDF文件！")
            return False
            
        print(f"\n找到 {len(pdf_files)} 个待处理文件")
        
        # 添加任务到队列
        for paper in pdf_files:
            processor.add_task(paper)
            
        # 启动处理
        processor.start()
        
        print("\n批处理任务完成！")
        return True
        
    except Exception as e:
        print(f"运行批处理任务时出错：{str(e)}")
        return False

def main():
    """工作流4：批量分析任务"""
    print("开始执行工作流4：批量分析任务...\n")
    
    # 准备批处理环境
    if not prepare_batch_environment():
        return False
    
    # 运行批处理任务
    if not run_batch_process():
        return False
    
    print("\n工作流4执行完成！")
    print("\n执行结果汇总：")
    print("1. 批处理配置：")
    print("   - 配置文件：config/batch_config.yaml")
    print("\n2. 生成的文件：")
    print("   - 批处理结果：output/analysis/report/batch/batch_results.json")
    print("   - 批处理报告：output/analysis/report/batch/batch_report.md")
    print("   - 分析报告：output/analysis/report/analysis_report.md")
    print("   - 分析结果：output/analysis/report/analysis_results.json")
    print("\n3. 临时文件：")
    print("   - 文本文件：output/analysis/text/")
    print("   - 分析规则：output/analysis/rules/")
    print("   - 日志文件：logs/")
    return True

if __name__ == "__main__":
    main() 