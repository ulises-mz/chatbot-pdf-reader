import { useEffect, useRef } from "react";
import MessageBubble from "./MessageBubble";

export default function ChatBox({ messages, isTyping }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const isEmpty = messages.length === 0;

  return (
    <div className="chat-box-scroll">
      <div className="chat-box">
        <div className="chat-box-inner">
          {isEmpty ? (
            <div className="welcome-screen">
              <h1>Hi, I'm MCW ChatBot.</h1>
              <p>How can I help you today?</p>
            </div>
          ) : (
            <>
              {messages.map((msg, i) => {
                const isLast = i === messages.length - 1;
                return (
                  <MessageBubble
                    key={i}
                    type={msg.type}
                    content={msg.content}
                    isTyping={isTyping && msg.type === "bot" && isLast}
                  />
                );
              })}
              <div ref={bottomRef} />
            </>
          )}
        </div>
      </div>
    </div>
  );
}
