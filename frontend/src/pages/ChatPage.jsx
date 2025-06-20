import { useState, useEffect } from "react";
import ChatBox from "../components/ChatBox";
import InputBar from "../components/InputBar";
import Sidebar from "../components/Sidebar";
import {
  streamChatMessage,
  fetchAllConversations,
  deleteConversation,
} from "../api/chatApi";
import "../styles/chat.css";
import { exportConversationToMarkdown } from "../utils/exportChat";

export default function ChatPage() {
  // Estado para los mensajes del chat actual
  const [messages, setMessages] = useState([]);

  // Entrada de texto del usuario
  const [input, setInput] = useState("");

  // Estado de carga (true mientras se recibe respuesta)
  const [loading, setLoading] = useState(false);

  // Lista de conversaciones disponibles
  const [conversations, setConversations] = useState([
    { id: "default", name: "Conversación 1" },
  ]);

  // ID de la conversación activa
  const [activeConv, setActiveConv] = useState("default");

  // Indicador de que el bot está "escribiendo"
  const [isTyping, setIsTyping] = useState(false);

  // Información sobre tokens usados y costo estimado
  const [usage, setUsage] = useState(null);

  // Enviar mensaje al backend y manejar la respuesta por stream
  const handleSend = async () => {
    if (!input.trim() || loading) return;

    setMessages((prev) => [
      ...prev,
      { type: "user", content: input },
      { type: "bot", content: "..." },
    ]);
    setInput("");
    setLoading(true);
    setIsTyping(true);
    setUsage(null);

    await streamChatMessage(
      input,
      activeConv,
      (partialOrObject) => {
        try {
          // Si es objeto, contiene stats de uso
          const parsed = JSON.parse(partialOrObject);
          if (parsed.type === "usage") {
            setUsage(parsed.tokens);
          }
        } catch {
          // Si no se puede parsear, es contenido parcial del bot
          setMessages((prev) => [
            ...prev.slice(0, -1),
            { type: "bot", content: partialOrObject },
          ]);
        }
      },
      () => {
        setLoading(false);
        setIsTyping(false);
      },
      (err) => {
        setMessages((prev) => [
          ...prev.slice(0, -1),
          { type: "bot", content: "❌ Error: " + err.message },
        ]);
        setLoading(false);
        setIsTyping(false);
      }
    );
  };

  // Crea una nueva conversación vacía
  const handleNewConversation = () => {
    const newId = "conv-" + Date.now();
    const newName = `Conversación ${conversations.length + 1}`;
    setConversations((prev) => [...prev, { id: newId, name: newName }]);
    setMessages([]);
    setActiveConv(newId);
    setUsage(null);
  };

  // Cambia la conversación activa y carga su historial si existe
  const handleSelectConversation = (id) => {
    setActiveConv(id);
    const selectedConv = conversations.find((c) => c.id === id);
    if (selectedConv?.history) {
      setMessages(
        selectedConv.history.map((m) => ({
          type: m.role === "user" ? "user" : "bot",
          content: m.content,
        }))
      );
    } else {
      setMessages([]);
    }
    setUsage(null);
  };

  // Elimina una conversación específica
  const handleDeleteConversation = async (id) => {
    try {
      await deleteConversation(id);
      setConversations((prev) => prev.filter((c) => c.id !== id));

      if (activeConv === id) {
        const remaining = conversations.filter((c) => c.id !== id);
        const next = remaining[0]?.id || "default";
        setActiveConv(next);
        const nextConv = remaining.find((c) => c.id === next);
        if (nextConv?.history) {
          setMessages(
            nextConv.history.map((m) => ({
              type: m.role === "user" ? "user" : "bot",
              content: m.content,
            }))
          );
        } else {
          setMessages([]);
        }
      }
      setUsage(null);
    } catch (err) {
      console.error("❌ Error eliminando conversación:", err);
    }
  };

  // Exporta la conversación como archivo .md
  const handleExportConversation = (id) => {
    const conv = conversations.find((c) => c.id === id);
    if (!conv) return;

    const messagesToExport = conv.history
      ? conv.history.map((m) => ({
          type: m.role === "user" ? "user" : "bot",
          content: m.content,
        }))
      : [];

    exportConversationToMarkdown(messagesToExport, `chat-${id}.md`);
  };

  // Carga las conversaciones existentes desde el backend
  useEffect(() => {
    const loadConversations = async () => {
      const allConvs = await fetchAllConversations();
      setConversations(
        allConvs.map((c, i) => ({
          id: c.conversation_id,
          name: `Conversación ${i + 1}`,
          history: c.history,
        }))
      );

      if (allConvs.length > 0) {
        setActiveConv(allConvs[0].conversation_id);
        setMessages(
          allConvs[0].history.map((m) => ({
            type: m.role === "user" ? "user" : "bot",
            content: m.content,
          }))
        );
      }
    };

    loadConversations();
  }, []);

  return (
    <div className="chat-layout" style={{ display: "flex", height: "100%" }}>
      <Sidebar
        conversations={conversations}
        onNew={handleNewConversation}
        onSelect={handleSelectConversation}
        onDelete={handleDeleteConversation}
        onExport={handleExportConversation}
        activeConv={activeConv}
      />

      <div
        className="chat-container"
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
        }}
      >
        {/* Componente principal que renderiza los mensajes */}
        <ChatBox messages={messages} isTyping={isTyping} />

        {/* Visualización de uso de tokens y costo aproximado */}
        {usage && (
          <div
            style={{
              textAlign: "center",
              fontSize: "13px",
              color: "#9ca3af",
              marginBottom: "4px",
              fontStyle: "italic",
            }}
          >
            🔢 {usage.total_tokens} tokens | 💵 $
            {usage.estimated_cost_usd.toFixed(5)}
          </div>
        )}

        {/* Barra de entrada de texto y botón de enviar */}
        <InputBar
          input={input}
          setInput={setInput}
          onSend={handleSend}
          loading={loading}
        />
      </div>
    </div>
  );
}
