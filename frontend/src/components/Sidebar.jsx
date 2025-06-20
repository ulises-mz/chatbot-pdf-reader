import React, { useState } from 'react';
import {
  FiPlus, FiMessageSquare, FiChevronLeft, FiChevronRight,
  FiMoreVertical, FiTrash2, FiSettings, FiUser
} from 'react-icons/fi';
import { HiMenuAlt2 } from "react-icons/hi";
import { TbMessageCirclePlus } from "react-icons/tb";
import '../styles/Sidebar.css';

const Sidebar = ({ conversations, onNew, onSelect, onDelete, onExport, activeConv }) => {

  const [isOpen, setIsOpen] = useState(true);
  const [activeMenu, setActiveMenu] = useState(null);

  const toggleMenu = (id) => {
    setActiveMenu(prev => (prev === id ? null : id));
  };

  const toggleSidebar = () => {
    setIsOpen(!isOpen);
  };

  return (
    <>
      <div className={`sidebar ${isOpen ? "open" : "closed"}`}>
        <div className="sidebar-decor"></div>
        <div className="sidebar-header">
          <div className="app-name">
            <div className="app-icon">
              <div className="gradient-icon">
                <FiMessageSquare />
              </div>
            </div>
            {isOpen && <span>MCW AI</span>}
          </div>
          <button
            className="toggle-btn"
            onClick={toggleSidebar}
            title={isOpen ? "Collapse" : "Expand"}
          >
            {isOpen ? <FiChevronLeft /> : <FiChevronRight />}
          </button>
        </div>

        <div className="sidebar-body">
          <button
            className={`new-chat ${isOpen ? "" : "icon-only"}`}
            title="New conversation"
            onClick={onNew}
          >
            {isOpen ? (
              <>
                <FiPlus />
                <span>New conversation</span>
              </>
            ) : <FiPlus />}
          </button>

          {isOpen && (
            <div className="chats-container">
              <h3>Recent conversations</h3>
              {conversations.map((conv, i) => (
                <div
                  key={conv.id}
                  className={`chat-item-wrapper ${activeConv === conv.id ? "active" : ""}`}
                  onClick={() => onSelect(conv.id)}
                >
                  <button className="chat-item" title={conv.name || `Conversation ${i + 1}`}>
                    <FiMessageSquare className="chat-icon" />
                    <span>{conv.name || `Conversation ${i + 1}`}</span>
                  </button>
                  <div className="menu-wrapper">
                    <button
                      className="menu-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleMenu(conv.id);
                      }}
                      title="Options"
                    >
                      <FiMoreVertical />
                    </button>
                    {activeMenu === conv.id && (
  <div className="menu-dropdown">

    <button onClick={() => onExport(conv.id)}>
      📤
      <span>Export</span>
    </button>
    <button className="delete" onClick={() => onDelete(conv.id)}>
      <FiTrash2 />
      <span>Delete</span>
    </button>
  </div>
)}

                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="sidebar-footer">
          <div className="user-profile">
            <div className="user-avatar">
              <FiUser />
            </div>
            {isOpen && (
              <div className="user-info">
                <div className="user-name">John Smith</div>
                <div className="user-status">Premium Account</div>
              </div>
            )}
            {isOpen && <FiSettings className="settings-icon" />}
          </div>
          {isOpen && <div className="version">v2.4.1</div>}
        </div>
      </div>

      {!isOpen && (
        <div className="mobile-navbar">
          <button className="nav-button" onClick={toggleSidebar} title="Open menu">
            <HiMenuAlt2 />
          </button>
          <button className="nav-button" onClick={onNew} title="New conversation">
            <TbMessageCirclePlus />
          </button>
        </div>
      )}
    </>
  );
};

export default Sidebar;
