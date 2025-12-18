import os
import requests
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

def get_weather(city: str) -> Dict[str, Any]:
    """
    Fetches the current weather for a given city using the OpenWeatherMap API.

    This function should be used when the user asks about current weather conditions,
    temperature, humidity, or other weather-related information for a specific city.

    Args:
        city: The name of the city for which to fetch the weather.
              Should be a valid city name (e.g., 'London', 'New York', 'Tokyo').

    Returns:
        A dictionary containing weather information including:
        - temperature: Current temperature in Celsius
        - description: Weather condition description (e.g., 'clear sky', 'rainy')
        - humidity: Humidity percentage
        - wind_speed: Wind speed in meters per second
        - city: Name of the city
        - error: Error message if API call fails (only present if there's an error)

    Raises:
        No exceptions are raised; errors are returned in the 'error' field.
    """
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        return {
            "error": "Weather API key not configured. Please set the WEATHER_API_KEY environment variable.",
            "city": city
        }

    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key, "units": "metric"}

    try:
        response = requests.get(base_url, params=params)

        if response.status_code == 401:
            return {
                "error": "Invalid API key. Please check your WEATHER_API_KEY in the .env file.",
                "city": city
            }
        elif response.status_code == 404:
            return {
                "error": f"City '{city}' not found. Please check the spelling and try again.",
                "city": city
            }
        elif response.status_code != 200:
            return {
                "error": f"Failed to retrieve weather data. Status code: {response.status_code}",
                "city": city
            }

        data = response.json()

        weather_info = {
            "city": data["name"],
            "temperature": round(data["main"]["temp"], 1),
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "country": data["sys"]["country"]
        }

        return weather_info

    except requests.exceptions.ConnectionError:
        return {
            "error": "Unable to connect to the weather service. Please check your internet connection.",
            "city": city
        }
    except requests.exceptions.Timeout:
        return {
            "error": "Request timed out while connecting to the weather service.",
            "city": city
        }
    except requests.exceptions.RequestException as e:
        return {
            "error": f"A request error occurred: {str(e)}",
            "city": city
        }
    except KeyError:
        return {
            "error": "Unexpected response format from the weather API.",
            "city": city
        }
    except Exception as e:
        return {
            "error": f"An unexpected error occurred: {str(e)}",
            "city": city
        }


def get_stock_price(symbol: str) -> Dict[str, Any]:
    """
    Fetches the current stock price for a given symbol using Alpha Vantage API.

    This function should be used when the user asks about current stock prices,
    financial market data, or stock performance for a specific company.

    Args:
        symbol: The stock symbol for which to fetch the price.
                Should be a valid stock symbol (e.g., 'AAPL', 'GOOGL', 'MSFT').

    Returns:
        A dictionary containing stock information including:
        - symbol: The stock symbol
        - price: Current stock price in USD
        - currency: Currency of the price ('USD')
        - last_updated: Date of the last price update
        - error: Error message if API call fails (only present if there's an error)

    Raises:
        No exceptions are raised; errors are returned in the 'error' field.
    """
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        return {
            "error": "Alpha Vantage API key not configured. Please set the ALPHA_VANTAGE_API_KEY environment variable.",
            "symbol": symbol
        }

    base_url = "https://www.alphavantage.co/query"
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": api_key
    }

    try:
        response = requests.get(base_url, params=params)

        if response.status_code != 200:
            return {
                "error": f"Failed to retrieve stock data. Status code: {response.status_code}",
                "symbol": symbol
            }

        data = response.json()

        # Check if the API returned an error message
        if "Error Message" in data:
            return {
                "error": f"Invalid stock symbol '{symbol}'. Please check the symbol and try again.",
                "symbol": symbol
            }

        if "Note" in data:
            return {
                "error": "API rate limit exceeded. Please try again later.",
                "symbol": symbol
            }

        quote_data = data.get("Global Quote", {})
        if not quote_data:
            return {
                "error": f"No data available for stock symbol '{symbol}'.",
                "symbol": symbol
            }

        stock_info = {
            "symbol": quote_data["01. symbol"],
            "price": float(quote_data["05. price"]),
            "currency": "USD",
            "last_updated": quote_data["07. latest trading day"]
        }

        return stock_info

    except requests.exceptions.ConnectionError:
        return {
            "error": "Unable to connect to the stock service. Please check your internet connection.",
            "symbol": symbol
        }
    except requests.exceptions.Timeout:
        return {
            "error": "Request timed out while connecting to the stock service.",
            "symbol": symbol
        }
    except requests.exceptions.RequestException as e:
        return {
            "error": f"A request error occurred: {str(e)}",
            "symbol": symbol
        }
    except (KeyError, ValueError):
        return {
            "error": "Unexpected response format from the stock API.",
            "symbol": symbol
        }
    except Exception as e:
        return {
            "error": f"An unexpected error occurred: {str(e)}",
            "symbol": symbol
        }