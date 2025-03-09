import os
from pathlib import Path
from PyPDF2 import PdfReader

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from scripts.preprocessing.validate_pdf import validate_pdf

def extract_text(pdf_path):
    """从 PDF 文件中提取文本内容"""
    try:
        # 首先验证 PDF 文件
        validated_path = validate_pdf(pdf_path)
        if not validated_path:
            print("PDF 文件验证失败，无法继续提取文本")
            return False
            
        # 读取 PDF 文件
        reader = PdfReader(str(validated_path))
        total_pages = len(reader.pages)
        print(f"PDF 文件共有 {total_pages} 页")
        
        # 提取文本
        text_content = []
        for i, page in enumerate(reader.pages, 1):
            print(f"正在处理第 {i}/{total_pages} 页...")
            text = page.extract_text()
            text_content.append(f"=== 第 {i} 页 ===\n{text}\n")
        
        # 合并所有页面的文本
        full_text = "\n".join(text_content)
        
        # 保存文本文件
        output_dir = Path("output/analysis/text")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / "extracted_text.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(full_text)
            
        print(f"\n文本提取完成！")
        print(f"输出文件：{output_file}")
        print(f"文本大小：{len(full_text) / 1024:.2f} KB")
        
        # 生成提取报告
        report_path = Path("output/analysis/report/extraction_result.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# PDF 文本提取报告\n\n")
            f.write("## 处理信息\n")
            f.write(f"- 源文件：{validated_path}\n")
            f.write(f"- 总页数：{total_pages} 页\n")
            f.write(f"- 输出文件：{output_file}\n")
            f.write(f"- 文本大小：{len(full_text) / 1024:.2f} KB\n")
            f.write("\n## 提取结果\n")
            f.write("- ✓ 文本提取成功\n")
            
        return True
        
    except Exception as e:
        print(f"文本提取过程中出现错误: {str(e)}")
        return False

if __name__ == "__main__":
    pdf_path = "data/test/GazeDiff A radiologist visual attention guided diffusion model for zero-shot disease classification.pdf"
    extract_text(pdf_path) 