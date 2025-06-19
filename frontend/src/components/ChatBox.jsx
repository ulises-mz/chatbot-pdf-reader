import { useEffect, useRef } from "react";
import MessageBubble from "./MessageBubble";

export default function ChatBox({ messages }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="chat-box">
      {messages.map((msg, i) => (
        <MessageBubble key={i} type={msg.type} content={msg.content} />
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
