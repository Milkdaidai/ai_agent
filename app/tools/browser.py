"""浏览器工具"""

import httpx
from bs4 import BeautifulSoup
from langchain_core.tools import tool


@tool
async def browse(url: str) -> str:
    """访问网页并提取文本内容

    Args:
        url: 网页 URL。
    """
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url, headers={"User-Agent": "AI-Agent/1.0"})
            soup = BeautifulSoup(resp.text, "html.parser")
            text = soup.get_text(separator=" ", strip=True)
            return text[:2000]
    except Exception as e:
        return f"访问失败: {e}"
