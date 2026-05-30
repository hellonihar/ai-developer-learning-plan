import { useState, useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'

const API_URL = 'http://localhost:8000'

function ChatMessage({ role, content }) {
  const isUser = role === 'user'
  return (
    <div className={`message ${isUser ? 'user' : 'assistant'}`}>
      <div className="avatar">{isUser ? '👤' : '🤖'}</div>
      <div className="bubble">
        {isUser ? (
          <p>{content}</p>
        ) : (
          <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
            {content}
          </ReactMarkdown>
        )}
      </div>
    </div>
  )
}

function ExampleCard({ example, onSelect }) {
  return (
    <div className="example-card" onClick={() => onSelect(example.problem)}>
      <div className="example-category">{example.category}</div>
      <div className="example-title">{example.title}</div>
      <div className="example-preview">
        <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
          {example.problem}
        </ReactMarkdown>
      </div>
    </div>
  )
}

export default function App() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: '🤖 Welcome to **Math Tutor Bot**! Ask me any math problem and I\'ll solve it step by step.' },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [examples, setExamples] = useState([])
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const bottomRef = useRef(null)

  useEffect(() => {
    fetch(`${API_URL}/examples`)
      .then(res => res.json())
      .then(data => setExamples(data.examples))
      .catch(() => {})
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function handleSend(e) {
    e.preventDefault()
    const trimmed = input.trim()
    if (!trimmed || loading) return

    const userMsg = { role: 'user', content: trimmed }
    const updated = [...messages, userMsg]
    setMessages(updated)
    setInput('')
    setLoading(true)

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: updated }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Request failed')
      setMessages(prev => [...prev, { role: 'assistant', content: data.reply }])
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `**Error:** ${err.message}. Please check that the backend is running.`,
      }])
    } finally {
      setLoading(false)
    }
  }

  function handleNewProblem() {
    setMessages([
      { role: 'assistant', content: '🤖 Welcome back! What math problem would you like to solve today?' },
    ])
  }

  function handleExampleSelect(problem) {
    setInput(problem)
  }

  return (
    <div className="app">
      <header className="header">
        <button className="sidebar-toggle" onClick={() => setSidebarOpen(!sidebarOpen)}>
          {sidebarOpen ? '◀' : '▶'}
        </button>
        <h1>📐 Math Tutor Bot</h1>
        <button className="new-problem-btn" onClick={handleNewProblem}>
          ➕ New Problem
        </button>
      </header>
      <div className="main">
        {sidebarOpen && (
          <aside className="sidebar">
            <h3>📚 Examples</h3>
            <p className="sidebar-hint">Click to load a problem</p>
            {examples.map((ex, i) => (
              <ExampleCard key={i} example={ex} onSelect={handleExampleSelect} />
            ))}
          </aside>
        )}
        <div className="chat-area">
          <div className="chat">
            {messages.map((msg, i) => (
              <ChatMessage key={i} role={msg.role} content={msg.content} />
            ))}
            {loading && (
              <div className="message assistant">
                <div className="avatar">🤖</div>
                <div className="bubble typing-indicator">
                  <span></span><span></span><span></span>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>
          <form className="input-bar" onSubmit={handleSend}>
            <input
              type="text"
              placeholder="Type a math problem (e.g., solve 2x + 5 = 13)..."
              value={input}
              onChange={e => setInput(e.target.value)}
              disabled={loading}
            />
            <button type="submit" disabled={loading || !input.trim()}>
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
