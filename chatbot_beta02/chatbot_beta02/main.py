from fastapi import FastAPI
from pydantic import BaseModel
from GraphInputDTO import GraphInputDTO

from graph_logic import run_graph

from SessionStore import session_store
from SessionStore import get_or_create_session
import uuid



app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class InputPrompt(BaseModel):
    prompt: str
    

@app.post("/start")
async def generate(input_data:  GraphInputDTO):
    try:
        result = run_graph(input_data)
        return {"response": result}
    except Exception as e:
        return {"error": str(e)}

@app.post("/chat")
async def generate(input_data: GraphInputDTO):
    result = run_graph(input_data)
    return {"response": result}

    
@app.post("/chat-continue")
async def generate(input_data:  GraphInputDTO):
    print("controller running with", input_data.prompt)
    try:
        result = update_graph(input_data)
        return {"response": result}
    except Exception as e:
        return {"error": str(e)}
    
@app.get("/session")
async def session():
      response = get_or_create_session( str(uuid.uuid4()))
      return {"session": response}


