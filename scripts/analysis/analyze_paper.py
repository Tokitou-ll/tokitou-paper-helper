import os
import json
import re
from pathlib import Path
from datetime import datetime

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

def load_rules(rules_file):
    """加载分析规则"""
    with open(rules_file, "r", encoding="utf-8") as f:
        return json.load(f)

def find_code_blocks(text, rules):
    """查找代码块"""
    code_blocks = []
    
    # 使用规则中定义的模式查找代码块
    for pattern in rules["code_analysis"]["patterns"]:
        matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
        for match in matches:
            code_blocks.append({
                "content": match.group(0),
                "start": match.start(),
                "end": match.end()
            })
    
    # 使用关键词查找可能包含代码的段落
    for keyword in rules["code_analysis"]["keywords"]:
        pattern = f"[^.]*{keyword}[^.]*\."
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            code_blocks.append({
                "content": match.group(0),
                "start": match.start(),
                "end": match.end()
            })
    
    return code_blocks

def analyze_implementation_type(code_blocks, rules):
    """分析代码实现类型"""
    # 定义判断标准
    official_indicators = [
        r"official.*implementation",
        r"our.*implementation",
        r"we.*implement",
        r"our.*code",
        r"code.*available",
        r"github\.com",
        r"source.*code",
        r"implementation.*details"
    ]
    
    unofficial_indicators = [
        r"unofficial.*implementation",
        r"third.party.*implementation",
        r"reimplementation",
        r"reproduce"
    ]
    
    # 初始化计数器
    official_count = 0
    unofficial_count = 0
    evidence = []
    code_url = None
    
    # 分析每个代码块
    for block in code_blocks:
        content = block["content"].lower()
        
        # 检查是否包含代码链接
        urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', content)
        if urls and not code_url:
            code_url = urls[0]
        
        # 检查官方实现指标
        for indicator in official_indicators:
            if re.search(indicator, content, re.IGNORECASE):
                official_count += 1
                evidence.append(content.strip())
                break
                
        # 检查非官方实现指标
        for indicator in unofficial_indicators:
            if re.search(indicator, content, re.IGNORECASE):
                unofficial_count += 1
                evidence.append(content.strip())
                break
    
    # 根据证据确定类型和置信度
    if official_count > unofficial_count:
        impl_type = "official"
        confidence = "high" if official_count >= 2 else "medium"
    elif unofficial_count > 0:
        impl_type = "unofficial"
        confidence = "high" if unofficial_count >= 2 else "medium"
    else:
        impl_type = "unknown"
        confidence = "low"
    
    return {
        "type": impl_type,
        "confidence": confidence,
        "code_url": code_url,
        "evidence": evidence[:3]  # 只保留前三条证据
    }

def extract_paper_info(text):
    """从文本中提取论文的基本信息。
    
    Args:
        text (str): 预处理后的论文文本
        
    Returns:
        dict: 包含标题、作者和机构信息的字典
    """
    info = {
        "title": None,
        "authors": [],
        "institutions": []
    }
    
    try:
        # 按段落分割文本
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        
        # 提取标题（通常是第一段，但需要排除一些特殊情况）
        title_blacklist = [
            'abstract', 'introduction', 'keywords', 'arxiv', 'copyright', 
            'http', 'www', 'submitted', 'received', 'accepted', 'published',
            'ieee', 'acm', 'proceedings', 'conference', 'journal', 'fig',
            'table', 'figure', 'algorithm', 'appendix', 'supplementary',
            'references', 'acknowledgments', 'conclusion', 'discussion',
            'email', 'address', 'tel', 'fax', 'corresponding'
        ]
        
        # 标题特征
        title_features = [
            lambda p: len(p.split()) >= 3 and len(p.split()) <= 40,  # 合理的单词数
            lambda p: not any(word.lower() in p.lower() for word in title_blacklist),  # 不包含黑名单词
            lambda p: not p.startswith('http'),  # 不是URL
            lambda p: not re.match(r'^[0-9\.\s]+$', p),  # 不全是数字和点
            lambda p: len(p) >= 10 and len(p) <= 500  # 合理的长度
        ]
        
        # 在前5段中寻找标题
        for p in paragraphs[:5]:
            # 清理段落文本
            p = p.strip()
            p = re.sub(r'\s+', ' ', p)  # 规范化空格
            p = re.sub(r'\d+$', '', p)  # 移除末尾数字
            p = re.sub(r'[\r\n]+', ' ', p)  # 移除换行符
            p = re.sub(r'\s*\([^)]*\)', '', p)  # 移除括号及其内容
            p = re.sub(r'\s*\[[^\]]*\]', '', p)  # 移除方括号及其内容
            
            # 检查标题特征
            if all(feature(p) for feature in title_features):
                info["title"] = p
                break
        
        # 提取作者（通常在标题后的1-3段）
        author_patterns = [
            # 标准作者名模式（名字 姓氏）
            r'([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)',
            # 带中间名缩写的作者名
            r'([A-Z][a-zA-Z]+\s+[A-Z]\.?\s+[A-Z][a-zA-Z]+)',
            # 带连字符的作者名
            r'([A-Z][a-zA-Z]+(?:-[A-Z][a-zA-Z]+)+)',
            # 带上标的作者名（移除上标）
            r'([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\s*[\d,\*†‡§]+',
            # 带括号的作者名
            r'([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\s*\([^)]+\)',
            # 带逗号分隔的作者名
            r'([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*),\s*(?:and\s+)?[A-Z]'
        ]
        
        # 作者名黑名单词和模式
        author_blacklist = [
            'abstract', 'introduction', 'university', 'department', 'institute',
            'keywords', 'corresponding', 'author', 'email', 'address', 'tel',
            'fax', 'http', 'www', 'fig', 'figure', 'table', 'algorithm',
            'appendix', 'supplementary', 'et al', 'ieee', 'copyright',
            'related', 'work', 'proposed', 'method', 'results', 'discussion',
            'conclusion', 'references', 'acknowledgments', 'background',
            'materials', 'methods', 'experimental', 'setup', 'implementation'
        ]
        
        # 作者名验证函数
        def is_valid_author(name):
            if not name or len(name) < 4:
                return False
            
            # 检查黑名单词
            if any(word in name.lower() for word in author_blacklist):
                return False
                
            # 检查长度和单词数
            words = name.split()
            if len(words) < 2 or len(words) > 5:
                return False
                
            # 检查每个单词的格式
            for word in words:
                if not word[0].isupper():
                    return False
                    
            # 检查是否包含常见的非作者词
            common_words = ['the', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'of', 'with']
            if any(word.lower() in common_words for word in words):
                return False
                
            return True
        
        # 在前5段中查找作者
        author_candidates = []
        for p in paragraphs[1:6]:  # 从第二段开始，因为第一段通常是标题
            # 跳过包含黑名单词的段落
            if any(word in p.lower() for word in author_blacklist):
                continue
                
            for pattern in author_patterns:
                matches = re.finditer(pattern, p)
                for match in matches:
                    author = match.group(1).strip()
                    # 清理作者名中的特殊字符
                    author = re.sub(r'[\d,\*†‡§\(\)\[\]]+', '', author)
                    author = re.sub(r'\s+', ' ', author)
                    author = author.strip()
                    
                    if is_valid_author(author) and author not in author_candidates:
                        author_candidates.append(author)
        
        # 对作者候选列表进行过滤和排序
        if author_candidates:
            # 按长度排序（通常较短的更可能是真实作者名）
            author_candidates.sort(key=len)
            # 取前10个作者
            info["authors"] = author_candidates[:10]
        
        # 提取机构（通常在作者后的1-3段）
        institution_patterns = [
            # 大学
            r'(?:Department|School|Faculty|College|Division)\s+of\s+[^,\n]+(?:,\s*[^,\n]+(?:University|Institute)[^,\n]*)?',
            # 研究所
            r'(?:Institute|Laboratory|Center|Centre)\s+(?:of|for)\s+[^,\n]+(?:,\s*[^,\n]+(?:University|Institute)[^,\n]*)?',
            # 医院
            r'[^,\n]+\s+Hospital[^,\n]*(?:,\s*[^,\n]+(?:University|Medical|Center)[^,\n]*)?',
            # 公司
            r'[^,\n]+\s+(?:Corporation|Corp\.|Inc\.|Ltd\.|LLC)[^,\n]*',
            # 大学（简单模式）
            r'[A-Z][a-zA-Z\s]+University[^,\n]*',
            # 研究中心（简单模式）
            r'[A-Z][a-zA-Z\s]+(?:Research|Medical)\s+Center[^,\n]*'
        ]
        
        # 机构名验证函数
        def clean_institution(inst):
            # 移除多余空格
            inst = re.sub(r'\s+', ' ', inst)
            # 移除末尾的标点
            inst = re.sub(r'[,;\.]$', '', inst)
            # 移除引用标记
            inst = re.sub(r'\[\d+\]', '', inst)
            # 移除电子邮件地址
            inst = re.sub(r'\S+@\S+', '', inst)
            # 移除括号及其内容
            inst = re.sub(r'\s*\([^)]*\)', '', inst)
            return inst.strip()
        
        # 在前10段中查找机构
        institution_candidates = []
        for p in paragraphs[:10]:
            for pattern in institution_patterns:
                matches = re.finditer(pattern, p)
                for match in matches:
                    institution = clean_institution(match.group())
                    if (len(institution) > 10 and  # 机构名不能太短
                        institution not in institution_candidates):
                        institution_candidates.append(institution)
        
        # 对机构候选列表进行过滤和排序
        if institution_candidates:
            # 按长度排序（通常较长的更可能是完整的机构名）
            institution_candidates.sort(key=len, reverse=True)
            # 取前5个机构
            info["institutions"] = institution_candidates[:5]
        
    except Exception as e:
        print(f"提取论文信息时出错: {str(e)}")
    
    return info

def analyze_code_implementation(text, rules_file):
    """
    分析论文中的代码实现类型
    """
    # 加载分析规则
    rules = load_rules(rules_file)
    if not rules:
        return None
        
    result = {
        "type": "unknown",  # 可能的值: official, unofficial, unknown
        "confidence": "low",  # 可能的值: high, medium, low
        "code_url": None,
        "evidence": []
    }
    
    try:
        # 按段落分割文本
        paragraphs = text.split("\n\n")
        
        # 计数器
        official_count = 0
        unofficial_count = 0
        
        # 收集证据
        official_evidence = []
        unofficial_evidence = []
        
        # 查找代码链接
        code_patterns = [
            r"https?://github\.com/[^\s\)]+",
            r"https?://gitlab\.com/[^\s\)]+",
            r"https?://bitbucket\.org/[^\s\)]+",
            r"https?://code\.google\.com/[^\s\)]+",
            r"https?://sourceforge\.net/[^\s\)]+",
            r"https?://huggingface\.co/[^\s\)]+",
            r"https?://paperswithcode\.com/[^\s\)]+",
            r"https?://zenodo\.org/[^\s\)]+",
            r"https?://figshare\.com/[^\s\)]+",
            r"https?://drive\.google\.com/[^\s\)]+",
            r"https?://dropbox\.com/[^\s\)]+",
            r"https?://onedrive\.live\.com/[^\s\)]+",
            r"https?://box\.com/[^\s\)]+",
            r"https?://mega\.nz/[^\s\)]+",
            r"https?://colab\.research\.google\.com/[^\s\)]+",
            r"https?://kaggle\.com/[^\s\)]+",
            r"https?://wandb\.ai/[^\s\)]+",
            r"https?://neptune\.ai/[^\s\)]+",
            r"https?://mlflow\.org/[^\s\)]+",
            r"https?://dvc\.org/[^\s\)]+",
            r"https?://weights\.biases\.com/[^\s\)]+",
            r"https?://tensorboard\.dev/[^\s\)]+",
            r"https?://tensorboard\.org/[^\s\)]+",
            r"https?://tensorflow\.org/[^\s\)]+",
            r"https?://pytorch\.org/[^\s\)]+",
            r"https?://keras\.io/[^\s\)]+",
            r"https?://scikit-learn\.org/[^\s\)]+",
            r"https?://scipy\.org/[^\s\)]+",
            r"https?://numpy\.org/[^\s\)]+",
            r"https?://pandas\.pydata\.org/[^\s\)]+",
            r"https?://matplotlib\.org/[^\s\)]+",
            r"https?://seaborn\.pydata\.org/[^\s\)]+",
            r"https?://plotly\.com/[^\s\)]+",
            r"https?://bokeh\.org/[^\s\)]+",
            r"https?://dash\.plotly\.com/[^\s\)]+",
            r"https?://streamlit\.io/[^\s\)]+",
            r"https?://gradio\.app/[^\s\)]+",
            r"https?://panel\.holoviz\.org/[^\s\)]+",
            r"https?://voila\.readthedocs\.io/[^\s\)]+",
            r"https?://jupyter\.org/[^\s\)]+",
            r"https?://colab\.research\.google\.com/[^\s\)]+",
            r"https?://kaggle\.com/[^\s\)]+",
            r"https?://wandb\.ai/[^\s\)]+",
            r"https?://neptune\.ai/[^\s\)]+",
            r"https?://mlflow\.org/[^\s\)]+",
            r"https?://dvc\.org/[^\s\)]+",
            r"https?://weights\.biases\.com/[^\s\)]+",
            r"https?://tensorboard\.dev/[^\s\)]+",
            r"https?://tensorboard\.org/[^\s\)]+",
            r"https?://tensorflow\.org/[^\s\)]+",
            r"https?://pytorch\.org/[^\s\)]+",
            r"https?://keras\.io/[^\s\)]+",
            r"https?://scikit-learn\.org/[^\s\)]+",
            r"https?://scipy\.org/[^\s\)]+",
            r"https?://numpy\.org/[^\s\)]+",
            r"https?://pandas\.pydata\.org/[^\s\)]+",
            r"https?://matplotlib\.org/[^\s\)]+",
            r"https?://seaborn\.pydata\.org/[^\s\)]+",
            r"https?://plotly\.com/[^\s\)]+",
            r"https?://bokeh\.org/[^\s\)]+",
            r"https?://dash\.plotly\.com/[^\s\)]+",
            r"https?://streamlit\.io/[^\s\)]+",
            r"https?://gradio\.app/[^\s\)]+",
            r"https?://panel\.holoviz\.org/[^\s\)]+",
            r"https?://voila\.readthedocs\.io/[^\s\)]+",
            r"https?://jupyter\.org/[^\s\)]+",
        ]
        
        # 遍历每个段落
        for p in paragraphs:
            # 检查官方实现指标
            for pattern in rules.get("official_patterns", []):
                matches = re.finditer(pattern, p, re.IGNORECASE)
                for match in matches:
                    official_count += 1
                    evidence = p[max(0, match.start()-50):min(len(p), match.end()+50)].strip()
                    if evidence not in official_evidence:
                        official_evidence.append(evidence)
            
            # 检查非官方实现指标
            for pattern in rules.get("unofficial_patterns", []):
                matches = re.finditer(pattern, p, re.IGNORECASE)
                for match in matches:
                    unofficial_count += 1
                    evidence = p[max(0, match.start()-50):min(len(p), match.end()+50)].strip()
                    if evidence not in unofficial_evidence:
                        unofficial_evidence.append(evidence)
            
            # 查找代码链接
            for pattern in code_patterns:
                matches = re.finditer(pattern, p)
                for match in matches:
                    code_url = match.group().strip()
                    if code_url and not result["code_url"]:
                        result["code_url"] = code_url
        
        # 根据计数确定实现类型和置信度
        if official_count > 0 or unofficial_count > 0:
            if official_count > unofficial_count:
                result["type"] = "official"
                result["evidence"] = official_evidence[:3]  # 最多保留3条证据
                result["confidence"] = "high" if official_count >= 3 else "medium"
            else:
                result["type"] = "unofficial"
                result["evidence"] = unofficial_evidence[:3]  # 最多保留3条证据
                result["confidence"] = "high" if unofficial_count >= 3 else "medium"
        
        # 如果有代码链接但没有其他证据，设置为中等置信度的非官方实现
        elif result["code_url"]:
            result["type"] = "unofficial"
            result["confidence"] = "medium"
            result["evidence"] = [f"Found code repository: {result['code_url']}"]
            
    except Exception as e:
        print(f"分析代码实现时出错: {str(e)}")
        
    return result

def analyze_method_innovation(text, rules_file):
    """分析论文中的方法创新点。
    
    Args:
        text (str): 预处理后的论文文本
        rules_file (str): 分析规则文件路径
    
    Returns:
        dict: 包含创新方法和改进点的字典，如果分析失败则返回 None
    """
    try:
        # 加载分析规则
        rules = load_rules(rules_file)
        if not rules or 'method_innovation' not in rules:
            print("未找到方法创新分析规则")
            return None
            
        # 初始化结果字典
        result = {
            'novel_methods': [],  # 创新方法列表
            'improvements': []    # 改进点列表
        }
        
        # 将文本分割成段落
        paragraphs = text.split("\n\n")
        
        # 分析每个段落
        for paragraph in paragraphs:
            # 跳过空段落
            if not paragraph.strip():
                continue
                
            # 查找创新方法
            for pattern in rules['method_innovation']['novel_patterns']:
                matches = re.finditer(pattern, paragraph, re.IGNORECASE)
                for match in matches:
                    # 提取包含匹配的完整句子
                    sentences = re.split('[.!?]', paragraph)
                    for sentence in sentences:
                        if match.group() in sentence:
                            # 清理并添加句子
                            cleaned = sentence.strip()
                            if cleaned and cleaned not in result['novel_methods']:
                                result['novel_methods'].append(cleaned)
                                
            # 查找改进点
            for pattern in rules['method_innovation']['improvement_patterns']:
                matches = re.finditer(pattern, paragraph, re.IGNORECASE)
                for match in matches:
                    # 提取包含匹配的完整句子
                    sentences = re.split('[.!?]', paragraph)
                    for sentence in sentences:
                        if match.group() in sentence:
                            # 清理并添加句子
                            cleaned = sentence.strip()
                            if cleaned and cleaned not in result['improvements']:
                                result['improvements'].append(cleaned)
        
        # 限制结果数量
        result['novel_methods'] = result['novel_methods'][:3]  # 最多保留3个创新方法
        result['improvements'] = result['improvements'][:3]    # 最多保留3个改进点
        
        return result
        
    except Exception as e:
        print(f"分析创新点时出错: {str(e)}")
        return None

def analyze_paper(text_file, rules_file, output_dir):
    """分析论文内容，提取关键信息并生成报告。
    
    Args:
        text_file (str): 预处理后的论文文本文件路径
        rules_file (str): 分析规则文件路径
        output_dir (str): 输出目录路径
    
    Returns:
        dict: 包含所有分析结果的字典，如果分析失败则返回 None
    """
    try:
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 读取文本内容
        with open(text_file, 'r', encoding='utf-8') as f:
            text = f.read()
            
        # 提取论文基本信息
        paper_info = extract_paper_info(text)
        if not paper_info:
            paper_info = {
                'title': None,
                'authors': [],
                'institutions': []
            }
            
        # 分析代码实现
        implementation = analyze_code_implementation(text, rules_file)
        if not implementation:
            implementation = {
                'type': 'unknown',
                'confidence': 'unknown',
                'code_url': None,
                'evidence': []
            }
            
        # 分析方法创新
        innovation = analyze_method_innovation(text, rules_file)
        if not innovation:
            innovation = {
                'novel_methods': [],
                'improvements': []
            }
            
        # 组合结果
        results = {
            'paper_info': paper_info,
            'implementation': implementation,
            'innovation': innovation,
            'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 保存分析结果
        results_file = os.path.join(output_dir, 'analysis_results.json')
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        # 生成分析报告
        report_file = os.path.join(output_dir, 'analysis_report.md')
        generate_report(results, report_file)
        
        print(f"\n分析完成！")
        print(f"结果文件：{results_file}")
        print(f"报告文件：{report_file}")
        
        return results
        
    except Exception as e:
        print(f"分析论文时出错: {str(e)}")
        return None

def generate_report(results, output_file):
    """生成论文分析报告。
    
    Args:
        results (dict): 分析结果字典
        output_file (str): 输出文件路径
    """
    try:
        # 实现类型映射
        impl_type_map = {
            'official': '官方实现',
            'unofficial': '非官方实现',
            'unknown': '未知'
        }
        
        # 置信度映射
        confidence_map = {
            'high': '高',
            'medium': '中',
            'low': '低',
            'unknown': '未知'
        }
        
        # 生成报告内容
        report = [
            '# 论文分析报告\n',
            f'生成时间：{results["analysis_time"]}\n',
            
            '## 基本信息',
            f'- 标题：{results["paper_info"]["title"] or "未提供"}',
            f'- 作者：{", ".join(results["paper_info"]["authors"]) or "未提供"}',
            f'- 机构：{", ".join(results["paper_info"]["institutions"]) or "未提供"}\n',
            
            '## 代码实现分析',
            f'- 实现类型：{impl_type_map.get(results["implementation"]["type"], "未知")}',
            f'- 置信度：{confidence_map.get(results["implementation"]["confidence"], "未知")}'
        ]
        
        # 添加代码链接（如果有）
        if results['implementation']['code_url']:
            report.append(f'- 代码链接：{results["implementation"]["code_url"]}')
            
        # 添加支持证据
        if results['implementation']['evidence']:
            report.append('\n### 支持证据')
            for evidence in results['implementation']['evidence']:
                report.append(f'- {evidence}')
                
        # 添加方法创新分析
        report.extend([
            '\n## 方法创新分析',
            '\n### 创新方法'
        ])
        
        if results['innovation']['novel_methods']:
            for method in results['innovation']['novel_methods']:
                report.append(f'- {method}')
        else:
            report.append('- 未发现明显的创新方法')
            
        report.append('\n### 改进点')
        if results['innovation']['improvements']:
            for improvement in results['innovation']['improvements']:
                report.append(f'- {improvement}')
        else:
            report.append('- 未发现明显的改进点')
            
        # 添加总结
        report.extend([
            '\n## 分析总结',
            '### 代码实现情况',
            f'该论文{impl_type_map.get(results["implementation"]["type"], "未知")}，'
            f'置信度{confidence_map.get(results["implementation"]["confidence"], "未知")}。'
        ])
        
        if results['implementation']['code_url']:
            report.append(f'提供了代码链接：{results["implementation"]["code_url"]}')
            
        report.append('\n### 创新性分析')
        if results['innovation']['novel_methods'] or results['innovation']['improvements']:
            report.append(f'论文提出了 {len(results["innovation"]["novel_methods"])} 个创新方法'
                        f'和 {len(results["innovation"]["improvements"])} 个改进点。')
        else:
            report.append('未发现明显的创新方法或改进点。')
            
        # 保存报告
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
            
    except Exception as e:
        print(f"生成报告时出错: {str(e)}")
        # 创建一个简单的错误报告
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('# 论文分析报告\n\n生成报告时发生错误。\n\n错误信息：' + str(e))

if __name__ == "__main__":
    # 测试分析功能
    text_file = "output/analysis/text/preprocessed_text.txt"
    rules_file = "output/analysis/rules/analysis_rules.json"
    output_dir = "output/analysis/report"
    analyze_paper(text_file, rules_file, output_dir) 