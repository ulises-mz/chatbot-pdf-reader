import ReactMarkdown from "react-markdown";

export default function MessageBubble({ content, type, isTyping = false }) {
  return (
    <div className={`message-wrapper ${type}`}>
      {isTyping && (
        <div className="typing-label">
          <span className="text">Typing</span>
          <span className="dot" />
          <span className="dot" />
          <span className="dot" />
        </div>
      )}

      <div className={`message-content ${type} ${isTyping ? "disabled" : ""}`}>
        {type === "bot" ? <ReactMarkdown>{content}</ReactMarkdown> : content}
      </div>
    </div>
  );
}
