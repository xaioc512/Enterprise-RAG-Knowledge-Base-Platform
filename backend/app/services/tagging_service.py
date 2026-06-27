"""文档智能标注服务 — LLM 自动生成摘要、关键词、分类建议"""

import json
from loguru import logger
from app.rag.generator import get_client

TAGGING_PROMPT = """你是企业文档分析专家。请分析以下文档内容，返回 JSON 格式（不要包含其他文字）：

{
  "summary": "150字以内的中文摘要，概括文档核心内容",
  "keywords": ["关键词1", "关键词2", "关键词3", "关键词4", "关键词5"],
  "suggested_category": "制度规范|工艺流程|流程文档|技术文档"
}

文档内容：
{content}

请输出 JSON："""


async def auto_tag_document(content: str, max_chars: int = 3000) -> dict:
    """
    对文档内容进行智能标注

    返回: {"summary": str, "keywords": list[str], "suggested_category": str}
    """
    # 截取前 max_chars 字符，避免 token 超限
    truncated = content[:max_chars]

    try:
        client = get_client()
        response = await client.chat.completions.create(
            model="deepseek-chat",
            messages=[{
                "role": "user",
                "content": TAGGING_PROMPT.format(content=truncated),
            }],
            temperature=0.3,
            max_tokens=500,
        )

        result_text = response.choices[0].message.content.strip()

        # 尝试提取 JSON（可能被 markdown 代码块包裹）
        if "```" in result_text:
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]

        result = json.loads(result_text)
        logger.info(f"Tagging result: {len(result.get('keywords', []))} keywords, cat: {result.get('suggested_category', 'N/A')}")
        return result

    except json.JSONDecodeError as e:
        logger.warning(f"Tagging JSON parse error: {e}, raw: {result_text[:200]}")
        return {"summary": content[:150], "keywords": [], "suggested_category": ""}
    except Exception as e:
        logger.error(f"Tagging error: {e}")
        return {"summary": content[:150], "keywords": [], "suggested_category": ""}
