import os
import json
from pathlib import Path
from datetime import datetime

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

class ResultCollector:
    def __init__(self, config_file="config/batch_config.yaml"):
        """初始化结果收集器"""
        self.config = self._load_config(config_file)
        self.results = []
        
    def _load_config(self, config_file):
        """加载配置文件"""
        with open(config_file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
            
    def collect_results(self):
        """收集处理结果"""
        try:
            # 读取批处理结果
            results_file = Path(self.config["report_dir"]) / "batch_results.json"
            with open(results_file, "r", encoding="utf-8") as f:
                self.results = json.load(f)
                
            # 生成汇总报告
            self._generate_summary_report()
            
            # 生成详细报告
            self._generate_detailed_report()
            
            return True
            
        except Exception as e:
            print(f"收集结果时出错: {str(e)}")
            return False
            
    def _generate_summary_report(self):
        """生成汇总报告"""
        output_dir = Path(self.config["report_dir"])
        summary_file = output_dir / "summary_report.md"
        
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write("# 批处理结果汇总报告\n\n")
            f.write(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # 总体统计
            total = len(self.results)
            success = sum(1 for r in self.results if r["status"] == "success")
            failed = total - success
            
            f.write("## 处理统计\n")
            f.write(f"- 总任务数：{total}\n")
            f.write(f"- 成功数量：{success}\n")
            f.write(f"- 失败数量：{failed}\n")
            f.write(f"- 成功率：{(success/total*100):.2f}%\n\n")
            
            # 处理时间统计
            if self.results:
                start_times = [datetime.strptime(r["start_time"], "%Y-%m-%d %H:%M:%S") for r in self.results]
                end_times = [datetime.strptime(r["end_time"], "%Y-%m-%d %H:%M:%S") for r in self.results]
                
                total_duration = max(end_times) - min(start_times)
                avg_duration = sum((end - start).total_seconds() for start, end in zip(start_times, end_times)) / total
                
                f.write("## 时间统计\n")
                f.write(f"- 开始时间：{min(start_times).strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"- 结束时间：{max(end_times).strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"- 总耗时：{total_duration.total_seconds()/3600:.2f} 小时\n")
                f.write(f"- 平均耗时：{avg_duration/60:.2f} 分钟\n\n")
                
            # 失败任务列表
            if failed > 0:
                f.write("## 失败任务\n")
                for result in self.results:
                    if result["status"] == "failed":
                        f.write(f"### 任务 {result['task_id']}\n")
                        f.write(f"- 论文：{result['paper_info']['title']}\n")
                        f.write(f"- 错误：{result['error']}\n\n")
                        
        print(f"汇总报告已生成：{summary_file}")
        
    def _generate_detailed_report(self):
        """生成详细报告"""
        output_dir = Path(self.config["report_dir"])
        detailed_file = output_dir / "detailed_report.md"
        
        with open(detailed_file, "w", encoding="utf-8") as f:
            f.write("# 批处理详细报告\n\n")
            
            for result in self.results:
                f.write(f"## 任务 {result['task_id']}\n")
                f.write(f"### 基本信息\n")
                f.write(f"- 论文：{result['paper_info']['title']}\n")
                f.write(f"- 状态：{result['status']}\n")
                f.write(f"- 开始时间：{result['start_time']}\n")
                f.write(f"- 结束时间：{result['end_time']}\n")
                
                if result["status"] == "success":
                    f.write("\n### 处理步骤\n")
                    for step in result["steps"]:
                        f.write(f"- {step['name']}: {step['status']}\n")
                else:
                    f.write(f"\n### 错误信息\n")
                    f.write(f"```\n{result['error']}\n```\n")
                    
                f.write("\n---\n\n")
                
        print(f"详细报告已生成：{detailed_file}")
        
if __name__ == "__main__":
    # 测试结果收集器
    collector = ResultCollector()
    collector.collect_results() 