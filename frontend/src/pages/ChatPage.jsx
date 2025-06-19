import { useState } from "react";
import ChatBox from "../components/ChatBox";
import InputBar from "../components/InputBar";
import Sidebar from "../components/Sidebar";
import { streamChatMessage } from "../api/chatApi";
import "../styles/chat.css";

export default function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [conversations, setConversations] = useState([
    { id: "default", name: "Conversación 1" },
  ]);
  const [activeConv, setActiveConv] = useState("default");

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    setMessages(prev => [
      ...prev,
      { type: "user", content: input },
      { type: "bot", content: "..." }
    ]);
    setInput("");
    setLoading(true);

    await streamChatMessage(
      input,
      activeConv, // ✅ Aquí se usa el ID de conversación activo
      (partial) => {
        setMessages(prev => [
          ...prev.slice(0, -1),
          { type: "bot", content: partial }
        ]);
      },
      () => setLoading(false),
      (err) => {
        setMessages(prev => [
          ...prev.slice(0, -1),
          { type: "bot", content: "❌ Error: " + err.message }
        ]);
        setLoading(false);
      }
    );
  };

  const handleNewConversation = () => {
    const newId = "conv-" + Date.now();
    const newName = `Conversación ${conversations.length + 1}`;
    setConversations(prev => [...prev, { id: newId, name: newName }]);
    setMessages([]);
    setActiveConv(newId);
  };

  const handleSelectConversation = (id) => {
    setActiveConv(id);
    setMessages([]); // En futuro: puedes cargar historial si lo deseas
  };

  const handleDeleteConversation = (id) => {
    setConversations(prev => prev.filter(c => c.id !== id));
    if (activeConv === id) {
      setMessages([]);
      setActiveConv(conversations[0]?.id || "default");
    }
  };

  return (
    <div className="chat-layout" style={{ display: "flex", height: "100%" }}>
      <Sidebar
        conversations={conversations}
        onNew={handleNewConversation}
        onSelect={handleSelectConversation}
        onDelete={handleDeleteConversation}
      />
      <div className="chat-container" style={{ flex: 1, display: "flex", flexDirection: "column" }}>
        <ChatBox messages={messages} />
        <InputBar input={input} setInput={setInput} onSend={handleSend} loading={loading} />
      </div>
    </div>
  );
}
