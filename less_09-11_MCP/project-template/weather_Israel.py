import asyncio
import os

from mcp.server.fastmcp import FastMCP
from playwright.async_api import async_playwright
from google import genai

import logging

logging.basicConfig(
    filename='mcp_server.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

mcp = FastMCP("weather-Israel")

FORECAST_URL = "https://www.weather2day.co.il/forecast"

_playwright = None
_browser = None
_page = None

async def get_page():
    logging.info("Checking Playwright browser instance...")
    global _playwright, _browser, _page
    if _playwright is None:
        _playwright = await async_playwright().start()
        _browser = await _playwright.chromium.launch(headless=True)
        _page = await _browser.new_page()

    if _page.is_closed():
        _page = await _browser.new_page()
    return _page

@mcp.tool()
async def open_weather_forecast_israel():
    """Opens the weather forecast page for Israel"""
    try:
        page = await get_page()
        await page.goto(FORECAST_URL)
        logging.info("✅ Weather forecast page opened successfully")
    except Exception as e:
        logging.error(f"❌ Failed to open weather forecast page: {str(e)}")

@mcp.tool()
async def enter_weather_forecast_city_israel(city: str = "ירושלים"):
    """
    Enters the city name in the weather forecast search box.
    If the input is in English, translate it to Hebrew before calling this tool.
    Example: 'Jerusalem' -> 'ירושלים'

    Args:
        city: The name of the city to search for (in Hebrew)
    """
    try:
        page = await get_page()
        await page.locator("#city_search_forecast").fill(city)
        logging.info(f"✅ City entered: {city}")
        
    except Exception as e:
        logging.error(f"❌ Failed to enter city: {str(e)}")

@mcp.tool()
async def select_weather_forecast_city_israel(option: str):
    """Selects the city from the dropdown options

    Args:
        option: The exact text of the city option to select (in Hebrew)
    """
    try:
        page = await get_page()
        dropdown =  page.locator("#city_search_forecastautocomplete-list")

        target_option = dropdown.get_by_text(option, exact=False).first

        await target_option.wait_for(state="visible", timeout=10000)

        await target_option.click()

        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(2)

        weather_container = page.locator(".current-weather:visible").first
        await weather_container.wait_for(state="visible", timeout=15000)
        raw_weather_info = await weather_container.inner_text()

        logging.info(f"weather_forecast for {str(option)} selected successfully")

        await page.close()
        logging.info(f"Raw whether information: {raw_weather_info}")
        return raw_weather_info

    except Exception as e:
        logging.error(f"❌ Failed to select city: {str(e)}")


@mcp.tool()      
async def refine_enrich_context(raw_weather_data: str):
    """
    A processing tool that takes raw, technical weather data (temperature, humidity, conditions) and transforms it into a polished, user-friendly summary.
    Use this ONLY after you have gathered all necessary data from other weather tools.
    Args:
        raw_weather_data: The FULL technical text/JSON returned from previous weather tool calls. 
        DO NOT just pass the city name; pass the actual weather statistics found.
    """
    
    prompt = f"""
    You are a friendly weather assistant. Below is raw weather data or information. 
    Please rewrite it into a concise, clear, and professional summary for the user. 
    Focus on:
    - Current temperature and "feels like".
    - Weather conditions (sunny, rainy, etc.).
    - Practical advice (e.g., "take an umbrella").
    
    Raw Data: {raw_weather_data}
    """
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    model_name = os.environ.get("GEMINI_MODEL")

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error refining context: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")