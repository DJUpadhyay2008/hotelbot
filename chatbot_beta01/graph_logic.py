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
    data = json.load(f)
    menu_string = json.dumps(data)

print(menu_string)

# ==== Chat Node ====
def chat_node(state: dict) -> dict:
    prompt = state.get("input", "")
    print("🧠 Prompt to Gemini:", prompt)

    system_prompt = (
        "Assume that you are a polite waiter in a hotel. Answer customer queries based only on the given menu. "
        "If something is not in the menu, say 'Sorry, we do not have that option.'\n\n"
        f"Here is the menu:\n{menu_string}\n\n"
        "When a customer gives an order, first reply politely. Then extract only valid items from the menu "
        "and return them in this JSON format:\n"
        "{ \"items\": [ {\"name\": \"ItemName\", \"price\": Price } ], \"total_price\": TotalPrice }\n"
        "If no valid item is found, do not return JSON.\n"
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
    import re
    prompt = state.get("input", "")
    session_id = state.get("session_id")

    print("🧠 Prompt to Gemini:", prompt)

    if session_id not in chat_sessions:
        chat_sessions[session_id] = model.start_chat(history=[])
        print(f"🆕 New chat session started for session_id: {session_id}")
    else:
        print(f"🔁 Reusing chat session for session_id: {session_id}")

    chat = chat_sessions[session_id]

    if len(chat.history) == 0:
        system_prompt = (
            "You are a polite hotel waiter named Jarvis. Only recommend items from the menu. "
            "If something is not available, say so.\n\n"
            f"Here is the menu:\n{menu_string}\n\n"
            "When a customer gives an order, first reply politely. Then extract only valid items from the menu "
            "and return them in this JSON format:\n"
            "{ \"items\": [ {\"name\": \"ItemName\", \"price\": Price } ], \"total_price\": TotalPrice }\n"
            "If no valid item is found, do not return JSON.\n"
        )
        full_prompt = f"{system_prompt}\n\nUser: {prompt}"
    else:
        full_prompt = prompt

    response = chat.send_message(full_prompt)
    answer = response.text.strip()

    # ✅ Robust JSON extraction logic
    order = {}
    try:
        matches = re.findall(r"```(?:json)?\s*({[\s\S]*?})\s*```", answer)
        if matches:
            for match in matches:
                try:
                    order = json.loads(match)
                    print("✅ Order extracted from Gemini response (code block):", order)
                    break
                except json.JSONDecodeError:
                    continue
        else:
            match = re.search(r'\{[\s\S]*?"items"[\s\S]*?\}', answer)
            if match:
                order = json.loads(match.group())
                print("✅ Order extracted from fallback match:", order)
    except Exception as e:
        print("❌ Failed to extract order JSON:", e)

    return {
        "reply": answer,
        "menu": "menu.jpeg" if "menu" in prompt.lower() else None,
        "order": order
    }

def confirm_order_node(state: dict) -> dict:
    session_id = state.get("session_id")

    if session_id not in chat_sessions:
        chat_sessions[session_id] = model.start_chat(history=[])
    chat = chat_sessions[session_id]

    current_order = state.get("order", {})
    if not current_order or "items" not in current_order or not current_order["items"]:
        return {"reply": "Dutta Bhai, abhi tak koi order diya hi nahi gaya."}

    order_items = current_order["items"]
    total_price = current_order["total_price"]

    order_summary = ", ".join([f'{item["name"]} (₹{item["price"]})' for item in order_items])
    prompt = (
        f"Aapne yeh order diya hai: {order_summary} | Total: ₹{total_price}.\n"
        f"Kya aap is order ko confirm karte hain? (yes/no)"
    )

    response = chat.send_message(prompt)
    answer = response.text.strip().lower()

    if "yes" in answer or "confirm" in answer:
        return {
            "reply": f"Shukriya Dutta Bhai! Order confirm ho gaya ✅",
            "confirmed_order": {
                "items": order_items,
                "total_price": total_price
            }
        }
    else:
        return {
            "reply": "Order cancel kar diya gaya Dutta Bhai ❌"
        }

# ==== Build Graph ====
builder = StateGraph(dict)

builder.add_node("chat", RunnableLambda(chat_new_node))
builder.add_node("confirm_order", RunnableLambda(confirm_order_node))

builder.set_entry_point("chat")

def should_confirm(state: dict) -> bool:
    order = state.get("order", {})
    return bool(order and "items" in order and len(order["items"]) > 0)

builder.add_conditional_edges(
    "chat",
    lambda state: "confirm_order" if should_confirm(state) else END,
    {
        "confirm_order": "confirm_order",
        END: END
    }
)

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
