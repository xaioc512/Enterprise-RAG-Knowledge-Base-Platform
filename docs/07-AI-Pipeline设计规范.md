# 07 - AI Pipeline设计规范

> 版本：v1.0 | 日期：2026-06-08

---

## 1. 模块架构

```
rag/
├── loader.py       # 文档加载器
├── splitter.py     # 文本分块器
├── embedder.py     # DeepSeek Embedding封装
├── retriever.py    # Chroma检索器
├── generator.py    # DeepSeek Chat生成（流式）
└── pipeline.py     # 完整Pipeline编排
```

## 2. 文档加载器

| 格式 | 库 | 方法 |
|------|-----|------|
| PDF | PyPDF2 | `PdfReader` 逐页提取 |
| Word | python-docx | `Document` 逐段提取 |
| Markdown | markdown | 转纯文本后处理 |
| TXT | 内置 | `open().read()` |

```python
from abc import ABC, abstractmethod

class BaseLoader(ABC):
    @abstractmethod
    def load(self, file_path: str) -> str:
        """加载文档并返回纯文本"""
        ...

class PDFLoader(BaseLoader): ...
class DocxLoader(BaseLoader): ...
class MarkdownLoader(BaseLoader): ...
class TxtLoader(BaseLoader): ...
```

## 3. 文本分块

使用 LangChain `RecursiveCharacterTextSplitter`：

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", "。", ".", " ", ""]
)
```

## 4. DeepSeek Embedding

```python
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(
    model="deepseek-embedding",  # 或具体模型名
    openai_api_key=settings.DEEPSEEK_API_KEY,
    openai_api_base="https://api.deepseek.com/v1",
)
```

## 5. Chroma 检索

```python
from langchain_chroma import Chroma

vectorstore = Chroma(
    collection_name="knowledge_base",
    embedding_function=embeddings,
    persist_directory=settings.CHROMA_PERSIST_DIR,
)

# 检索Top-5
docs = vectorstore.similarity_search(query, k=5)
# 带相似度分数的检索
docs_with_scores = vectorstore.similarity_search_with_score(query, k=5)
```

## 6. DeepSeek Chat 生成

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="deepseek-chat",
    openai_api_key=settings.DEEPSEEK_API_KEY,
    openai_api_base="https://api.deepseek.com/v1",
    streaming=True,
    temperature=0.3,  # RAG场景低温度，保证准确性
)
```

## 7. RAG Prompt 模板

```python
SYSTEM_PROMPT = """你是企业内部知识库AI助手。请仅根据以下提供的文档内容回答用户问题。
如果文档中没有相关信息，请如实告知用户"文档库中暂未找到相关信息"。
回答时请明确引用文档来源。"""

USER_PROMPT_TEMPLATE = """参考文档片段：
{sources}

---
历史对话：
{history}

---
用户问题：{question}

请回答："""
```

## 8. Pipeline 编排

```
1. 接收用户消息 + conversation_id
2. 获取/创建对话
3. 加载对话历史（最近10轮）
4. 问题向量化 → Chroma检索 → Top-5 文档片段
5. 构建 Prompt（系统提示 + 来源文档 + 历史 + 问题）
6. 流式调用 DeepSeek Chat
7. 收集完整回答 → 解析引用 → 保存到MySQL
8. 更新对话标题（首轮时用前20字作为标题）
```

## 9. 依赖

```toml
[tool.poetry.dependencies]
langchain = "^0.3"
langchain-openai = "^0.2"
langchain-chroma = "^0.1"
chromadb = "^0.5"
PyPDF2 = "^3.0"
python-docx = "^1.1"
markdown = "^3.5"
```

---

> 关联文档：[02-技术选型与架构设计](02-技术选型与架构设计.md) | [06-数据库设计规范](06-数据库设计规范.md)
