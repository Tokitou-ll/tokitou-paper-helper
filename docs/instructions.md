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
   - [x] 从 paper_summary.md 中确定第一篇论文
   - [x] 记录论文信息

2. 执行分析流程：
   - [x] PDF 文件验证
   - [x] 文本提取
   - [x] 文本预处理
   - [x] 规则准备
   - [x] 论文分析

3. 更新汇总文档：
   - [x] 更新分析状态
   - [x] 添加分析结果
   - [x] 记录更新时间

## 工作流4：批量分析任务

### 执行方式
```bash
python scripts/workflow4_batch.py
```

### 任务内容
1. 准备批处理环境：
   - [x] 清理临时文件
   - [x] 检查配置文件
   - [x] 初始化任务队列

2. 执行批量分析：
   - [x] 扫描所有论文
   - [x] 并行处理任务
   - [x] 错误处理和重试

3. 生成分析报告：
   - [x] 收集处理结果
   - [x] 生成统计报告
   - [x] 更新汇总文档

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

