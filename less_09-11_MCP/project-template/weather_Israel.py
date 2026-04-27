from mcp.server.fastmcp import FastMCP
from playwright.async_api import TimeoutError as PlaywrightTimeout
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright


mcp = FastMCP("weather-Israel")

FORECAST_URL = "https://www.weather2day.co.il/forecast"

browser = None
page = None
playwright_instance = None

def get_page():
    global browser, page, playwright_instance
    if page is None:
        playwright_instance = sync_playwright().start()
        browser = playwright_instance.chromium.launch(headless=False)
        page = browser.new_page()
    return page

@mcp.tool()
def open_weather_forecast_israel():
    """Opens the weather forecast page for Israel"""
    page=get_page()
    page.goto(FORECAST_URL)

@mcp.tool()
def enter_weather_forecast_city_israel(city: str = "ירושלים"):
    """Enters the city name in the weather forecast search box"""
    page=get_page()
    page.get_by_placeholder("מזג האוויר ב...").fill(city)

@mcp.tool()
def select_weather_forecast_city_israel(option: str):
    """Selects the city from the dropdown options"""
    page = get_page()
    page.locator("#city_search_forecastautocomplete-list").select_option(option)

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
