import React, { useState } from "react";
import axios from "axios";

export default function Upload({ API, token, showPopup }) {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");

  const uploadFile = async () => {
    if (!file) return setStatus("Select a file");

    try {
      setStatus("Uploading...");

      const f = new FormData();
      f.append("token", token || "guest_" + Math.random().toString(36).slice(2));
      f.append("file", file);

      await axios.post(`${API}/upload`, f);

      const f2 = new FormData();
      f2.append("token", token);

      const res = await axios.post(`${API}/process`, f2);

      setStatus("Processed ✔");
      showPopup("File processed ✔");
    } catch {
      showPopup("Upload failed ❌");
      setStatus("Failed ❌");
    }
  };

  return (
    <div className="upload-page">
      <div className="login-card" style={{ width: 520 }}>
        <h1 className="login-title">📁 Upload Documents</h1>

        <input type="file" onChange={(e) => setFile(e.target.files[0])} />

        <button className="btn-primary" style={{ width: "100%", marginTop: 18 }} onClick={uploadFile}>
          Upload + Process
        </button>

        {status && <p style={{ marginTop: 8 }}>{status}</p>}
      </div>
    </div>
  );
}
