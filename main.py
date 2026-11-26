from fastapi import FastAPI
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_groq import ChatGroq
from tools import multipy, divide, get_location, get_weather
from agent import agent
from langgraph.types import Command

load_dotenv()
app = FastAPI()

@app.get("/")
def home():
    return {"success":True, "message":"Welcome to the Simple LLM with Tools api."}

llm = ChatGroq(
    model="openai/gpt-oss-120b"
)



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

@app.post("/api/agent/chat")
def agent_chat(body:Chat_body):
     messages = [
            ("system", "You are a helpfull assistant, please use tools to perform mathematical operation, and you must use tool for mathematical operation and other works and give ans in short but don't give any answer directly, give with at least in half line, don't explain too much, don't give answer in markdown."),
            ("human", body.user_message)
        ]

     thread_id  = "user_1"

     result = agent.invoke(
         {"messages": messages},
         config={
             "configurable":{
                 "thread_id":thread_id
             },
             "recursion_limit":10}
     )

     if result.get("__interrupt__"):
         return {
             "status":"approval required",
             "thread_id":thread_id,
             "approval": result["__interrupt__"][0].value,
             "result":result
         }

     return {
         "success": True,
         "response": result["messages"][-1].content,
         "result":result,

     }

class ApprovalBody(BaseModel):
    thread_id: str
    approved:bool

@app.post("/api/agent/approve")
def approve(body:ApprovalBody):

    result = agent.invoke(
        Command(resume=body.approved),
        config = {
            "configurable":{
                "thread_id": body.thread_id
            }
        }
    )

    return {
        "response": result["messages"][-1].content
    }