import React, { useState, useEffect } from "react";
import axios from "axios";

export default function History({ API, token, showPopup }) {
  const [rows, setRows] = useState([]);

  const loadHistory = async () => {
    try {
      const res = await axios.get(`${API}/history?token=${token}`);
      const data = res.data.history || [];

      setRows(
        data.map((h, i) => ({
          id: i + 1,
          title: h.title,
          created_at: new Date(h.created_at).toLocaleString("en-IN", { timeZone: "Asia/Kolkata" }),
        }))
      );
    } catch {
      showPopup("Failed to load history ❌");
    }
  };

  useEffect(() => { loadHistory(); }, [token]);

  return (
    <div className="login-card" style={{ width: 700 }}>
      <h1 className="login-title">📝 History</h1>

      <table className="history-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Query</th>
            <th>Date</th>
          </tr>
        </thead>

        <tbody>
          {rows.length === 0 ? (
            <tr><td colSpan={3}>No history found</td></tr>
          ) : (
            rows.map(r => (
              <tr key={r.id}>
                <td>{r.id}</td>
                <td>{r.title}</td>
                <td>{r.created_at}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
