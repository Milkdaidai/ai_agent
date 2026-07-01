"""天气查询工具"""

import httpx
from langchain_core.tools import tool

from app.core.config import settings


@tool
async def get_weather(city: str) -> str:
    """查询指定城市的当前天气

    Args:
        city: 城市名称（中文）。
    """
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={settings.OPENWEATHER_API_KEY}&lang=zh_cn&units=metric"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        data = resp.json()
        if resp.status_code != 200:
            return f"查询失败: {data.get('message', '未知错误')}"
        desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        return f"{city} 当前天气: {desc}, 温度: {temp}°C"
