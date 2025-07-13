
session_store = {}


# Check if session exists
def get_session(session_id: str):
    return session_store.get(session_id)

# Create a new session if not found
def get_or_create_session(session_id: str):
    if session_id not in session_store:
        session_store[session_id] = {
            "sessionId":session_id,
            "initialized": False,
            "menu_summary": None,
            "chat_history": []
        }
    return session_store[session_id]



    
# Update session
def update_session(session_id: str, key: str, value):
    session = get_or_create_session(session_id)
    session[key] = value