import os
from pathlib import Path

def print_filename_hex(directory):
    """打印目录中文件名的十六进制表示"""
    path = Path(directory)
    print(f"\n目录内容: {path.absolute()}\n")
    
    for filename in os.listdir(directory):
        print(f"文件名: {filename}")
        print(f"十六进制: {filename.encode('utf-8').hex()}")
        print("-" * 80)

if __name__ == "__main__":
    print_filename_hex("data/test") 