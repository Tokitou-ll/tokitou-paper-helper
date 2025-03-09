import json
import os
from datetime import datetime

def normalize_title(title):
    # 移除文件扩展名和路径
    title = os.path.splitext(os.path.basename(title))[0]
    return title

def load_analysis_results():
    """加载分析结果"""
    results = []
    batch_results_file = "output/analysis/report/batch/batch_results.json"
    analysis_results_file = "output/analysis/report/analysis_results.json"
    
    if os.path.exists(batch_results_file):
        with open(batch_results_file, "r", encoding="utf-8") as f:
            batch_results = json.load(f)
            
        # 首先加载所有批处理结果
        for result in batch_results:
            new_result = {
                "paper_info": result["paper_info"],
                "steps": result["steps"],
                "status": result["status"]
            }
            results.append(new_result)
    
    # 如果存在分析结果文件，将其作为第一个论文的分析结果
    if os.path.exists(analysis_results_file):
        with open(analysis_results_file, "r", encoding="utf-8") as f:
            analysis_result = json.load(f)
            if results:
                results[0]["analysis_result"] = analysis_result
    
    return results

def normalize_spaces(lines):
    # 规范化空行：确保段落之间只有一个空行
    normalized = []
    prev_empty = False
    for line in lines:
        is_empty = not line.strip()
        if not (is_empty and prev_empty):
            normalized.append(line)
        prev_empty = is_empty
    return normalized

def extract_title_from_path(file_path):
    # 从文件路径中提取论文标题
    return os.path.splitext(os.path.basename(file_path))[0]

def format_step_name(step):
    # 格式化步骤名称
    step_names = {
        "validate_pdf": "PDF 文件验证",
        "extract_text": "PDF 文本提取",
        "preprocess_text": "文本预处理",
        "prepare_rules": "规则准备",
        "analyze_paper": "论文分析"
    }
    return step_names.get(step, step)

def calculate_progress(analysis_results):
    """计算分析进度"""
    total_papers = len(analysis_results)
    if total_papers == 0:
        return {
            "total": 0,
            "completed": 0,
            "in_progress": 0,
            "pending": 0,
            "completion_rate": 0
        }
    
    completed = sum(1 for r in analysis_results if r["status"] == "success")
    in_progress = sum(1 for r in analysis_results if r["status"] == "pending")
    pending = total_papers - completed - in_progress
    
    return {
        "total": total_papers,
        "completed": completed,
        "in_progress": in_progress,
        "pending": pending,
        "completion_rate": (completed / total_papers * 100)
    }

def get_implementation_type(result):
    """获取代码实现类型和置信度"""
    if not isinstance(result, dict):
        return "未知", "低"
        
    # 如果有分析结果，使用分析结果中的实现类型
    if 'analysis_result' in result and isinstance(result['analysis_result'], dict):
        implementation = result['analysis_result'].get('implementation', {})
        if implementation:
            impl_type = implementation.get('type', '未知')
            confidence = implementation.get('confidence', '低')
            
            # 转换类型为中文
            type_map = {
                'official': '官方实现',
                'unofficial': '非官方实现',
                'unknown': '未知'
            }
            confidence_map = {
                'high': '高',
                'medium': '中',
                'low': '低'
            }
            
            return type_map.get(impl_type, impl_type), confidence_map.get(confidence, confidence)
    
    # 如果没有分析结果，根据步骤完成情况判断
    steps = result.get('steps', [])
    if not steps:
        return "未知", "低"
        
    all_steps_completed = all(
        any(step['name'] == name and step['status'] == 'success' 
            for step in steps)
        for name in ['validate_pdf', 'extract_text', 'preprocess_text', 'prepare_rules', 'analyze_paper']
    )
    
    if all_steps_completed:
        return "可能是官方实现", "中"
    else:
        return "未知", "低"

def get_paper_info(result):
    """获取论文的作者和机构信息"""
    if not isinstance(result, dict):
        return {
            'authors': '[论文中未明确列出]',
            'institutions': '[论文中未明确列出]'
        }
        
    # 如果有分析结果，从中提取信息
    if 'analysis_result' in result and isinstance(result['analysis_result'], dict):
        paper_info = result['analysis_result'].get('paper_info', {})
        return {
            'authors': '; '.join(paper_info.get('authors', [])) or '[论文中未明确列出]',
            'institutions': '; '.join(paper_info.get('institutions', [])) or '[论文中未明确列出]'
        }
    
    # 如果没有分析结果，返回默认值
    return {
        'authors': '[论文中未明确列出]',
        'institutions': '[论文中未明确列出]'
    }

def get_key_findings(result):
    """获取论文的关键发现"""
    if not isinstance(result, dict):
        return "- 分析完成，等待更新关键发现"
        
    findings = []
    
    if 'analysis_result' in result and isinstance(result['analysis_result'], dict):
        innovation = result['analysis_result'].get('innovation', {})
        implementation = result['analysis_result'].get('implementation', {})
        
        # 添加代码实现相关的发现
        if implementation:
            if implementation.get('code_url'):
                findings.append(f"代码实现：提供了代码仓库 {implementation['code_url']}")
            if implementation.get('evidence'):
                findings.extend([f"实现证据：{e}" for e in implementation['evidence'][:2]])  # 只显示前两条证据
        
        # 添加创新点相关的发现
        if innovation:
            if innovation.get('novel_methods'):
                findings.extend([f"创新方法：{m}" for m in innovation['novel_methods'][:2]])
            if innovation.get('improvements'):
                findings.extend([f"改进点：{i}" for i in innovation['improvements'][:2]])
    
    # 如果没有找到具体发现，返回默认值
    if not findings:
        findings = ["分析完成，等待更新关键发现"]
    
    return "\n".join(f"- {finding}" for finding in findings)

def format_update_record(record):
    """格式化更新记录"""
    lines = record.strip().split("\n")
    if not lines:
        return ""
    
    # 提取时间和内容
    header = lines[0]  # 包含时间的行
    content = lines[1:]  # 更新内容
    
    # 确保内容的每一行都有正确的缩进
    formatted_content = []
    for line in content:
        if line.strip():
            if not line.startswith("- "):
                line = "- " + line
            formatted_content.append(line)
    
    # 组合格式化后的记录
    return header + "\n" + "\n".join(formatted_content)

def update_paper_summary():
    # 加载分析结果
    analysis_results = load_analysis_results()
    if not analysis_results:
        print("未找到分析结果！")
        return
    
    # 读取现有的汇总文件
    summary_file = "output/paper_summary.md"
    if os.path.exists(summary_file):
        with open(summary_file, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        content = "# 论文汇总\n\n本文档汇总了 data/test 目录下的所有论文信息。\n"

    # 分割内容为不同部分
    sections = {}
    current_section = "header"
    current_content = []
    
    for line in content.split("\n"):
        if line.startswith("## "):
            sections[current_section] = "\n".join(current_content)
            current_section = line[3:].strip()
            current_content = [line]
        else:
            current_content.append(line)
    sections[current_section] = "\n".join(current_content)

    # 更新统计信息部分
    total_size = sum(float(result['paper_info'].get('file_size', 0)) for result in analysis_results if isinstance(result, dict))
    stats_section = f"""## 统计信息

- 总文件数：{len(analysis_results)} 个
- 总文件大小：{total_size:.1f}MB
- 更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    # 更新注意事项部分
    notes_section = """## 注意事项

1. 目录中存在两个相似的 GazeDiff 相关论文，可能需要确认是否为重复文件
2. 所有论文都与医学影像生成相关，特别是 MRI 和 diffusion model
3. 所有文件都是在 2024-01-03 上传的
4. 所有文件都存放在项目的 data/test 目录下
"""

    # 计算分析进度
    completed = sum(1 for r in analysis_results if isinstance(r, dict) and r.get('status') == 'success')
    in_progress = sum(1 for r in analysis_results if isinstance(r, dict) and r.get('status') == 'pending')
    total = len(analysis_results)
    pending = total - completed - in_progress
    completion_rate = (completed / total * 100) if total > 0 else 0

    # 生成分析进度统计
    progress_section = f"""## 分析进度统计

- 总论文数：{total} 篇
- 已完成：{completed} 篇
- 进行中：{in_progress} 篇
- 待分析：{pending} 篇
- 完成率：{completion_rate:.1f}%
"""

    # 生成论文分析部分
    papers_section = []
    implementation_results = []
    
    for i, result in enumerate(analysis_results, 1):
        if not isinstance(result, dict):
            continue
            
        paper_info = result.get('paper_info', {})
        title = paper_info.get('title', '未知标题')
        
        # 获取实现类型和置信度
        impl_type, confidence = get_implementation_type(result)
        implementation_results.append({
            "title": title,
            "type": impl_type,
            "confidence": confidence
        })
        
        # 获取作者和机构信息
        author_info = get_paper_info(result)
        
        paper_section = f"""### {i}. {title}

#### 基本信息
- 作者：{author_info['authors']}
- 机构：{author_info['institutions']}"""

        paper_section += f"""

#### 代码实现
- 类型：{impl_type}
- 置信度：{confidence}"""

        # 添加关键发现
        paper_section += "\n\n#### 关键发现\n"
        paper_section += get_key_findings(result)
        
        # 添加分析步骤的状态
        paper_section += "\n\n#### 分析状态"
        steps = result.get('steps', [])
        for step_name in ['validate_pdf', 'extract_text', 'preprocess_text', 'prepare_rules', 'analyze_paper']:
            status = '✓' if any(isinstance(step, dict) and step.get('name') == step_name and step.get('status') == 'success' for step in steps) else ' '
            paper_section += f"\n- [{status}] {format_step_name(step_name)}"
        
        papers_section.append(paper_section)

    # 生成代码实现分析结果
    implementation_section = "## 代码实现分析结果\n\n"
    if implementation_results:
        implementation_section += "| 序号 | 论文标题 | 实现类型 | 置信度 |\n"
        implementation_section += "|------|----------|----------|----------|\n"
        for i, result in enumerate(implementation_results, 1):
            implementation_section += f"| {i} | {result['title']} | {result['type']} | {result['confidence']} |\n"
    else:
        implementation_section += "等待分析完成后更新..."

    # 生成更新记录
    update_record = f"""### {datetime.now().strftime('%Y-%m-%d %H:%M')}
- 更新了 {len(analysis_results)} 篇论文的分析状态
- 完成了 {completed} 篇论文的分析
- 当前完成率：{completion_rate:.1f}%
- 更新了论文的作者和机构信息
- 更新了代码实现分析结果
- 添加了关键发现内容"""

    # 保持已有的更新记录
    update_section = "## 更新记录\n\n" + format_update_record(update_record)
    if "更新记录" in sections:
        old_records = sections["更新记录"].split("\n\n")[1:]  # 跳过标题
        if old_records:
            formatted_records = []
            for record in old_records:
                if record.strip():
                    formatted_records.append(format_update_record(record))
            if formatted_records:
                update_section += "\n\n" + "\n\n".join(formatted_records)

    # 组合新内容
    new_content = [
        "# 论文汇总\n\n本文档汇总了 data/test 目录下的所有论文信息。\n",
        stats_section,
        notes_section,
        progress_section,
        "## 论文分析结果\n",
        "\n\n".join(papers_section),
        "\n" + implementation_section,
        update_section
    ]

    # 写入更新后的内容
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write("\n".join(normalize_spaces(new_content)))
    
    print("汇总文件更新完成！")

if __name__ == "__main__":
    update_paper_summary() 