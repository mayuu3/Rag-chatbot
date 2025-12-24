import React, { useState, useEffect } from "react";
import Sidebar from "./components/Sidebar";
import Login from "./pages/Login";
import Chat from "./pages/Chat";
import Upload from "./pages/Upload";
import History from "./pages/History";
import "./style.css";

const API = "http://127.0.0.1:8000";

export default function App() {
  const [page, setPage] = useState("login");
  const [token, setToken] = useState("");
  const [popup, setPopup] = useState("");
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  useEffect(() => {
    const t = localStorage.getItem("rag_token");
    if (t) {
      setToken(t);
      setPage("chat");
    }
  }, []);

  const showPopup = (msg) => {
    setPopup(msg);
    setTimeout(() => setPopup(""), 2000);
  };

  const handleSetToken = (t) => {
    setToken(t);
    if (t) localStorage.setItem("rag_token", t);
    else localStorage.removeItem("rag_token");
  };

  return (
    <div className={`app-container ${sidebarCollapsed ? "collapsed" : ""}`}>
      {popup && <div className="popup neon">{popup}</div>}

      <Sidebar
        setPage={setPage}
        token={token}
        onLogout={() => { handleSetToken(""); setPage("login"); showPopup("Logged out"); }}
        collapsed={sidebarCollapsed}
        setCollapsed={setSidebarCollapsed}
      />

      <div className="main-page">
        {page === "login" && (
          <Login
            API={API}
            setToken={handleSetToken}
            setPage={setPage}
            showPopup={showPopup}
          />
        )}

        {page === "chat" && <Chat API={API} token={token} showPopup={showPopup} />}
        {page === "upload" && <Upload API={API} token={token} showPopup={showPopup} />}
        {page === "history" && <History API={API} token={token} showPopup={showPopup} />}
      </div>
    </div>
  );
}
