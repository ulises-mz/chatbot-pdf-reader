import { useState } from "react";
import "../styles/Sidebar.css";

export default function Sidebar({ conversations, onNew, onSelect, onDelete }) {
  const [isOpen, setIsOpen] = useState(true);
  const [activeMenu, setActiveMenu] = useState(null);

  const toggleMenu = (id) => {
    setActiveMenu(prev => (prev === id ? null : id));
  };

  return (
    <div className={`sidebar ${isOpen ? "open" : "closed"}`}>
      <div className="sidebar-header">
        <button className="toggle-btn" onClick={() => setIsOpen(!isOpen)} title={isOpen ? "Colapsar" : "Expandir"}>
          {isOpen ? "←" : "→"}
        </button>
        {isOpen && <span style={{ fontWeight: "bold" }}>ChatGPT</span>}
      </div>

      <div className="sidebar-body">
        <button
          className={`new-chat ${isOpen ? "full" : "icon-only"}`}
          onClick={onNew}
          title="Nueva conversación"
        >
          {isOpen ? "+ Nueva conversación" : "➕"}
        </button>

        {isOpen && conversations.map((conv) => (
          <div key={conv.id} className="chat-item-wrapper">
            <button
              className="chat-item"
              onClick={() => onSelect(conv.id)}
              title={conv.name}
            >
              {conv.name}
            </button>
            <div className="menu-wrapper">
              <button
                className="menu-btn"
                onClick={() => toggleMenu(conv.id)}
                title="Opciones"
              >
                ⋯
              </button>
              {activeMenu === conv.id && (
                <div className="menu-dropdown">
                  <button onClick={() => { onDelete(conv.id); setActiveMenu(null); }}>Eliminar</button>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
