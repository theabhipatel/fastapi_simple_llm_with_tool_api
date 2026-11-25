from dotenv import load_dotenv
from langchain_groq import ChatGroq
from tools import multipy, divide, get_weather, get_location
from langgraph.graph import MessagesState, StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-120b"
)

tools = [multipy, divide, get_weather, get_location]

llm_with_tools = llm.bind_tools(tools)

def call_llm (state:MessagesState):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages":[response]}

graph = StateGraph(MessagesState)

graph.add_node("llm", call_llm)
graph.add_node("tools", ToolNode(tools))
graph.add_edge(START, "llm")
graph.add_conditional_edges("llm", tools_condition)
graph.add_edge("tools", "llm")

memory = InMemorySaver()

agent = graph.compile(checkpointer=memory)