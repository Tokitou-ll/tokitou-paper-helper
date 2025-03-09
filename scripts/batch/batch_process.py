import os
import yaml
import json
from pathlib import Path
from datetime import datetime
from queue import Queue, Empty
from threading import Thread, Lock
import time
import urllib.parse

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from scripts.preprocessing.validate_pdf import validate_pdf
from scripts.preprocessing.extract_text import extract_text
from scripts.preprocessing.preprocess_text import preprocess_text
from scripts.analysis.prepare_analysis_rules import prepare_analysis_rules
from scripts.analysis.analyze_paper import analyze_paper
from scripts.utils.cleanup import cleanup_temp_files

class BatchProcessor:
    def __init__(self, config_file="config/batch_config.yaml", path_config_file="config/path_config.yaml"):
        """初始化批处理器"""
        self.config = self._load_config(config_file)
        self.path_config = self._load_config(path_config_file)
        self.task_queue = Queue()
        self.results = []
        self.results_lock = Lock()
        self.workers = []
        self.task_counter = 0
        self.task_counter_lock = Lock()
        
    def _load_config(self, config_file):
        """加载配置文件"""
        with open(config_file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
            
    def scan_pdf_directory(self):
        """扫描PDF目录，获取所有PDF文件"""
        pdf_dir = Path(self.path_config["directories"]["papers"])
        if not pdf_dir.exists():
            raise Exception(f"PDF目录不存在：{pdf_dir}")
            
        pdf_files = []
        for file in pdf_dir.glob("*.pdf"):
            # 对文件路径进行编码，处理空格问题
            encoded_path = str(file).replace(" ", "%20")
            pdf_files.append({
                "title": file.stem,
                "pdf_path": str(file),
                "encoded_path": encoded_path,
                "file_size": file.stat().st_size / (1024 * 1024),  # 转换为MB
                "last_modified": datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            })
            
        return sorted(pdf_files, key=lambda x: x["title"])
            
    def add_task(self, paper_info):
        """添加任务到队列"""
        self.task_queue.put(paper_info)
        
    def get_next_task_id(self):
        """获取下一个任务ID"""
        with self.task_counter_lock:
            task_id = self.task_counter
            self.task_counter += 1
            return task_id
            
    def _process_task(self, worker_id):
        """处理单个任务"""
        while True:
            try:
                paper_info = self.task_queue.get_nowait()
            except Empty:
                break
                
            task_id = self.get_next_task_id()
            result = {
                "task_id": task_id,
                "worker_id": worker_id,
                "file_info": {
                    "title": paper_info["title"],
                    "pdf_path": paper_info["pdf_path"],
                    "file_size": paper_info["file_size"],
                    "last_modified": paper_info["last_modified"]
                },
                "status": "pending",
                "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "steps": []
            }
            
            try:
                print(f"\n开始处理论文：{paper_info['title']}")
                print(f"文件信息：")
                print(f"- 路径：{paper_info['pdf_path']}")
                print(f"- 大小：{paper_info['file_size']:.2f} MB")
                print(f"- 修改时间：{paper_info['last_modified']}")
                
                # 1. 验证PDF
                if not validate_pdf(paper_info["pdf_path"]):
                    raise Exception("PDF验证失败")
                result["steps"].append({"name": "validate_pdf", "status": "success"})
                print("PDF验证成功")
                
                # 2. 提取文本
                if not extract_text(paper_info["pdf_path"]):
                    raise Exception("文本提取失败")
                result["steps"].append({"name": "extract_text", "status": "success"})
                print("文本提取成功")
                
                # 3. 预处理文本
                text_file = "output/analysis/text/extracted_text.txt"
                if not preprocess_text(text_file):
                    raise Exception("文本预处理失败")
                result["steps"].append({"name": "preprocess_text", "status": "success"})
                print("文本预处理成功")
                
                # 4. 准备分析规则
                rules_dir = Path("output/analysis/rules")
                if not prepare_analysis_rules(str(rules_dir)):
                    raise Exception("规则准备失败")
                result["steps"].append({"name": "prepare_rules", "status": "success"})
                print("规则准备成功")
                
                # 5. 分析论文
                text_file = "output/analysis/text/preprocessed_text.txt"
                rules_file = "output/analysis/rules/analysis_rules.json"
                output_dir = "output/analysis/report"
                analysis_results = analyze_paper(text_file=text_file, rules_file=rules_file, output_dir=output_dir)
                if not analysis_results:
                    raise Exception("论文分析失败")
                result["steps"].append({"name": "analyze_paper", "status": "success"})
                result["analysis_results"] = analysis_results
                print("论文分析成功")
                
                result["status"] = "success"
                result["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"论文处理完成：{paper_info['title']}")
                
            except Exception as e:
                result["status"] = "failed"
                result["error"] = str(e)
                result["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"处理论文时出错: {str(e)}")
                
                # 如果配置为跳过失败任务
                if self.config.get("error_handling", {}).get("skip_on_failure", True):
                    print(f"跳过失败的任务 {task_id}")
                else:
                    raise e
                    
            finally:
                with self.results_lock:
                    self.results.append(result)
                self.task_queue.task_done()
                
    def start(self):
        """启动任务处理"""
        num_workers = self.config.get("batch", {}).get("parallel_tasks", 2)
        
        # 创建工作线程
        for i in range(num_workers):
            worker = Thread(target=self._process_task, args=(i,))
            worker.daemon = True
            worker.start()
            self.workers.append(worker)
            
        # 等待所有任务完成
        self.task_queue.join()
        
        # 保存结果
        self._save_results()
        
    def _process_single_file(self, pdf_file):
        """处理单个PDF文件"""
        try:
            # 获取文件信息
            file_info = self._get_file_info(pdf_file)
            print(f"\n开始处理论文：{file_info['title']}")
            print("文件信息：")
            print(f"- 路径：{file_info['pdf_path']}")
            print(f"- 大小：{file_info['file_size']:.2f} MB")
            print(f"- 修改时间：{file_info['last_modified']}")
            
            # 1. 验证PDF文件
            if not validate_pdf(file_info['pdf_path']):
                raise Exception("PDF验证失败")
            print("PDF验证成功")
            
            # 2. 提取文本
            text_file = Path("output/analysis/text/extracted_text.txt")
            if not extract_text(file_info['pdf_path']):
                raise Exception("文本提取失败")
            print("文本提取成功")
            
            # 3. 预处理文本
            preprocessed_text_file = Path("output/analysis/text/preprocessed_text.txt")
            if not preprocess_text(text_file):
                raise Exception("文本预处理失败")
            print("文本预处理成功")
            
            # 4. 准备分析规则
            rules_dir = Path("output/analysis/rules")
            if not prepare_analysis_rules(str(rules_dir)):
                raise Exception("规则准备失败")
            print("规则准备成功")
            
            # 5. 分析论文
            output_dir = Path("output/analysis/report")
            results = analyze_paper(str(preprocessed_text_file), str(rules_dir / "analysis_rules.json"), str(output_dir))
            if not results:
                raise Exception("论文分析失败")
            print("论文分析成功")
            
            print(f"论文处理完成：{file_info['title']}\n")
            
            return {
                "status": "success",
                "file_info": file_info,
                "results": results
            }
            
        except Exception as e:
            print(f"处理论文时出错: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "file_info": self._get_file_info(pdf_file)
            }

    def _generate_summary_table(self, results):
        """生成论文分析结果汇总表格。
        
        Args:
            results: 分析结果列表
        
        Returns:
            str: Markdown格式的表格
        """
        # 表格头部
        table = "| 论文标题 | 文件大小 | 修改时间 | 实现类型 | 置信度 | 代码链接 | 关键证据 |\n"
        table += "| --- | --- | --- | --- | --- | --- | --- |\n"
        
        # 实现类型映射
        impl_type_map = {
            "official": "官方实现",
            "unofficial": "非官方实现",
            "unknown": "未知"
        }
        
        # 置信度映射
        confidence_map = {
            "high": "高",
            "medium": "中",
            "low": "低",
            "unknown": "未知"
        }
        
        # 添加每个论文的结果
        for result in results:
            if result["status"] == "success":
                # 获取文件信息
                file_info = result.get("file_info", {})
                
                # 获取分析结果
                analysis_results = result.get("analysis_results", {})
                implementation = analysis_results.get("implementation", {})
                
                # 提取信息
                title = file_info.get("title", "未知")
                file_size = f"{file_info.get('file_size', 0):.2f} MB"
                mod_time = file_info.get("last_modified", "未知")
                impl_type = impl_type_map.get(implementation.get("type", "unknown"), "未知")
                confidence = confidence_map.get(implementation.get("confidence", "unknown"), "未知")
                code_url = implementation.get("code_url", "无")
                evidence = implementation.get("evidence", [])
                
                # 格式化证据
                evidence_str = "; ".join(evidence[:2]) if evidence else "无"
                if len(evidence_str) > 100:
                    evidence_str = evidence_str[:97] + "..."
                
                # 添加到表格
                table += f"| {title} | {file_size} | {mod_time} | {impl_type} | {confidence} | {code_url} | {evidence_str} |\n"
            else:
                # 处理失败的情况
                file_info = result.get("file_info", {})
                title = file_info.get("title", "未知")
                file_size = f"{file_info.get('file_size', 0):.2f} MB"
                mod_time = file_info.get("last_modified", "未知")
                table += f"| {title} | {file_size} | {mod_time} | 处理失败 | - | - | {result.get('error', '未知错误')} |\n"
                
        return table

    def _save_results(self):
        """保存批处理结果"""
        try:
            # 创建输出目录
            output_dir = Path("output/analysis/report/batch")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 准备结果数据
            end_time = datetime.now()
            start_time = min(r["start_time"] for r in self.results) if self.results else "未知"
            
            # 计算总耗时（分钟）
            if start_time != "未知":
                start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                total_duration = (end_time - start_dt).total_seconds() / 60
            else:
                total_duration = 0
                
            # 计算平均耗时（秒）
            successful_tasks = [r for r in self.results if r["status"] == "success"]
            if successful_tasks:
                avg_duration = total_duration * 60 / len(successful_tasks)
            else:
                avg_duration = 0
                
            # 构建结果字典
            batch_results = {
                "start_time": start_time,
                "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_duration": total_duration,
                "avg_duration": avg_duration,
                "total_tasks": len(self.results),
                "successful_tasks": len(successful_tasks),
                "failed_tasks": len(self.results) - len(successful_tasks),
                "tasks": self.results
            }
            
            # 保存JSON结果
            results_file = output_dir / "batch_results.json"
            with open(results_file, "w", encoding="utf-8") as f:
                json.dump(batch_results, f, ensure_ascii=False, indent=2)
                
            # 生成报告
            report = self._generate_batch_report(batch_results)
            report_file = output_dir / "batch_report.md"
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(report)
                
            print("\n批处理完成！")
            print(f"结果文件：{results_file}")
            print(f"报告文件：{report_file}")
            
            # 清理临时文件
            cleanup_temp_files()
            print("\n清理完成！")
            
        except Exception as e:
            print(f"保存结果时出错：{str(e)}")
            raise
            
    def _generate_batch_report(self, results):
        """生成批处理报告。
        
        Args:
            results (dict): 批处理结果字典
        
        Returns:
            str: Markdown格式的报告
        """
        # 生成报告头部
        report = [
            "# 批处理分析报告",
            f"\n生成时间：{results['end_time']}",
            "\n## 处理概要",
            f"- 总任务数：{results['total_tasks']}",
            f"- 成功：{results['successful_tasks']}",
            f"- 失败：{results['failed_tasks']}",
            f"- 成功率：{(results['successful_tasks'] / results['total_tasks'] * 100):.2f}%",
            "\n## 时间统计",
            f"- 开始时间：{results['start_time']}",
            f"- 结束时间：{results['end_time']}",
            f"- 总耗时：{results['total_duration']:.2f} 分钟",
            f"- 平均耗时：{results['avg_duration']:.2f} 秒",
            "\n## 论文分析汇总"
        ]
        
        # 添加结果表格
        report.append(self._generate_summary_table(results["tasks"]))
        
        return "\n".join(report)

    def _get_file_info(self, pdf_file):
        """获取文件信息"""
        return {
            "title": pdf_file.stem,
            "path": str(pdf_file),
            "size": f"{pdf_file.stat().st_size / (1024*1024):.2f} MB",
            "modified": datetime.fromtimestamp(pdf_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        }

def main():
    """主函数"""
    try:
        # 清理临时文件
        if not cleanup_temp_files():
            raise Exception("清理临时文件失败")
            
        # 创建批处理器
        processor = BatchProcessor()
        
        # 扫描PDF目录
        pdf_files = processor.scan_pdf_directory()
        print(f"找到 {len(pdf_files)} 篇待处理论文")
        
        # 添加任务到队列
        for paper in pdf_files:
            processor.add_task(paper)
            
        # 启动处理
        processor.start()
        
        return True
        
    except Exception as e:
        print(f"批处理过程中出错: {str(e)}")
        return False
        
if __name__ == "__main__":
    main()