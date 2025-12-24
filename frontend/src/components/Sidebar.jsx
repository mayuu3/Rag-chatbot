import React from "react";
import {
  FiLogIn,
  FiMessageCircle,
  FiUpload,
  FiClock,
  FiLogOut,
  FiChevronLeft,
  FiChevronRight
} from "react-icons/fi";

export default function Sidebar({ setPage, token, onLogout, collapsed, setCollapsed }) {
  return (
    <div className={`sidebar neon-side ${collapsed ? "is-collapsed" : ""}`}>
      <div className="sidebar-top">
        {!collapsed && <h2 className="logo">⚡ RAG-Chatbot</h2>}
        <button className="collapse-btn" onClick={() => setCollapsed(!collapsed)}>
          {collapsed ? <FiChevronRight size={20} /> : <FiChevronLeft size={20} />}
        </button>
      </div>

      <nav className="nav-buttons">
        <button onClick={() => setPage("login")}>
          <FiLogIn size={18} />
          {!collapsed && "Login"}
        </button>

        <button onClick={() => setPage("chat")}>
          <FiMessageCircle size={18} />
          {!collapsed && "Chat"}
        </button>

        <button onClick={() => setPage("upload")}>
          <FiUpload size={18} />
          {!collapsed && "Upload Docs"}
        </button>

        <button onClick={() => setPage("history")}>
          <FiClock size={18} />
          {!collapsed && "History"}
        </button>
      </nav>

      <div className="sidebar-footer">
        <div className="status">{token ? "🟢 Logged In" : "🔴 Guest"}</div>

        {token && (
          <button className="btn-logout" onClick={onLogout}>
            <FiLogOut size={18} />
            {!collapsed && "Logout"}
          </button>
        )}
      </div>
    </div>
  );
}
