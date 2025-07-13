// src/App.tsx
import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import ChatInput from "./ChatInput";
import MessageBubble from "./MessageBubble";

type Message = {
  sender: "user" | "bot";
  text: string;
};

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessionId] = useState(() => Date.now().toString());
  const [isTyping, setIsTyping] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (userText: string) => {
    setMessages((prev) => [...prev, { sender: "user", text: userText }]);
    setIsTyping(true);

    try {
      const res = await axios.post("http://localhost:8000/start", {
        session_id: sessionId,
        prompt: userText,
      });

      const botReply = res.data.response.reply;

      setMessages((prev) => [...prev, { sender: "bot", text: botReply }]);

      if (res.data.response.confirmed_order) {
        const orderJSON = JSON.stringify(res.data.response.confirmed_order, null, 2);
        setMessages((prev) => [
          ...prev,
          { sender: "bot", text: `✅ Confirmed Order:\n${orderJSON}` },
        ]);
      }
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "❌ Error talking to server" },
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  // 👇 Show Menu Image on button click
  const handleShowMenu = () => {
    setMessages((prev) => [
      ...prev,
      { sender: "bot", text: "__show_menu_image__" },
    ]);
  };

  return (
    <div
      style={{
        width: "100%",
        maxWidth: "500px",
        height: "90vh",
        background: "#fff",
        padding: "1rem",
        borderRadius: "16px",
        boxShadow: "0 0 24px rgba(0,0,0,0.3)",
        display: "flex",
        flexDirection: "column",
        gap: "1rem",
      }}
    >
      {/* 👇 Header + Show Menu Button */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h2 style={{ margin: 0 }}>
          🍽️ <span style={{ color: "#007bff" }}>Highway Adda Waiter</span>
        </h2>
        <button
          onClick={handleShowMenu}
          style={{
            padding: "6px 12px",
            fontSize: "14px",
            backgroundColor: "#007bff",
            color: "#fff",
            border: "none",
            borderRadius: "6px",
            cursor: "pointer",
          }}
        >
          📋 Show Menu
        </button>
      </div>

      {/* 👇 Chatbox */}
      <div
        style={{
          flexGrow: 1,
          border: "1px solid #ddd",
          padding: "10px",
          borderRadius: "8px",
          overflowY: "auto",
          backgroundColor: "#fdfdfd",
        }}
      >
        {messages.map((msg, idx) =>
          msg.text === "__show_menu_image__" ? (
            <div
              key={idx}
              style={{ textAlign: "center", margin: "10px 0" }}
            >
              <img
                src="/menu.jpeg"
                alt="Menu"
                style={{ width: "100%", borderRadius: "10px" }}
              />
            </div>
          ) : (
            <MessageBubble key={idx} sender={msg.sender} text={msg.text} />
          )
        )}

        {isTyping && (
          <div
            style={{
              fontStyle: "italic",
              color: "#888",
              paddingLeft: "8px",
              marginTop: "8px",
            }}
          >
            Thinking....
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      <ChatInput onSend={handleSend} />
    </div>
  );
}

export default App;
