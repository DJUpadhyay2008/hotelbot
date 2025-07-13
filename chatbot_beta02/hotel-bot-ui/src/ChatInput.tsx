// src/ChatInput.tsx
import React, { useState } from "react";

type Props = {
    onSend: (message: string) => void;
};

const ChatInput: React.FC<Props> = ({ onSend }) => {
    const [message, setMessage] = useState("");

    const handleSend = () => {
        if (message.trim()) {
            onSend(message);
            setMessage("");
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === "Enter") handleSend();
    };

    return (
        <div style={{ display: "flex", gap: "8px", marginTop: "10px" }}>
            <input
                type="text"
                value={message}
                placeholder="Type your message..."
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                style={{
                    flex: 1,
                    padding: "10px",
                    fontSize: "16px",
                    borderRadius: "8px",
                    border: "1px solid #ccc",
                }}
            />
            <button
                onClick={handleSend}
                style={{
                    padding: "10px 16px",
                    fontSize: "16px",
                    backgroundColor: "#007bff",
                    color: "#fff",
                    border: "none",
                    borderRadius: "8px",
                    cursor: "pointer",
                }}
            >
                Send
            </button>
        </div>
    );
};

export default ChatInput;
