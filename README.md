# Python 工具集

这个目录包含各种Python工具文件，使用Poetry进行依赖管理。

## 环境设置

### 使用Poetry管理环境

本项目使用Poetry进行依赖管理和虚拟环境管理。

#### 1. 安装Poetry

```bash
# 使用官方安装脚本
curl -sSL https://install.python-poetry.org | python3 -

# 或者使用pip安装
pip install poetry
```

#### 2. 初始化项目环境

```bash
# 检查项目配置
poetry check

# 安装所有依赖（包括开发依赖）
poetry install

# 或者只安装生产依赖
poetry install --only=main
```

#### 3. 常用Poetry命令

```bash
# 显示环境信息
poetry env info

# 激活虚拟环境
poetry shell

# 在虚拟环境中运行命令
poetry run python civil_code_parser.py

# 添加新依赖
poetry add requests

# 添加开发依赖
poetry add --group dev pytest

# 显示已安装的包
poetry show

# 更新依赖
poetry update
```

## 工具文件

### 1. 民法典解析器

#### 文本文件解析器 (civil_code_parser.py)
一个用于解析民法典文本文件的工具，可以将民法典条款自动转换为结构化的JSON格式。

#### Word文档解析器 (docx_civil_code_parser.py)
专门用于解析.docx格式的民法典文件，支持结构化提取和智能解析。

#### PDF文档解析器 (pdf_civil_code_parser.py)
专门用于解析PDF格式的民法典文件，支持多种PDF读取方法和智能解析。

#### 功能特点

- 自动识别和分割民法典条款
- 使用OpenAI GPT模型进行智能解析
- 支持批量处理
- 包含错误处理和重试机制
- 可配置的API调用间隔
- 支持环境变量配置
- **Word文档支持**: 直接解析.docx文件
- **PDF文档支持**: 直接解析PDF文件
- **结构化提取**: 智能识别条款标题和内容
- **多种PDF读取方法**: 支持pdfplumber和PyPDF2

#### 使用方法

##### 方法1: 解析Word文档（推荐）

1. 设置环境变量：
```bash
# Windows
set OPENAI_API_KEY=sk-your-actual-api-key

# Linux/Mac
export OPENAI_API_KEY=sk-your-actual-api-key
```

2. 准备Word文档：
   - 将民法典Word文档命名为 `1.中华人民共和国民法典.docx`
   - 确保文件在当前目录中

3. 运行解析器：
```bash
# 使用简单脚本
poetry run python parse_civil_code_docx.py

# 或使用完整功能
poetry run python docx_civil_code_parser.py
```

##### 方法2: 解析PDF文档

1. 设置环境变量（同上）

2. 准备PDF文件：
   - 将民法典PDF文件命名为 `民法典.pdf`
   - 确保文件在当前目录中

3. 运行解析器：
```bash
# 使用简单脚本
poetry run python parse_civil_code_pdf.py

# 或使用完整功能
poetry run python pdf_civil_code_parser.py
```

##### 方法3: 解析文本文件

1. 设置环境变量（同上）

2. 准备文本文件：
   - 将民法典文本保存为 `civil_code.txt` 文件
   - 确保文件编码为UTF-8

3. 运行解析器：
```bash
poetry run python civil_code_parser.py
```

#### 输出格式

解析结果将保存为JSON文件，每个条款包含以下字段：
- `article_number`: 条款号（如"第一百五十八条"）
- `content`: 条款内容

### 2. 环境变量管理

项目支持通过环境变量进行配置：

- 支持从 `.env` 文件加载环境变量
- 支持多种配置方式
- 包含安全的环境变量处理

## 项目结构

```
python-tool/
├── pyproject.toml              # Poetry项目配置
├── civil_code_parser.py        # 文本文件民法典解析器
├── docx_civil_code_parser.py   # Word文档民法典解析器
├── pdf_civil_code_parser.py    # PDF文档民法典解析器
├── parse_civil_code_txt.py     # 文本解析脚本
├── parse_civil_code_docx.py    # Word解析脚本
├── parse_civil_code_pdf.py     # PDF解析脚本
├── README.md                   # 项目说明文档
└── .env                        # 环境变量文件（需要创建）
```

## 开发工具

项目包含以下开发工具配置：

- **Black**: 代码格式化
- **Flake8**: 代码风格检查
- **MyPy**: 类型检查
- **Pytest**: 单元测试
- **Pre-commit**: Git提交前检查

## 注意事项

- 需要有效的OpenAI API密钥
- 建议设置适当的API调用间隔以避免速率限制
- 确保输入文件格式正确，条款以"第xxx条"开头
- 使用Poetry管理依赖可以确保环境一致性
