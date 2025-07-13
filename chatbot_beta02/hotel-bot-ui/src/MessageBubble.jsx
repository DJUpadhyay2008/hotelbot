// src/MessageBubble.jsx
import React from "react";
import "./MessageBubble.css";

function MessageBubble({ sender, text }) {
    const isUser = sender === "user";

    const formatText = (text) => {
        // Convert **bold** to <strong> and line breaks to <br />
        const boldFormatted = text.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
        const withLineBreaks = boldFormatted
            .replace(/\\n/g, "<br/>") // handles double escaped \n
            .replace(/\n/g, "<br/>"); // handles single \n
        return withLineBreaks;
    };

    return (
        <div className={`bubble-container ${isUser ? "right" : "left"}`}>
            <div
                className={`bubble ${isUser ? "user-bubble" : "bot-bubble"}`}
                dangerouslySetInnerHTML={{ __html: formatText(text) }}
            />
        </div>
    );
}

export default MessageBubble;
