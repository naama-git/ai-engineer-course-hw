from todoService import TodoService
from agentService import agent
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str


@app.post("/chat")
def chat_with_agent(request: QueryRequest):
    
    response = agent(request.query)
    return {"status": "success", "response": response}

@app.get("/")
def read_root():
    return {"message": "Todo AI Agent API is running!"}
