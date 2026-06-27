"""联网搜索工具 — DuckDuckGo 免费搜索 API"""

from loguru import logger


async def web_search(query: str, max_results: int = 3) -> list[dict]:
    """
    执行联网搜索，返回结果列表 [{title, url, snippet}, ...]

    使用 DuckDuckGo Instant Answer API（免费、无需密钥）
    """
    try:
        from duckduckgo_search import DDGS

        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", ""),
                })

        logger.info(f"Web search '{query[:40]}...' returned {len(results)} results")
        return results

    except ImportError:
        logger.warning("duckduckgo-search not installed, web search unavailable")
        return []
    except Exception as e:
        logger.error(f"Web search error: {e}")
        return []


def format_web_results(results: list[dict]) -> str:
    """将搜索结果格式化为 Prompt 文本"""
    if not results:
        return "（无网络搜索结果）"

    lines = []
    for i, r in enumerate(results, 1):
        lines.append(f"[web{i}] {r['title']}\n{r['snippet']}\n来源: {r['url']}")
    return "\n\n".join(lines)
