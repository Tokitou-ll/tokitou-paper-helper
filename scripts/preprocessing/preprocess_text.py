import os
import re
from pathlib import Path

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

def preprocess_text(input_file):
    """预处理提取的文本内容"""
    try:
        # 读取原始文本
        with open(input_file, "r", encoding="utf-8") as f:
            text = f.read()
            
        # 1. 清理特殊字符
        # 保留换行符，但删除连续的空白字符
        text = re.sub(r'[ \t]+', ' ', text)
        # 删除连续的换行符
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # 2. 标记可能的代码块
        # 寻找可能包含代码的段落（包含特定关键字或模式）
        code_keywords = [
            r'import\s+\w+',
            r'def\s+\w+\s*\(',
            r'class\s+\w+',
            r'return\s+',
            r'for\s+\w+\s+in\s+',
            r'if\s+.*:',
            r'while\s+.*:',
            r'print\s*\(',
            r'=\s*\w+\(',
            r'\.py$'
        ]
        
        # 用特殊标记包围可能的代码块
        for keyword in code_keywords:
            text = re.sub(
                f'([^\n]*{keyword}[^\n]*)',
                r'[CODE_BLOCK_START]\1[CODE_BLOCK_END]',
                text
            )
        
        # 3. 保存处理后的文本
        output_dir = Path("output/analysis/text")
        output_file = output_dir / "preprocessed_text.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)
            
        print(f"\n文本预处理完成！")
        print(f"输出文件：{output_file}")
        print(f"文本大小：{len(text) / 1024:.2f} KB")
        
        # 生成预处理报告
        report_path = Path("output/analysis/report/preprocessing_result.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# 文本预处理报告\n\n")
            f.write("## 处理信息\n")
            f.write(f"- 源文件：{input_file}\n")
            f.write(f"- 输出文件：{output_file}\n")
            f.write(f"- 文本大小：{len(text) / 1024:.2f} KB\n")
            
            # 统计可能的代码块数量
            code_blocks = len(re.findall(r'\[CODE_BLOCK_START\].*?\[CODE_BLOCK_END\]', text, re.DOTALL))
            f.write(f"- 检测到的代码块数量：{code_blocks}\n")
            
            f.write("\n## 预处理步骤\n")
            f.write("1. 清理特殊字符\n")
            f.write("2. 规范化空白字符\n")
            f.write("3. 标记可能的代码块\n")
            
            f.write("\n## 处理结果\n")
            f.write("- ✓ 文本预处理成功\n")
            
        return True
        
    except Exception as e:
        print(f"文本预处理过程中出错: {str(e)}")
        return False

if __name__ == "__main__":
    input_file = "output/analysis/text/extracted_text.txt"
    preprocess_text(input_file) 