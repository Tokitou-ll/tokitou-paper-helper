# 项目开发指令文档

本文档记录了论文代码实现分析工具的开发指令。每个工作流都有一个统一的入口文件，可以一键执行该阶段的所有任务。

## 工作流概述

1. 工作流1：项目初始化 (`scripts/workflow1_init.py`)
   - 创建项目目录结构
   - 配置开发环境

2. 工作流2：论文信息汇总 (`scripts/workflow2_summary.py`)
   - 扫描论文目录
   - 生成汇总文档

3. 工作流3：单篇论文分析 (`scripts/workflow3_analyze.py`)
   - 选择目标论文
   - 执行分析流程
   - 更新汇总文档

4. 工作流4：批量分析任务 (`scripts/workflow4_batch.py`)
   - 准备批处理环境
   - 执行批量分析
   - 生成分析报告

## 工作流1：项目初始化

### 执行方式
```bash
python scripts/workflow1_init.py
```

### 任务内容
1. 创建项目目录：
   - [x] data/test：论文存放位置
   - [x] output：结果输出位置
   - [x] output/analysis/text：文本提取结果
   - [x] output/analysis/report：分析报告
   - [x] output/analysis/rules：分析规则
   - [x] logs：日志文件

2. 配置开发环境：
   - [x] 创建 Python 虚拟环境
   - [x] 安装依赖包：
     - PyPDF2：PDF 文件处理
     - python-magic：文件类型检测
     - pyyaml：配置文件处理
     - langchain：AI 文本处理
     - transformers：自然语言处理
     - fastapi：Web API 服务
     - uvicorn：ASGI 服务器

## 工作流2：论文信息汇总

### 执行方式
```bash
python scripts/workflow2_summary.py
```

### 任务内容
1. 扫描论文目录：
   - [x] 读取 data/test 目录下的 PDF 文件
   - [x] 获取文件基本信息：
     - 文件名
     - 相对路径
     - 文件大小
     - 修改时间

2. 生成汇总文档：
   - [x] 在 output 目录下创建 paper_summary.md
   - [x] 按格式生成内容：
     - 文档标题和说明
     - 论文列表表格
     - 统计信息
     - 注意事项

## 工作流3：单篇论文分析

### 执行方式
```bash
python scripts/workflow3_analyze.py
```

### 任务内容
1. 选择目标论文：
   - [x] 从 paper_summary.md 中确定待分析论文
   - [x] 记录论文基本信息（文件名、路径等）

2. 执行分析流程：
   - [x] PDF 文本提取
     - 提取论文标题、作者、摘要等基本信息
     - 提取关键章节内容（实现细节、代码示例、实验部分等）
     - 保存结构化的文本内容
   
   - [x] AI 分析（使用 Grok API）
     - 第一阶段：论文类型分析
       * 判断是否为官方实现论文
       * 识别作者团队背景
       * 分析代码仓库信息
       * 评估实验的可复现性
     
     - 第二阶段：生成分析报告
       * 整合分析结果
       * 生成结构化的 Markdown 报告
       * 提供具体的改进建议

   - [x] 结果处理
     - 保存分析报告（Markdown 格式）
     - 保存完整结果（JSON 格式）
     - 更新论文汇总文档

### 输出文件
1. 分析报告 (`output/analysis/report/<paper_name>_analysis.md`)
   ```markdown
   # 论文分析报告
   
   ## 基本信息
   - 标题：[论文标题]
   - 作者：[作者列表]
   - 分析时间：[时间戳]
   
   ## 实现类型判定
   - 判定结果：[官方实现/非官方实现]
   - 判定依据：
     1. [依据1]
     2. [依据2]
     ...
   
   ## 关键发现
   1. [发现1]
   2. [发现2]
   ...
   
   ## 建议
   1. [建议1]
   2. [建议2]
   ...
   ```

2. 分析结果 (`output/analysis/report/<paper_name>_analysis.json`)
   ```json
   {
     "paper_info": {
       "title": "论文标题",
       "authors": "作者列表",
       "metadata": {}
     },
     "paper_type_analysis": "类型分析结果",
     "final_report": "完整报告内容",
     "analysis_time": "分析时间戳"
   }
   ```

### 配置要求

1. AI 服务配置 (`config/ai_config.yaml`)
   ```yaml
   services:
     grok:
       api_key: "your-api-key-here"
       api_base: "https://api.groq.com/openai/v1"
       model: "mixtral-8x7b-32768"
       timeout: 60
   ```

2. 分析提示模板 (`config/prompts.yaml`)
   ```yaml
   analysis_prompts:
     paper_type:
       system: "论文类型分析提示..."
       user: "分析模板..."
     final_report:
       system: "报告生成提示..."
       user: "报告模板..."
   ```

### 注意事项

1. 前置条件：
   - 确保 AI 服务配置正确（API密钥等）
   - PDF 文件可访问且格式正确
   - 配置文件完整且格式正确

2. 错误处理：
   - PDF 解析失败时提供错误信息
   - AI 服务调用失败时自动重试
   - 保存所有分析过程的日志

3. 性能优化：
   - 缓存提取的文本内容
   - 分批处理大型论文
   - 使用异步调用提高效率

4. 结果验证：
   - 检查报告完整性
   - 验证分析结果的合理性
   - 确保输出格式规范

## 工作流4：批量分析任务

### 执行方式
```bash
python scripts/workflow4_batch.py
```

### 任务内容
1. 准备批处理环境：
   - [x] 检查配置文件完整性
   - [x] 验证目录结构
   - [x] 初始化日志系统

2. 执行批量分析：
   - [x] 扫描论文目录
   - [x] 创建任务队列
   - [x] 分批执行分析：
     * 使用工作流3的 PaperAnalyzer 进行分析
     * 每批次处理指定数量的论文
     * 支持断点续处理
   - [x] 错误处理：
     * 记录失败的任务
     * 支持失败重试
     * 保存错误日志

3. 生成汇总报告：
   - [x] 收集所有分析结果
   - [x] 生成统计信息：
     * 总论文数量
     * 官方实现数量
     * 非官方实现数量
     * 分析失败数量
   - [x] 生成汇总报告：
     * Markdown格式
     * 包含所有论文的简要分析结果
     * 提供详细报告的链接

### 配置要求

1. 批处理配置 (`config/batch_config.yaml`)
```yaml
# 批处理参数
batch:
  size: 5                # 每批次处理的论文数量
  max_retries: 3         # 失败重试次数
  parallel: false        # 是否并行处理（当前版本不支持）

# 输出设置
output:
  summary_file: output/batch_summary.md    # 汇总报告文件
  log_file: logs/batch_process.log         # 处理日志文件
  error_log: logs/error.log                # 错误日志文件

# 路径配置
paths:
  papers_dir: data/test                    # 论文目录
  output_dir: output/analysis/report       # 输出目录
  temp_dir: output/temp                    # 临时文件目录

# 处理控制
control:
  continue_on_error: true                  # 错误时是否继续处理其他文件
  save_temp: false                         # 是否保存临时文件
```

### 输出文件

1. 批处理汇总报告 (`output/batch_summary.md`)
```markdown
# 论文分析批处理报告

## 处理概况
- 总论文数：[数量]
- 处理成功：[数量]
- 处理失败：[数量]
- 处理时间：[起始时间] - [结束时间]

## 实现类型统计
- 官方实现：[数量] ([百分比])
- 非官方实现：[数量] ([百分比])
- 无法判定：[数量] ([百分比])

## 分析结果汇总
1. [论文标题1]
   - 类型：[官方/非官方]
   - 可信度：[高/中/低]
   - 详细报告：[链接]

2. [论文标题2]
   ...

## 处理失败列表
1. [论文标题]
   - 原因：[失败原因]
   - 重试次数：[次数]
```

2. 错误日志 (`logs/error.log`)
```
[时间戳] [论文名] [错误类型] [错误信息]
[时间戳] [论文名] [重试次数] [重试结果]
...
```

### 注意事项

1. 资源管理
   - 合理设置批次大小，避免内存溢出
   - 及时清理临时文件
   - 定期保存处理进度

2. 错误处理
   - 记录详细的错误信息
   - 支持从失败处继续处理
   - 提供重试机制

3. 性能优化
   - 使用异步处理提高效率
   - 缓存已处理的结果
   - 避免重复分析

4. 结果验证
   - 检查每篇论文的分析结果
   - 验证统计数据的准确性
   - 确保报告格式规范

## 配置文件说明

### batch_config.yaml
```yaml
# 批处理参数
batch:
  size: 5                # 每批次处理的论文数量
  timeout: 1800          # 每个任务超时时间（秒）
  max_retries: 3         # 失败重试次数
  parallel_tasks: 2      # 并行处理的任务数

# 输出设置
output:
  log_level: INFO
  log_file: logs/batch_process.log
  report_format: markdown
  report_dir: output/analysis/report/batch

# 错误处理
error_handling:
  retry_delay: 300       # 重试等待时间（秒）
  skip_on_failure: true  # 失败时是否跳过继续处理
  error_log: logs/error.log

# 路径配置
paths:
  input_summary: output/paper_summary.md
  temp_dir: output/temp
  data_dir: data/test
```

## 注意事项

1. 工作流必须按顺序执行，每个后续工作流依赖于前一个工作流的完成
2. 每个工作流都有独立的入口文件，可以通过运行对应的 Python 脚本执行
3. 所有中间结果都会保存在 output 目录下
4. 批处理配置可以通过修改 config/batch_config.yaml 文件调整

## 更新记录

### 2024-03-21
- 创建初始文档结构
- 完成工作流1-4的实现
- 添加统一的入口文件
- 优化工作流执行逻辑
- 完善错误处理机制
- 更新文档结构

