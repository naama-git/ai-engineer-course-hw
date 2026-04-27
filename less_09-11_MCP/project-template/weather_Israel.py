from mcp.server.fastmcp import FastMCP
from playwright.sync_api import sync_playwright

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

def get_page():
    logging.info("🔍 Checking Playwright browser instance...")
    global _playwright, _browser, _page
    if _playwright is None:
        _playwright = sync_playwright().start()
        _browser = _playwright.chromium.launch(headless=False)
        _page = _browser.new_page()
    return _page

@mcp.tool()
def open_weather_forecast_israel():
    """Opens the weather forecast page for Israel"""
    try:
        page = get_page()
        page.goto(FORECAST_URL)
        logging.info("✅ Weather forecast page opened successfully")
    except Exception as e:
        logging.info(f"❌ Failed to open weather forecast page: {str(e)}")

@mcp.tool()
def enter_weather_forecast_city_israel(city: str = "ירושלים"):
    """
    Enters the city name in the weather forecast search box.
    If the input is in English, translate it to Hebrew before calling this tool.
    Example: 'Jerusalem' -> 'ירושלים'

    Args:
        city: The name of the city to search for (in Hebrew)
    """
    try:
        page = get_page()
        page.get_by_placeholder("מזג האוויר ב...").fill(city)
        logging.info(f"✅ City entered: {city}")
    except Exception as e:
        logging.info(f"❌ Failed to enter city: {str(e)}")

@mcp.tool()
def select_weather_forecast_city_israel(option: str):
    """Selects the city from the dropdown options

    Args:
        option: The exact text of the city option to select (in Hebrew)
    """
    try:
        page = get_page()
        dropdown = page.locator("#city_search_forecastautocomplete-list")

        target_option = dropdown.get_by_text(option, exact=True)

        target_option.wait_for(state="visible", timeout=5000)

        target_option.click()

        page.wait_for_load_state("networkidle")

        logging.info(f"weather_forecast for {str(option)} selected successfully")

    except Exception as e:
        logging.info(f"❌ Failed to select city: {str(e)}")

if __name__ == "__main__":
    mcp.run(transport="stdio")