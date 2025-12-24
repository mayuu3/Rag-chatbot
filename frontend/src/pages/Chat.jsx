// frontend/src/pages/Chat.jsx
import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

/*
  Props:
   - API (string) e.g. "http://127.0.0.1:8000"
   - token (string) user's token (or empty)
   - showPopup (fn) to show small popups
*/

export default function Chat({ API, token, showPopup }) {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]); // { role: "user"|"bot", text: "full text", display: "revealed partial text" }
  const [loading, setLoading] = useState(false);
  const messagesEnd = useRef(null);

  // auto-scroll to bottom
  useEffect(() => {
    messagesEnd.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // helper: add a user message immediately
  const pushUserMessage = (text) => {
    setMessages((prev) => [...prev, { role: "user", text, display: text }]);
  };

  // helper: add a bot placeholder message (empty display) and return its index
  const pushBotPlaceholder = (fullText) => {
    let index;
    setMessages((prev) => {
      index = prev.length;
      return [...prev, { role: "bot", text: fullText, display: "" }];
    });
    return index;
  };

  // animate reveal: gradually update messages[index].display until full
  const animateReveal = (index, fullText) => {
    const CHUNK_SIZE = 12; // chars per tick (tweak for speed)
    const TICK_MS = 24; // ms between ticks (tweak)
    let pos = 0;

    const timer = setInterval(() => {
      pos = Math.min(pos + CHUNK_SIZE, fullText.length);
      const partial = fullText.slice(0, pos);

      setMessages((prev) => {
        const copy = prev.slice();
        if (!copy[index]) {
          clearInterval(timer);
          return prev;
        }
        copy[index] = { ...copy[index], display: partial };
        return copy;
      });

      if (pos >= fullText.length) {
        clearInterval(timer);
      }
    }, TICK_MS);
  };

  // main send
  const sendMessage = async () => {
  if (!query.trim()) return;

  const userText = query.trim();

  // Add user message
  setMessages(prev => [...prev, { role: "user", text: userText }]);
  setQuery("");
  setLoading(true);

  try {
    const form = new FormData();
    form.append("token", token || "guest_" + Math.random().toString(36).slice(2));
    form.append("query", userText);

    const res = await axios.post(`${API}/chat`, form);

    const answer = res.data.answer || "(No answer)";

    // Add bot answer CORRECTLY using prev state
    setMessages(prev => [...prev, { role: "bot", text: answer }]);

  } catch (err) {
    showPopup("Chat failed ❌");
    
    setMessages(prev => [
      ...prev, 
      { role: "bot", text: "Error: failed to get answer." }
    ]);

  } finally {
    setLoading(false);
  }
};


  // enter key handling
  const onKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!loading) sendMessage();
    }
  };

  return (
    <div className="chat-page">
      <div className="chat-card">
        <div className="chat-header">
          <h3>RAG-Chatbot ⚡</h3>
          <div className="typing-area">{loading ? "AI is typing..." : "Ready"}</div>
        </div>

        <div className="messages-area" role="log" aria-live="polite">
          {messages.map((m, i) => (
            <div key={i} className={`msg-row ${m.role}`}>
              <div className={`bubble ${m.role}`}>
                {/* Use ReactMarkdown to render the currently revealed text */}
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {m.display ?? m.text ?? ""}
                </ReactMarkdown>
              </div>
            </div>
          ))}

          <div ref={messagesEnd} />
        </div>

        <div className="chat-input">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={onKeyDown}
            placeholder="Ask anything... (Shift+Enter for newline)"
            rows={2}
          />
          <button className="btn-send" onClick={sendMessage} disabled={loading}>
            {loading ? "..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}
