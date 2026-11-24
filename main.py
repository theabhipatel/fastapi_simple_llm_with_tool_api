from fastapi import FastAPI
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_groq import ChatGroq

load_dotenv()
app = FastAPI()

@app.get("/")
def home():
    return {"success":True, "message":"Welcome to the Simple LLM with Tools api."}

llm = ChatGroq(
    model="openai/gpt-oss-120b"
)

class Chat_body(BaseModel):
    user_message:str

@app.post("/api/chat")
def chat(body:Chat_body):
    response = llm.invoke(body.user_message)
    return {"success":True, "response":response}
