import React, { useState } from "react";
import axios from "axios";

export default function Register({ setPage, showPopup }) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const registerUser = async () => {
    try {
      const form = new FormData();
      form.append("name", name);
      form.append("email", email);
      form.append("password", password);

      await axios.post("http://127.0.0.1:8000/register", form);
      showPopup("Account Created Successfully!");
      setPage("login");
    } catch {
      showPopup("Email Already Exists!");
    }
  };

  return (
    <div className="register-card">
      <h1 className="register-title">Create Account</h1>

      <input className="login-input" placeholder="Name" onChange={e => setName(e.target.value)} />
      <input className="login-input" placeholder="Email" onChange={e => setEmail(e.target.value)} />
      <input className="login-input" type="password" placeholder="Password" onChange={e => setPassword(e.target.value)} />

      <div style={{ display: "flex", gap: "10px", marginTop: "10px" }}>
        <button className="btn-primary" onClick={registerUser}>Register</button>
        <button className="btn-secondary" onClick={() => setPage("login")}>Back</button>
      </div>
    </div>
  );
}
