import { useState, useRef } from 'react'

function App() {
  const [image, setImage] = useState(null)
  const [preview, setPreview] = useState(null)
  const [captions, setCaptions] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [copied, setCopied] = useState(false)
  const inputRef = useRef(null)

  function handleFile(file) {
    if (!file || !file.type.startsWith('image/')) return
    setImage(file)
    setCaptions(null)
    setError('')
    setCopied(false)
    setPreview(URL.createObjectURL(file))
  }

  function handleDrop(e) {
    e.preventDefault()
    handleFile(e.dataTransfer.files[0])
  }

  async function handleUpload() {
    if (!image) return
    setLoading(true)
    setError('')

    const form = new FormData()
    form.append('file', image)

    try {
      const res = await fetch('http://localhost:8000/caption', {
        method: 'POST',
        body: form,
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Request failed')
      }
      const data = await res.json()
      setCaptions(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  function copyAlt() {
    if (!captions?.alt_text) return
    navigator.clipboard.writeText(captions.alt_text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="app">
      <header>
        <h1>Multimodal Captioner</h1>
        <p>Upload an image to generate descriptive captions and alt-text</p>
      </header>

      <main>
        <div
          className="dropzone"
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
        >
          {preview ? (
            <img src={preview} alt="Preview" className="preview" />
          ) : (
            <div className="placeholder">
              <span className="icon">📁</span>
              <p>Drag & drop an image here, or click to browse</p>
            </div>
          )}
          <input
            ref={inputRef}
            type="file"
            accept="image/*"
            hidden
            onChange={(e) => handleFile(e.target.files[0])}
          />
        </div>

        {image && !captions && (
          <button className="btn primary" onClick={handleUpload} disabled={loading}>
            {loading ? 'Generating...' : 'Generate Caption'}
          </button>
        )}

        {error && <div className="error">{error}</div>}

        {captions && (
          <div className="results">
            <section>
              <h2>Alt Text</h2>
              <p className="alt-text">{captions.alt_text}</p>
              <button className="btn small" onClick={copyAlt}>
                {copied ? 'Copied!' : 'Copy Alt Text'}
              </button>
            </section>
            <section>
              <h2>Captions</h2>
              <ul>
                {captions.captions.map((c, i) => (
                  <li key={i}>{c}</li>
                ))}
              </ul>
            </section>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
