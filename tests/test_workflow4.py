import os
import sys
import asyncio
import shutil
from pathlib import Path
import yaml
from unittest.mock import patch
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from scripts.workflow4_batch import BatchProcessor

def setup_test_environment():
    """准备测试环境"""
    # 确保配置文件存在
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    # 创建测试配置文件（强制更新）
    config_file = config_dir / "batch_config.yaml"
    config_content = {
        "batch": {
            "size": 2,                # 每批次处理的论文数量
            "max_retries": 2,         # 失败重试次数
            "parallel": False,        # 是否并行处理
            "timeout": 1800          # 任务超时时间（秒）
        },
        "output": {
            "summary_file": "output/test_batch_summary.md",
            "log_file": "logs/test_batch.log",
            "error_log": "logs/test_error.log",
            "log_level": "INFO",
            "report_format": "markdown"
        },
        "paths": {
            "papers_dir": "data/test",
            "output_dir": "output/analysis/report",
            "temp_dir": "output/temp"
        },
        "control": {
            "continue_on_error": True,
            "save_temp": False
        },
        "error_handling": {
            "retry_delay": 300,
            "skip_on_failure": True
        }
    }
    
    # 强制写入新的配置文件
    with open(config_file, "w", encoding="utf-8") as f:
        yaml.dump(config_content, f, allow_unicode=True, sort_keys=False)
    
    # 确保测试数据目录存在
    test_data_dir = Path("data/test")
    test_data_dir.mkdir(parents=True, exist_ok=True)
    
    # 确保输出目录存在
    output_dirs = [
        Path("output/analysis/report"),
        Path("output/temp"),
        Path("logs")
    ]
    for dir_path in output_dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # 验证配置文件内容
    with open(config_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        required_sections = ["batch", "output", "paths", "control"]
        for section in required_sections:
            if section not in config:
                raise Exception(f"配置文件缺少必要的部分：{section}")
    
    # 创建一个测试用的PDF文件（如果目录为空）
    test_papers = list(test_data_dir.glob("*.pdf"))
    if not test_papers:
        dummy_pdf_path = test_data_dir / "test_paper.pdf"
        with open(dummy_pdf_path, "wb") as f:
            f.write(b"%PDF-1.4\n%EOF")  # 创建一个最小的有效PDF文件

def cleanup_test_environment():
    """清理测试环境"""
    # 删除测试生成的文件
    test_files = [
        Path("output/test_batch_summary.md"),
        Path("logs/test_batch.log"),
        Path("logs/test_error.log")
    ]
    
    for file in test_files:
        if file.exists():
            file.unlink()

def test_batch_processor():
    """测试批处理功能"""
    try:
        # 准备测试环境
        setup_test_environment()
        
        # 创建处理器实例
        processor = BatchProcessor("config/batch_config.yaml")
        
        # 检查环境准备
        assert processor.prepare_environment(), "环境准备失败"
        
        # 检查论文扫描
        papers = processor.scan_papers()
        assert len(papers) > 0, "未找到测试论文"
        print(f"找到 {len(papers)} 篇测试论文")
        
        # 执行批处理
        processor.process_batch(papers[:2])  # 只处理前两篇论文进行测试
        assert len(processor.results) > 0, "没有成功处理的结果"
        
        # 生成汇总报告
        processor.generate_summary()
        summary_file = Path(processor.config["output"]["summary_file"])
        assert summary_file.exists(), "汇总报告未生成"
        
        # 检查日志文件
        log_file = Path(processor.config["output"]["log_file"])
        error_log = Path(processor.config["output"]["error_log"])
        assert log_file.exists(), "处理日志未生成"
        assert error_log.exists(), "错误日志未生成"
        
        print("\n测试结果：")
        print(f"- 处理成功：{len(processor.results)} 篇")
        print(f"- 处理失败：{len(processor.failed_tasks)} 篇")
        print(f"- 汇总报告：{summary_file}")
        
        return True
        
    except AssertionError as e:
        print(f"测试断言失败：{str(e)}")
        return False
        
    except Exception as e:
        print(f"测试过程出错：{str(e)}")
        return False
        
    finally:
        cleanup_test_environment()

def test_batch_processor_with_user_interaction():
    """测试带用户交互的批处理功能"""
    try:
        # 准备测试环境
        setup_test_environment()
        
        # 创建处理器实例
        processor = BatchProcessor("config/batch_config.yaml")
        
        # 检查环境准备
        assert processor.prepare_environment(), "环境准备失败"
        
        # 检查论文扫描
        papers = processor.scan_papers()
        assert len(papers) > 0, "未找到测试论文"
        print(f"找到 {len(papers)} 篇测试论文")
        
        # 测试用户选择继续处理的情况
        with patch('builtins.input', side_effect=['y']):
            processor.process_batch(papers[:3])  # 假设批次大小为2，这样会有两批
            assert len(processor.results) > 0, "没有成功处理的结果"
            print("\n测试用户选择继续的情况：")
            print(f"- 处理成功：{len(processor.results)} 篇")
            print(f"- 处理失败：{len(processor.failed_tasks)} 篇")
        
        # 重置处理器
        processor = BatchProcessor("config/batch_config.yaml")
        
        # 测试用户选择停止处理的情况
        with patch('builtins.input', side_effect=['n']):
            processor.process_batch(papers[:3])
            print("\n测试用户选择停止的情况：")
            print(f"- 处理成功：{len(processor.results)} 篇")
            print(f"- 处理失败：{len(processor.failed_tasks)} 篇")
            # 验证是否在第一批后停止
            assert len(processor.results) <= 2, "用户选择停止后仍继续处理"
        
        # 测试用户输入无效值后输入有效值的情况
        processor = BatchProcessor("config/batch_config.yaml")
        with patch('builtins.input', side_effect=['invalid', 'x', 'y']):
            processor.process_batch(papers[:3])
            assert len(processor.results) > 0, "没有成功处理的结果"
            print("\n测试用户输入无效值的情况：")
            print(f"- 处理成功：{len(processor.results)} 篇")
            print(f"- 处理失败：{len(processor.failed_tasks)} 篇")
        
        return True
        
    except AssertionError as e:
        print(f"测试断言失败：{str(e)}")
        return False
        
    except Exception as e:
        print(f"测试过程出错：{str(e)}")
        return False
        
    finally:
        cleanup_test_environment()

def main():
    """运行测试"""
    print("开始测试工作流4...")
    
    # 运行基本功能测试
    basic_test_success = test_batch_processor()
    print("\n基本功能测试", "通过" if basic_test_success else "失败")
    
    # 运行用户交互测试
    interaction_test_success = test_batch_processor_with_user_interaction()
    print("\n用户交互测试", "通过" if interaction_test_success else "失败")
    
    if basic_test_success and interaction_test_success:
        print("\n所有测试通过！")
    else:
        print("\n测试失败！")
    
    return basic_test_success and interaction_test_success

if __name__ == "__main__":
    main() 