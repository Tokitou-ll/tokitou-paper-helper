import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from pathlib import Path
import yaml
from scripts.preprocessing.validate_pdf import validate_pdf
from scripts.preprocessing.extract_text import extract_text
from scripts.preprocessing.preprocess_text import preprocess_text
from scripts.analysis.prepare_analysis_rules import prepare_analysis_rules
from scripts.analysis.analyze_paper import analyze_paper
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

def analyze_single_paper(pdf_path):
    """分析单篇论文"""
    try:
        print(f"\n开始分析论文：{pdf_path}")
        
        # 1. 验证PDF文件
        print("\n步骤1：验证PDF文件")
        if not validate_pdf(pdf_path):
            print("PDF文件验证失败！")
            return False
        print("PDF文件验证成功！")
        
        # 2. 提取文本
        print("\n步骤2：提取文本内容")
        if not extract_text(pdf_path):
            print("文本提取失败！")
            return False
        print("文本提取成功！")
        
        # 3. 预处理文本
        print("\n步骤3：预处理文本")
        text_file = "output/analysis/text/extracted_text.txt"
        if not preprocess_text(text_file):
            print("文本预处理失败！")
            return False
        print("文本预处理成功！")
        
        # 4. 准备分析规则
        print("\n步骤4：准备分析规则")
        if not prepare_analysis_rules():
            print("规则准备失败！")
            return False
        print("规则准备成功！")
        
        # 5. 分析论文
        print("\n步骤5：分析论文")
        if not analyze_paper():
            print("论文分析失败！")
            return False
        print("论文分析成功！")
        
        # 6. 更新汇总文件
        print("\n步骤6：更新汇总文件")
        if not update_paper_summary():
            print("更新汇总文件失败！")
            return False
        print("更新汇总文件成功！")
        
        return True
        
    except Exception as e:
        print(f"分析论文过程中出错：{str(e)}")
        return False

def select_paper():
    """从论文目录中选择第一篇论文"""
    try:
        # 加载配置
        config = load_config()
        if not config:
            return None
        
        papers_dir = Path(config["directories"]["papers"])
        if not papers_dir.exists():
            print(f"论文目录不存在：{papers_dir}")
            return None
            
        pdf_files = list(papers_dir.glob("*.pdf"))
        if not pdf_files:
            print("未找到PDF文件！")
            return None
            
        # 选择第一个PDF文件
        return str(pdf_files[0])
        
    except Exception as e:
        print(f"选择论文时出错：{str(e)}")
        return None

def main():
    """工作流3：单篇论文分析"""
    print("开始执行工作流3：单篇论文分析...\n")
    
    # 选择要分析的论文
    pdf_path = select_paper()
    if not pdf_path:
        return False
    
    # 分析论文
    if not analyze_single_paper(pdf_path):
        return False
    
    print("\n工作流3执行完成！")
    print("\n执行结果汇总：")
    print("1. 分析的论文：")
    print(f"   - 文件路径：{pdf_path}")
    print("\n2. 生成的文件：")
    print("   - 提取文本：output/analysis/text/extracted_text.txt")
    print("   - 预处理文本：output/analysis/text/preprocessed_text.txt")
    print("   - 分析规则：output/analysis/rules/analysis_rules.json")
    print("   - 分析报告：output/analysis/report/analysis_report.md")
    print("   - 分析结果：output/analysis/report/analysis_results.json")
    print("   - 更新汇总：output/paper_summary.md")
    return True

if __name__ == "__main__":
    main() 