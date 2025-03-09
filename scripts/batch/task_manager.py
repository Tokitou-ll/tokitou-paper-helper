import os
import yaml
import json
from pathlib import Path
from datetime import datetime
from queue import Queue
from threading import Thread, Lock
import time

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from scripts.preprocessing.validate_pdf import validate_pdf
from scripts.preprocessing.extract_text import extract_text
from scripts.preprocessing.preprocess_text import preprocess_text
from scripts.analysis.prepare_analysis_rules import prepare_analysis_rules
from scripts.analysis.analyze_paper import analyze_paper

class TaskManager:
    def __init__(self, config_file="config/batch_config.yaml"):
        """初始化任务管理器"""
        self.config = self._load_config(config_file)
        self.task_queue = Queue()
        self.results = []
        self.results_lock = Lock()
        self.workers = []
        
    def _load_config(self, config_file):
        """加载配置文件"""
        with open(config_file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
            
    def add_task(self, paper_info):
        """添加任务到队列"""
        self.task_queue.put(paper_info)
        
    def _process_task(self, task_id):
        """处理单个任务"""
        while True:
            try:
                paper_info = self.task_queue.get_nowait()
            except Queue.Empty:
                break
                
            result = {
                "task_id": task_id,
                "paper_info": paper_info,
                "status": "pending",
                "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "steps": []
            }
            
            try:
                # 1. 验证PDF
                if not validate_pdf(paper_info["pdf_path"]):
                    raise Exception("PDF验证失败")
                result["steps"].append({"name": "validate_pdf", "status": "success"})
                
                # 2. 提取文本
                if not extract_text():
                    raise Exception("文本提取失败")
                result["steps"].append({"name": "extract_text", "status": "success"})
                
                # 3. 预处理文本
                if not preprocess_text():
                    raise Exception("文本预处理失败")
                result["steps"].append({"name": "preprocess_text", "status": "success"})
                
                # 4. 准备分析规则
                if not prepare_analysis_rules():
                    raise Exception("规则准备失败")
                result["steps"].append({"name": "prepare_rules", "status": "success"})
                
                # 5. 分析论文
                if not analyze_paper():
                    raise Exception("论文分析失败")
                result["steps"].append({"name": "analyze_paper", "status": "success"})
                
                result["status"] = "success"
                result["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
            except Exception as e:
                result["status"] = "failed"
                result["error"] = str(e)
                result["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # 如果配置为跳过失败任务
                if self.config.get("skip_on_failure", True):
                    print(f"任务 {task_id} 失败: {str(e)}")
                else:
                    raise e
                    
            finally:
                with self.results_lock:
                    self.results.append(result)
                self.task_queue.task_done()
                
    def start(self):
        """启动任务处理"""
        num_workers = self.config.get("parallel_tasks", 2)
        
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
        
    def _save_results(self):
        """保存处理结果"""
        output_dir = Path(self.config["report_dir"])
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存JSON结果
        results_file = output_dir / "batch_results.json"
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=4)
            
        # 生成Markdown报告
        report_file = output_dir / "batch_report.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("# 批处理分析报告\n\n")
            
            # 总体统计
            total = len(self.results)
            success = sum(1 for r in self.results if r["status"] == "success")
            failed = total - success
            
            f.write("## 处理概要\n")
            f.write(f"- 总任务数：{total}\n")
            f.write(f"- 成功：{success}\n")
            f.write(f"- 失败：{failed}\n\n")
            
            # 详细结果
            f.write("## 详细结果\n")
            for result in self.results:
                f.write(f"\n### 任务 {result['task_id']}\n")
                f.write(f"- 论文：{result['paper_info']['title']}\n")
                f.write(f"- 状态：{result['status']}\n")
                f.write(f"- 开始时间：{result['start_time']}\n")
                f.write(f"- 结束时间：{result['end_time']}\n")
                
                if result["status"] == "failed":
                    f.write(f"- 错误：{result['error']}\n")
                else:
                    f.write("\n处理步骤：\n")
                    for step in result["steps"]:
                        f.write(f"- {step['name']}: {step['status']}\n")
                        
        print(f"\n批处理完成！")
        print(f"结果文件：{results_file}")
        print(f"报告文件：{report_file}")
        
if __name__ == "__main__":
    # 测试任务管理器
    manager = TaskManager()
    
    # 添加测试任务
    test_papers = [
        {
            "title": "测试论文1",
            "pdf_path": "data/test/paper1.pdf"
        },
        {
            "title": "测试论文2",
            "pdf_path": "data/test/paper2.pdf"
        }
    ]
    
    for paper in test_papers:
        manager.add_task(paper)
        
    # 启动处理
    manager.start() 