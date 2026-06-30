"""天气查询工具"""

import httpx
from app.core.config import settings


async def get_weather(city: str) -> str:
    """查询城市天气"""
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={settings.OPENWEATHER_API_KEY}&lang=zh_cn&units=metric"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        data = resp.json()
        if resp.status_code != 200:
            return f"查询失败: {data.get('message', '未知错误')}"
        desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        return f"{city} 当前天气: {desc}, 温度: {temp}°C"


WEATHER_TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "查询指定城市的当前天气",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "城市名称（中文）"},
            },
            "required": ["city"],
        },
    },
}
