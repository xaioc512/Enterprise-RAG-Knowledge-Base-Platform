"""AI Agent 工具集 — 供 LangGraph Agent 调用"""

from langchain_core.tools import tool

from app.rag.retriever import search_similar
from app.rag.web_search import web_search, format_web_results


@tool
def search_knowledge_base(query: str) -> str:
    """
    在企业内部知识库中搜索相关文档内容。
    适用于查找制度规范、工艺流程、技术文档等企业内部信息。
    参数: query - 搜索查询文本
    返回: 相关文档片段（含来源和内容预览）
    """
    results = search_similar(query, k=5)
    if not results:
        return "知识库中未找到相关信息。"

    lines = []
    for i, (content, meta, score) in enumerate(results, 1):
        title = meta.get("document_title", "未知文档")
        lines.append(f"[kb{i}] 来源: {title}\n内容: {content[:500]}")
    return "\n\n".join(lines)


@tool
def search_web(query: str) -> str:
    """
    在互联网上搜索最新信息。当知识库中没有相关信息时使用。
    适用于查找外部公开信息、新闻、通用知识等。
    参数: query - 搜索查询文本
    返回: 网页搜索结果摘要
    """
    results = web_search(query, max_results=3)
    return format_web_results(results)


@tool
def analyze_data(question: str) -> str:
    """
    使用 Python Pandas 分析数据。当用户询问统计、计算、趋势等问题时使用。
    参数: question - 用户的数据分析需求描述（用自然语言）
    返回: 分析结果
    """
    try:
        import pandas as pd
        import io

        # 这里可以根据实际需求扩展：从数据库查询数据进行分析
        # 当前返回引导信息
        return (
            "数据分析工具已就绪。可以使用 Pandas 进行以下分析：\n"
            "- 数据统计和汇总\n"
            "- 趋势分析和预测\n"
            "- 数据清洗和转换\n"
            "请在提问中明确需要分析的数据类型和维度。"
        )
    except ImportError:
        return "Pandas 未安装，数据分析功能不可用。"
