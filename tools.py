from langchain.tools import tool
import requests

@tool
def multipy(a:int, b:int) -> int:
    """Use to multiply a and b"""
    return a * b

@tool
def divide(a:int, b:int) -> int:
    """Use to divide a by b"""
    return a // b

@tool 
def get_location(city:str) -> dict:
    """Get latitude and longitude of a city."""

    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name":city,
        "count": 1,
        "language":"en",
        "format":"json"
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    print(data)

    if not data.get("results"):
        return {"error": "City location not found."}

    location = data.get("results")[0]

    return {
        "name":location.get("name"),
        "latitude":location.get("latitude"),
        "longitude":location.get("longitude"),
    }

@tool
def get_weather(latitude:float, longitude:float) -> dict:
    """Get the weather of a city using it's latitude and longitude. if you don't have latitude and longitude, please first call this tool get_location."""

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude":latitude,
        "longitude":longitude,
        "current":"temperature_2m,wind_speed_10m"
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    current = data.get("current")
    units = data.get("current_units")

    if not current:
        return {"error":"Weather data not available for this location."}

    return {
        "latitude":latitude,
        "longitude":longitude,
        "temperature_2m":current.get("temperature_2m"),
        "wind_speed_10m":current.get("wind_speed_10m"),
        "current_units":{
            "temperature_2m":units.get("temperature_2m"),
            "wind_speed_10m":units.get("wind_speed_10m"),
        }
    }
