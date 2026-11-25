from fastapi import FastAPI
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain.tools import tool
import requests

load_dotenv()
app = FastAPI()

@app.get("/")
def home():
    return {"success":True, "message":"Welcome to the Simple LLM with Tools api."}

llm = ChatGroq(
    model="openai/gpt-oss-120b"
)

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


tools = [multipy, divide, get_location, get_weather]

llm_with_tools = llm.bind_tools(tools)

tools_map = {t.name:t for t in tools}

class Chat_body(BaseModel):
    user_message:str

@app.post("/api/chat")
def chat(body:Chat_body):
    messages = [
        ("system", "You are a helpfull assistant, please use tools to perform mathematical operation, and you must use tool for mathematical operation and give ans in short but don't give any answer directly, give with at least in half line, don't explain too much, don't give answer in markdown."),
        ("human", body.user_message)
    ]

    while True:
        response = llm_with_tools.invoke(messages)
        messages.append(response)

        print("response ->", response)

        if not response.tool_calls:
            break

        for tool_call in response.tool_calls:
            selected_tool = tools_map[tool_call["name"]]
            result = selected_tool.invoke(tool_call)
            messages.append(result)

    return {"success":True, "response":response.content, "messages": messages}
