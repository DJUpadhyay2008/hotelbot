# nodes/take_order_node.py

def take_order_node(state: dict) -> dict:
    user_message = state.get("foo")
    print("🔍 Full state:", state)
    print("🔍 State keys:", list(state.keys()))
    print("👉 Data received from Command:",user_message)

    # Gemini se reply lo
    print("take order called")

    return state
