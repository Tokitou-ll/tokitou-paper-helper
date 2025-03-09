import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import yaml
import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from services import AIServiceFactory
from utils.config import ConfigManager
from utils.pdf_utils import PDFProcessor
import re

class PaperAnalyzer:
    """论文分析器类"""
    
    def __init__(self):
        self.ai_service = AIServiceFactory.create("grok")
        self.prompts = self._load_prompts()
        self.pdf_processor = PDFProcessor()
        
    def _load_prompts(self):
        """加载提示模板"""
        prompt_path = Path("config/prompts.yaml")
        if not prompt_path.exists():
            raise FileNotFoundError("提示模板配置文件不存在！")
            
        with open(prompt_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    
    def analyze_paper(self, pdf_path: str):
        """分析单篇论文"""
        try:
            print(f"\n开始分析论文：{pdf_path}")
            
            # 1. 验证PDF文件
            if not Path(pdf_path).exists():
                raise FileNotFoundError(f"PDF文件不存在：{pdf_path}")
            
            # 2. 提取文本和元数据
            print("\n步骤1：提取论文内容")
            paper_content = self.pdf_processor.extract_text(pdf_path)
            paper_info = self.pdf_processor.extract_metadata(pdf_path)
            
            # 3. 分析论文类型
            print("\n步骤2：分析论文类型")
            paper_type_result = self._analyze_paper_type(paper_info, paper_content)
            
            # 4. 生成综合报告
            print("\n步骤3：生成分析报告")
            final_report = self._generate_final_report(
                paper_info, 
                paper_type_result
            )
            
            # 5. 保存结果
            print("\n步骤4：保存分析结果")
            self._save_results(pdf_path, {
                "paper_info": paper_info,
                "paper_type_analysis": paper_type_result,
                "final_report": final_report,
                "analysis_time": datetime.now().isoformat()
            })
            
            return True
            
        except Exception as e:
            print(f"论文分析过程中出错：{str(e)}")
            return False
    
    def _analyze_paper_type(self, paper_info, paper_content):
        """分析论文类型（官方/非官方实现）"""
        messages = [
            {
                "role": "system",
                "content": self.prompts["analysis_prompts"]["paper_type"]["system"]
            },
            {
                "role": "user",
                "content": self.prompts["analysis_prompts"]["paper_type"]["user"].format(
                    title=paper_info.get("title", ""),
                    authors=paper_info.get("authors", ""),
                    abstract=paper_content.get("abstract", ""),
                    key_sections=paper_content.get("key_sections", "")
                )
            }
        ]
        
        response = self.ai_service.chat_completion(messages)
        return response["content"]
    
    def _generate_final_report(self, paper_info, paper_analysis):
        """生成最终分析报告"""
        messages = [
            {
                "role": "system",
                "content": self.prompts["analysis_prompts"]["final_report"]["system"]
            },
            {
                "role": "user",
                "content": self.prompts["analysis_prompts"]["final_report"]["user"].format(
                    paper_analysis=paper_analysis
                )
            }
        ]
        
        response = self.ai_service.chat_completion(messages)
        return response["content"]
    
    def _save_results(self, pdf_path: str, results: dict):
        """保存分析结果"""
        output_dir = Path("output/analysis/report")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成安全的文件名
        safe_name = re.sub(r'[^\w\-_\. ]', '_', Path(pdf_path).stem)
        
        # 保存Markdown报告
        report_path = output_dir / f"{safe_name}_analysis.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(results["final_report"])
        
        # 保存完整结果
        json_path = output_dir / f"{safe_name}_analysis.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"分析报告已保存到：{report_path}")
        print(f"完整结果已保存到：{json_path}")

def select_paper() -> Optional[str]:
    """选择要分析的论文"""
    config = ConfigManager()
    papers_dir = Path(config.get_config("paths")["data_dir"])
    
    if not papers_dir.exists():
        print(f"论文目录不存在：{papers_dir}")
        return None
    
    pdf_files = list(papers_dir.glob("*.pdf"))
    if not pdf_files:
        print("未找到PDF文件！")
        return None
    
    return str(pdf_files[0])

def main():
    """工作流3主函数"""
    print("开始执行工作流3：单篇论文分析...\n")
    
    try:
        # 选择论文
        pdf_path = select_paper()
        if not pdf_path:
            return False
        
        # 创建分析器并执行分析
        analyzer = PaperAnalyzer()
        success = analyzer.analyze_paper(pdf_path)
        
        if success:
            print("\n工作流3执行完成！")
            print(f"\n已分析论文：{pdf_path}")
            print("\n生成的文件：")
            print(f"- 提取文本：output/analysis/text/extracted_text.txt")
            print(f"- 分析报告：output/analysis/report/{Path(pdf_path).stem}_analysis.md")
            print(f"- 分析结果：output/analysis/report/{Path(pdf_path).stem}_analysis.json")
        
        return success
        
    except Exception as e:
        print(f"工作流执行出错：{str(e)}")
        return False

if __name__ == "__main__":
    main() 