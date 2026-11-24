from fastapi import FastAPI
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain.tools import tool

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

tools = [multipy, divide]

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
