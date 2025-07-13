import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
import base64
import json
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
import GraphInputDTO
from langgraph.checkpoint.memory import MemorySaver
import google.generativeai as genai

# Setup Gemini
genai.configure(api_key=os.getenv("GENAI_API_KEY"))
model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")
chat_session = model.start_chat(history=[])

checkpointer = MemorySaver()
# ==== Load Menu ====
with open("menu.json", "r", encoding="utf-8") as f:
    data = json.load(f)             # JSON object ban gaya
    menu_string = json.dumps(data)  # Ab string ban gaya

print(menu_string)  # Yeh pure file ka string output karega


# ==== Chat Node ====
def chat_node(state: dict) -> dict:
    prompt = state.get("input", "")
    print("🧠 Prompt to Gemini:", prompt)

    # Strict system prompt
    system_prompt = (
        "Assume that you are a waiter in hotel based on menu answer the query of customer. if something is not in menu please " \
        "say we do not have that option "
        f"\n\nHere is the menu:\n{menu_string}"
    )

    full_prompt = f"{system_prompt}\n\nUser: {prompt}"
 
    response = chat_session.send_message(full_prompt)
    answer = response.text

    return {
        "reply": answer,
        "menu": "menu.jpeg" if "menu" in prompt.lower() else None
    }
# ✅ Global dictionary to store chat sessions per session_id
chat_sessions = {}

def chat_new_node(state: dict) -> dict:
    prompt = state.get("input", "")
    session_id = state.get("session_id")

    print("🧠 Prompt to Gemini:", prompt)

    # ✅ Reuse chat if exists, otherwise create new chat for session_id
    if session_id not in chat_sessions:
        chat_sessions[session_id] = model.start_chat(history=[])
        print(f"🆕 New chat session started for session_id: {session_id}")
    else:
        print(f"🔁 Reusing chat session for session_id: {session_id}")

    chat = chat_sessions[session_id]

    # 👇 Add system prompt only in first message
    if len(chat.history) == 0:
        system_prompt = (
            "You are a polite hotel waiter named Jarvis. Only recommend items from the menu. "
            "If something is not available, say so."
            f"\n\nHere is the menu:\n{menu_string}"
        )
        full_prompt = f"{system_prompt}\n\nUser: {prompt}"
    else:
        full_prompt = prompt

    response = chat.send_message(full_prompt)
    answer = response.text.strip()

    return {
        "reply": answer,
        "menu": "menu.jpeg" if "menu" in prompt.lower() else None
    }

# ==== Build Graph ====
builder = StateGraph(dict)
builder.add_node("chat", RunnableLambda(chat_new_node))
builder.set_entry_point("chat")
builder.add_edge("chat", END)
graph = builder.compile(checkpointer=checkpointer)

# ==== Function to Run ====
def run_graph(input_data: GraphInputDTO):
    thread_config = {"thread_id": input_data.session_id}
    state = {
        "session_id": input_data.session_id,
        "input": input_data.prompt,
        "thread_id": input_data.session_id
    }
    result = graph.invoke(state, thread_config)
    return result
