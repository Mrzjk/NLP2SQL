## Text2SQL 智能体

将中文自然语言问题自动转换为可在 MySQL 执行的 SQL 语句，并进行一次性校验（开启事务后回滚，仅验证可执行性与结果形态）。项目基于 LangChain、LangGraph 与大语言模型，内置表结构向量检索，自动进行问题改写、相关表召回、问题完善、SQL 生成、执行验证与思考式迭代修正。

### 主要特性
- 将自然语言问题转为标准 SQL，并在数据库中校验可执行性
- 多路召回相关数据表（Chroma 向量库），限定字段与表，防止“越权”引用
- 工作流驱动（LangGraph）：改写 → RAG → 完善 → 生成 → 执行 → 判断/反思 → 迭代
- 结构化输出解析（Pydantic），确保返回严格的 `SQL` 或计划结构
- 事务回滚执行验证，安全不改写数据

## 环境准备

### 依赖
建议 Python 3.10+。

```bash
pip install -U pip
pip install langchain-openai langchain-core langgraph langchain-chroma chromadb pymysql python-dotenv pydantic
```

### 环境变量（.env）
在项目根目录创建 `.env` 文件：

```dotenv
# 大模型与向量模型
API_KEY=你的_API_Key
BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small

# MySQL 连接
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=your_database
```

说明：
- `BASE_URL` 支持 OpenAI 兼容服务地址。
- `MODEL_NAME` 与 `EMBEDDING_MODEL` 需与你的服务/镜像可用模型一致。

## 项目结构

```text
Text2SQL/
  ├─ agent/
  │  ├─ graph.py               # 智能体工作流（LangGraph 状态机）
  │  └─ model.py               # 思考/判定结果的数据结构（Pydantic）
  ├─ config/
  │  └─ config.py              # 配置数据类（如相关表召回上限）
  ├─ model/
  │  └─ tables.py              # 业务表结构定义（Pydantic 模型）
  ├─ prompts/
  │  ├─ __init__.py            # 导出提示词模板
  │  └─ prompt.py              # 提示词模板：生成、改写、完善、思考、评估
  ├─ utils/
  │  ├─ dataset_util.py        # 执行结果转字典工具
  │  ├─ output_format.py       # LLM 输出解析格式（SQL/问题格式）
  │  └─ table_util.py          # 表结构向量库保存/加载（Chroma）
  ├─ table_schemas_db/         # Chroma 持久化目录（自动生成/已内置）
  ├─ main.py                   # 入口：演示从问题到 SQL 的全流程
  └─ readme                    # 本说明
```

## 初始化与运行

### 1) 初始化表结构向量库（如首次运行或更改了表定义）
`utils/table_util.py` 会读取 `model/tables.py` 的表定义，并将其结构以向量形式持久化到 `table_schemas_db/`：

```bash
python utils/table_util.py
```

若目录已存在且内含数据，可跳过。

### 2) 运行主程序

```bash
python main.py
```

程序会：
- 加载 .env 与数据库连接
- 构建工作流，并以示例问题触发一轮改写/检索/完善/生成/验证/反思
- 控制台打印最终 SQL：

```
===========生成的SQL语句=============
<最终可执行的 SQL>
```

## 工作流原理（LangGraph）

节点说明（位于 `agent/graph.py`）：
- `change_question`：问题专业化改写（生成多种风格的分析型表述）
- `rag`：基于改写问题与原问题，在向量库中检索最相关的 K 张表并合并描述
- `completetion_question`：根据表信息完善问题，使其更可 SQL 化
- `generate_sql`：按规则生成或迭代优化 SQL（严格限定在相关表/字段内）
- `execute_sql`：在 MySQL 中开启事务执行 SQL，抓取结果后回滚
- `thinker`：评估结果是否匹配问题；若不匹配，产出下一步修正计划并回到 `generate_sql`

状态结构（节选）：
- `original_question`/`question`/`rewritten_question`
- `related_tables`：与问题相关的表及字段提示
- `sql`：历史 SQL 列表（便于迭代优化）
- `execute_info`：上次执行结果（字典列表）或错误信息
- `plan`：思考生成的迭代计划

## 数据与表结构

位于 `model/tables.py`，使用 Pydantic 定义以下表的字段与含义（示例）：
- `enterprise_basic_info`：企业基本信息
- `enterprise_annual_finance`：企业年度财务
- `enterprise_quarterly_finance`：企业季度财务
- `industry_development`：产业发展总体指标
- `tb_policies`：政策信息库

向量库中保存的是这些表的 JSON Schema，用于在生成 SQL 时严格限定可用表与字段。

## 配置

- `config/config.py` 提供 `Configuration` 数据类（如 `relation_table_count` 检索表数量上限）。
- 如需改动召回数量、模型名称或温度等，可分别在 `config/config.py` 与 `agent/graph.py` 中调整。

## 常见问题

- 连接 MySQL 失败：
  - 确认 `.env` 中 `DB_HOST/DB_PORT/DB_USER/DB_PASSWORD/DB_NAME` 正确
  - 数据库网络可达，账号具备 `SELECT` 权限

- 生成 SQL 引用了不存在的字段/表：
  - 先执行 `python utils/table_util.py` 以更新向量库
  - 确保 `model/tables.py` 的字段与真实数据库一致

- 执行结果为空或不匹配：
  - 工作流会自动进入 `thinker` 节点进行原因分析与迭代修正
  - 可查看控制台日志定位聚合/条件/关联是否合理

- 更换/新增业务表：
  - 更新 `model/tables.py`
  - 重新运行 `python utils/table_util.py`

## 快速上手（Windows 虚拟环境可选）

```bat
py -3.10 -m venv .venv
.venv\Scripts\activate
pip install -U pip
pip install langchain-openai langchain-core langgraph langchain-chroma chromadb pymysql python-dotenv pydantic
python utils/table_util.py
python main.py
```

## 安全性

本项目的 SQL 执行默认开启事务并在结束时回滚，不会对数据库产生写入或结构性变更。请勿输入 DDL/DML 类需求；若需启用生产环境，请务必自查并限制可执行语句类型。

## 许可

如未附带许可证文件，请在使用前与项目作者确认授权方式。
