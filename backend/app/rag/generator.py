"""DeepSeek Chat 生成器 — 流式输出"""

from openai import AsyncOpenAI

from app.config import settings


_client: AsyncOpenAI | None = None


def get_client() -> AsyncOpenAI:
    """获取 DeepSeek API 客户端（兼容 OpenAI SDK）"""
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=f"{settings.DEEPSEEK_BASE_URL}/v1",
        )
    return _client


async def generate_stream(
    messages: list[dict],
    temperature: float = 0.3,
) -> str:
    """
    流式生成回答，通过 async generator 逐块返回文本。

    Usage:
        async for chunk in generate_stream(messages):
            yield chunk
    """
    client = get_client()
    response = await client.chat.completions.create(
        model=settings.DEEPSEEK_CHAT_MODEL,
        messages=messages,
        temperature=temperature,
        stream=True,
    )

    async for chunk in response:
        delta = chunk.choices[0].delta if chunk.choices else None
        if delta and delta.content:
            yield delta.content


async def generate_sync(
    messages: list[dict],
    temperature: float = 0.3,
) -> str:
    """非流式生成（用于标题生成等场景）"""
    client = get_client()
    response = await client.chat.completions.create(
        model=settings.DEEPSEEK_CHAT_MODEL,
        messages=messages,
        temperature=temperature,
        stream=False,
    )
    return response.choices[0].message.content.strip()
