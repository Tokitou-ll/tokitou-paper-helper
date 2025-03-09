import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import yaml
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from scripts.workflow3_analyze import PaperAnalyzer

class BatchProcessor:
    """批量处理器类"""
    
    def __init__(self, config_file: str = "config/batch_config.yaml"):
        """初始化批处理器"""
        try:
            self.config = self._load_config(config_file)
            self.setup_logging()
            self.analyzer = PaperAnalyzer()
            self.results = []
            self.failed_tasks = []
        except Exception as e:
            print(f"初始化批处理器失败：{str(e)}")
            raise
            
    def _load_config(self, config_file: str) -> dict:
        """加载配置文件"""
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                # 验证必要的配置项
                required_sections = ["batch", "output", "paths", "control"]
                for section in required_sections:
                    if section not in config:
                        raise ValueError(f"配置文件缺少必要的部分：{section}")
                return config
        except Exception as e:
            raise Exception(f"加载配置文件失败：{str(e)}")
            
    def setup_logging(self):
        """设置日志系统"""
        try:
            log_file = self.config["output"]["log_file"]
            error_log = self.config["output"]["error_log"]
            
            # 确保日志目录存在
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
            Path(error_log).parent.mkdir(parents=True, exist_ok=True)
            
            # 设置主日志
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s [%(levelname)s] %(message)s",
                handlers=[
                    logging.FileHandler(log_file),
                    logging.StreamHandler()
                ]
            )
            
            # 设置错误日志
            error_handler = logging.FileHandler(error_log)
            error_handler.setLevel(logging.ERROR)
            logging.getLogger().addHandler(error_handler)
            
        except Exception as e:
            raise Exception(f"设置日志系统失败：{str(e)}")
        
    def prepare_environment(self) -> bool:
        """准备处理环境"""
        try:
            # 检查并创建必要的目录
            paths = self.config["paths"]
            for path in paths.values():
                Path(path).mkdir(parents=True, exist_ok=True)
                
            # 清理临时目录（如果配置要求）
            if not self.config["control"]["save_temp"]:
                temp_dir = Path(paths["temp_dir"])
                if temp_dir.exists():
                    for file in temp_dir.glob("*"):
                        file.unlink()
                        
            return True
            
        except Exception as e:
            logging.error(f"准备环境失败：{str(e)}")
            return False
            
    def scan_papers(self) -> List[Path]:
        """扫描论文目录"""
        papers_dir = Path(self.config["paths"]["papers_dir"])
        return list(papers_dir.glob("*.pdf"))
        
    def process_batch(self, papers: List[Path]) -> None:
        """处理一批论文"""
        batch_size = self.config["batch"]["size"]
        max_retries = self.config["batch"]["max_retries"]
        
        for i in range(0, len(papers), batch_size):
            batch = papers[i:i + batch_size]
            batch_num = i//batch_size + 1
            total_batches = (len(papers) + batch_size - 1) // batch_size
            
            logging.info(f"开始处理第 {batch_num}/{total_batches} 批（{len(batch)} 篇论文）")
            
            for paper in batch:
                success = False
                retries = 0
                
                while not success and retries < max_retries:
                    try:
                        if retries > 0:
                            logging.info(f"重试处理论文 {paper.name}（第 {retries} 次）")
                            
                        result = self.analyzer.analyze_paper(str(paper))
                        if result:
                            self.results.append({
                                "paper": paper.name,
                                "status": "success",
                                "time": datetime.now().isoformat()
                            })
                            success = True
                        else:
                            raise Exception("分析返回失败")
                            
                    except Exception as e:
                        retries += 1
                        error_msg = f"处理论文 {paper.name} 失败：{str(e)}"
                        logging.error(error_msg)
                        
                        if retries >= max_retries:
                            self.failed_tasks.append({
                                "paper": paper.name,
                                "error": str(e),
                                "retries": retries
                            })
                            
                            if not self.config["control"]["continue_on_error"]:
                                raise Exception(f"处理失败且配置要求停止：{error_msg}")
            
            # 每个批次处理完成后，如果不是最后一批，询问用户是否继续
            if batch_num < total_batches:
                print(f"\n已完成第 {batch_num}/{total_batches} 批处理")
                print(f"成功：{len(self.results)} 篇，失败：{len(self.failed_tasks)} 篇")
                
                while True:
                    response = input("\n是否继续处理下一批？(y/n): ").lower().strip()
                    if response in ['y', 'n']:
                        break
                    print("请输入 y 或 n")
                
                if response == 'n':
                    logging.info("用户选择停止批处理")
                    return
            
    def generate_summary(self) -> None:
        """生成汇总报告"""
        summary_file = Path(self.config["output"]["summary_file"])
        
        # 统计处理结果
        total = len(self.results) + len(self.failed_tasks)
        success = len(self.results)
        failed = len(self.failed_tasks)
        
        # 分析实现类型统计
        type_stats = {"official": 0, "unofficial": 0, "unknown": 0}
        for result in self.results:
            paper_name = result["paper"]
            report_file = Path(self.config["paths"]["output_dir"]) / f"{paper_name}_analysis.json"
            
            if report_file.exists():
                with open(report_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "官方实现" in data["paper_type_analysis"]:
                        type_stats["official"] += 1
                    elif "非官方实现" in data["paper_type_analysis"]:
                        type_stats["unofficial"] += 1
                    else:
                        type_stats["unknown"] += 1
                        
        # 生成报告
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write("# 论文分析批处理报告\n\n")
            
            f.write("## 处理概况\n")
            f.write(f"- 总论文数：{total}\n")
            f.write(f"- 处理成功：{success}\n")
            f.write(f"- 处理失败：{failed}\n")
            f.write(f"- 处理时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## 实现类型统计\n")
            f.write(f"- 官方实现：{type_stats['official']} ({type_stats['official']/total*100:.1f}%)\n")
            f.write(f"- 非官方实现：{type_stats['unofficial']} ({type_stats['unofficial']/total*100:.1f}%)\n")
            f.write(f"- 无法判定：{type_stats['unknown']} ({type_stats['unknown']/total*100:.1f}%)\n\n")
            
            f.write("## 分析结果汇总\n")
            for result in self.results:
                paper_name = result["paper"]
                report_file = Path(self.config["paths"]["output_dir"]) / f"{paper_name}_analysis.json"
                
                if report_file.exists():
                    with open(report_file, "r", encoding="utf-8") as rf:
                        data = json.load(rf)
                        f.write(f"\n### {paper_name}\n")
                        f.write(f"- 分析时间：{result['time']}\n")
                        f.write(f"- 详细报告：[查看报告]({report_file})\n")
                        f.write(f"- 主要发现：\n")
                        f.write(f"  * 实现类型：{'官方实现' if '官方实现' in data['paper_type_analysis'] else '非官方实现'}\n")
                        f.write(f"  * 可信度：{'高' if '可信度：高' in data['paper_type_analysis'] else '中' if '可信度：中' in data['paper_type_analysis'] else '低'}\n")
            
            if self.failed_tasks:
                f.write("\n## 处理失败列表\n")
                for task in self.failed_tasks:
                    f.write(f"\n### {task['paper']}\n")
                    f.write(f"- 错误信息：{task['error']}\n")
                    f.write(f"- 重试次数：{task['retries']}\n")
                    
        logging.info(f"汇总报告已生成：{summary_file}")
        
    def run(self) -> bool:
        """运行批处理"""
        try:
            # 1. 准备环境
            logging.info("准备处理环境...")
            if not self.prepare_environment():
                return False
                
            # 2. 扫描论文
            logging.info("扫描论文目录...")
            papers = self.scan_papers()
            if not papers:
                logging.error("未找到PDF文件")
                return False
                
            logging.info(f"找到 {len(papers)} 篇论文")
            
            # 3. 批量处理
            logging.info("开始批量处理...")
            self.process_batch(papers)
            
            # 4. 生成汇总报告
            logging.info("生成汇总报告...")
            self.generate_summary()
            
            logging.info("批处理完成！")
            return True
            
        except Exception as e:
            logging.error(f"批处理执行失败：{str(e)}")
            return False

def main():
    """工作流4主函数"""
    print("开始执行工作流4：批量分析任务...\n")
    
    try:
        processor = BatchProcessor()
        success = processor.run()
        
        if success:
            print("\n工作流4执行完成！")
            print(f"\n生成的文件：")
            print(f"- 汇总报告：{processor.config['output']['summary_file']}")
            print(f"- 处理日志：{processor.config['output']['log_file']}")
            print(f"- 错误日志：{processor.config['output']['error_log']}")
        
        return success
        
    except Exception as e:
        print(f"工作流执行出错：{str(e)}")
        return False

if __name__ == "__main__":
    main() 