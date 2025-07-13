# session_manager.py

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

class SessionManager:
    def __init__(self):
        self.sessions = {}

    def get_or_create_chain(self, session_id: str):
        if session_id not in self.sessions:
            llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro-preview-03-25")
            memory = ConversationBufferMemory(return_messages=True)
            chain = ConversationChain(llm=llm, memory=memory)
            self.sessions[session_id] = chain
        return self.sessions[session_id]
