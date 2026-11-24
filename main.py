from fastapi import FastAPI
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()
app = FastAPI()

@app.get("/")
def home():
    return {"success":True, "message":"Welcome to the Simple LLM with Tools api."}

class Chat_body(BaseModel):
    user_message:str

@app.post("/api/chat")
def chat(body:Chat_body):
    return {"body":body}
