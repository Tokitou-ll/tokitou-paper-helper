from pathlib import Path

def list_files(directory):
    """列出目录中的所有文件"""
    path = Path(directory)
    print(f"\n目录内容: {path.absolute()}\n")
    
    for item in path.iterdir():
        if item.is_file():
            print(f"文件名: {item.name}")
            print(f"路径: {item.absolute()}")
            print(f"大小: {item.stat().st_size / 1024 / 1024:.2f} MB")
            print("-" * 80)

if __name__ == "__main__":
    list_files("data/test") 