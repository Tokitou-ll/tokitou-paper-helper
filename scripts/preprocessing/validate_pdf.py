import os
from pathlib import Path

def validate_pdf(file_path):
    """验证 PDF 文件是否存在且可读"""
    try:
        # 使用 Path 对象处理路径
        path = Path(file_path)
        directory = path.parent
        target_filename = path.name
        
        # 检查目录是否存在
        if not directory.exists():
            print(f"目录不存在: {directory}")
            return False
            
        # 查找匹配的文件（忽略不可见字符和空格差异）
        actual_filename = None
        for filename in os.listdir(directory):
            # 规范化文件名：移除不可见字符，统一空格
            normalized_filename = filename.replace('\xa0', ' ').strip()
            normalized_target = target_filename.replace('\xa0', ' ').strip()
            
            if normalized_filename == normalized_target:
                actual_filename = filename
                break
        
        if actual_filename is None:
            print(f"找不到匹配的文件: {target_filename}")
            return False
            
        path = directory / actual_filename
        print(f"正在验证文件: {path}")
        
        if not path.exists():
            print(f"文件不存在: {path}")
            return False
        
        if not path.is_file():
            print("路径不是一个文件")
            return False
            
        if not os.access(str(path), os.R_OK):
            print("文件不可读")
            return False
            
        if path.suffix.lower() != '.pdf':
            print("文件不是 PDF 格式")
            return False
            
        file_size = path.stat().st_size / 1024 / 1024  # 转换为 MB
        print(f"文件验证成功：")
        print(f"- 路径: {path}")
        print(f"- 大小: {file_size:.2f} MB")
        return path
        
    except Exception as e:
        print(f"验证过程中出现错误: {str(e)}")
        return False

if __name__ == "__main__":
    # 测试不同类型的文件名
    test_files = [
        "data/test/GazeDiff A radiologist visual attention guided diffusion model for zero-shot disease classification.pdf",
        "data/test/Generating Realistic Brain MRIs via a Conditional Diffusion Probabilistic Model.pdf",
        "data/test/test file with spaces.pdf"  # 测试文件不存在，应该返回False
    ]
    
    for pdf_path in test_files:
        print(f"\n测试文件：{pdf_path}")
        result = validate_pdf(pdf_path)
        
        if result:
            report_path = Path("output/analysis/report/validation_result.md")
            report_path.parent.mkdir(parents=True, exist_ok=True)
            with open(report_path, "w", encoding="utf-8") as f:
                f.write("# PDF 文件验证报告\n\n")
                f.write("## 文件信息\n")
                f.write(f"- 文件路径：{result}\n")
                f.write(f"- 文件大小：{result.stat().st_size / 1024 / 1024:.2f} MB\n")
                f.write(f"- 验证时间：{os.path.getmtime(result)}\n")
                f.write("\n## 验证结果\n")
                f.write("- ✓ 文件验证成功\n") 