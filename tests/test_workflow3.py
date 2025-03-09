import os
import sys
import asyncio
import re
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from pathlib import Path
from scripts.workflow3_analyze import PaperAnalyzer
import yaml

async def test_paper_analysis():
    """测试论文分析功能"""
    try:
        # 获取测试论文路径
        test_dir = Path("data/test")
        test_files = list(test_dir.glob("*.pdf"))
        if not test_files:
            print("未找到测试论文文件")
            return False
            
        # 选择第一个PDF文件并安全处理文件名
        test_pdf = test_files[0]
        test_pdf_path = str(test_pdf)
        print(f"使用测试论文：{test_pdf_path}")
        
        # 生成安全的输出文件名
        safe_name = re.sub(r'[^\w\-_\. ]', '_', test_pdf.stem)
        
        # 确保配置文件存在
        ensure_config_files()
        
        # 创建分析器实例
        analyzer = PaperAnalyzer()
        
        # 执行分析
        success = await asyncio.to_thread(analyzer.analyze_paper, test_pdf_path)
        
        if not success:
            print("论文分析失败")
            return False
        
        # 检查输出文件是否存在
        report_path = Path(f"output/analysis/report/{safe_name}_analysis.md")
        json_path = Path(f"output/analysis/report/{safe_name}_analysis.json")
        
        if not report_path.exists():
            print(f"分析报告文件不存在：{report_path}")
            return False
            
        if not json_path.exists():
            print(f"JSON结果文件不存在：{json_path}")
            return False
        
        # 验证报告内容
        with open(report_path, "r", encoding="utf-8") as f:
            report_content = f.read()
            if "基本信息" not in report_content:
                print("报告缺少基本信息部分")
                return False
            if "实现类型判定" not in report_content:
                print("报告缺少实现类型判定部分")
                return False
            if "关键发现" not in report_content:
                print("报告缺少关键发现部分")
                return False
            if "建议" not in report_content:
                print("报告缺少建议部分")
                return False
        
        print("\n分析报告内容预览：")
        print_report_preview(report_path)
        
        print("\n所有测试项通过！")
        return True
        
    except Exception as e:
        print(f"测试过程中出现错误：{str(e)}")
        return False

def print_report_preview(report_path: Path, preview_lines: int = 20):
    """打印报告预览"""
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.readlines()
            
        print("\n" + "="*50)
        print("报告前20行预览：")
        print("="*50)
        for line in content[:preview_lines]:
            print(line.strip())
        print("="*50)
        print(f"完整报告请查看：{report_path}")
        
    except Exception as e:
        print(f"读取报告时出错：{str(e)}")

def ensure_config_files():
    """确保必要的配置文件存在"""
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    # 确保prompts.yaml存在
    prompts_path = config_dir / "prompts.yaml"
    if not prompts_path.exists():
        with open(prompts_path, "w", encoding="utf-8") as f:
            yaml.dump({
                "analysis_prompts": {
                    "paper_type": {
                        "system": "你是一个专业的论文分析助手...",
                        "user": "请分析以下论文内容..."
                    },
                    "final_report": {
                        "system": "你是一个专业的论文分析报告生成器...",
                        "user": "请基于以下分析结果生成报告..."
                    }
                }
            }, f, allow_unicode=True)
    
    # 确保ai_config.yaml存在
    ai_config_path = config_dir / "ai_config.yaml"
    if not ai_config_path.exists():
        with open(ai_config_path, "w", encoding="utf-8") as f:
            yaml.dump({
                "services": {
                    "grok": {
                        "api_key": "your-api-key-here",
                        "api_base": "https://api.groq.com/openai/v1",
                        "model": "mixtral-8x7b-32768",
                        "timeout": 60
                    }
                }
            }, f, allow_unicode=True)

async def main():
    """运行测试"""
    print("开始测试工作流3...")
    try:
        await test_paper_analysis()
    except Exception as e:
        print(f"测试执行失败：{str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 