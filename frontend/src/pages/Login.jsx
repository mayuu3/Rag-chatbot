import React, { useState } from "react";
import axios from "axios";

export default function Login({ API, setToken, setPage, showPopup }) {
  const [tab, setTab] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);

  const loginUser = async () => {
    if (!email || !password) return showPopup("Enter email & password");
    try {
      setLoading(true);
      const form = new FormData();
      form.append("email", email);
      form.append("password", password);

      const res = await axios.post(`${API}/login`, form);
      setToken(res.data.token);
      showPopup("Login Successful ⚡");
      setPage("chat");
    } catch {
      showPopup("Invalid Credentials ❌");
    } finally { setLoading(false); }
  };

  const registerUser = async () => {
    if (!email || !password || !name) return showPopup("Fill all fields");
    try {
      setLoading(true);
      const form = new FormData();
      form.append("name", name);
      form.append("email", email);
      form.append("password", password);

      const res = await axios.post(`${API}/register`, form);
      if (res.data.token) {
        setToken(res.data.token);
        showPopup("Registered & Logged In ⚡");
        setPage("chat");
      } else {
        showPopup("Registered Successfully");
        setTab("login");
      }
    } catch {
      showPopup("Email Already Exists ❌");
    } finally { setLoading(false); }
  };

  return (
    <div className="login-screen">
      <div className="login-card animated-card">
        <h1 className="login-title">⚡ RAG-Chatbot</h1>

        <div className="toggle-area">
          <button className={`toggle-btn ${tab === "login" ? "active" : ""}`} onClick={() => setTab("login")}>
            Login
          </button>
          <button className={`toggle-btn ${tab === "register" ? "active" : ""}`} onClick={() => setTab("register")}>
            Register
          </button>
        </div>

        {tab === "register" && (
          <input className="login-input" placeholder="Full name" value={name} onChange={e => setName(e.target.value)} />
        )}

        <input className="login-input" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} />
        <input className="login-input" type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} />

        {tab === "login" ? (
          <button className="btn-primary" onClick={loginUser} disabled={loading}>
            {loading ? "Logging..." : "Login"}
          </button>
        ) : (
          <button className="btn-primary" onClick={registerUser} disabled={loading}>
            {loading ? "Creating..." : "Create Account"}
          </button>
        )}
      </div>
    </div>
  );
}
