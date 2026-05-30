import React, { useState } from 'react'
import ContractUpload from './components/ContractUpload'
import VoiceNoteInput from './components/VoiceNoteInput'
import RiskSummary from './components/RiskSummary'
import HighlightedClauses from './components/HighlightedClauses'
import RecommendedRevisions from './components/RecommendedRevisions'
import { analyzeContract } from './services/api'

export default function App() {
  const [file, setFile] = useState(null)
  const [instructions, setInstructions] = useState('')
  const [voiceNote, setVoiceNote] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file) return

    setLoading(true)
    setError('')
    setResult(null)

    try {
      const data = await analyzeContract(file, instructions, voiceNote)
      setResult(data)
    } catch (err) {
      const msg =
        err.response?.data?.detail || err.message || 'Analysis failed'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-950">
      <header className="border-b border-gray-800 bg-gray-900/80 backdrop-blur sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-sm font-bold">
            C
          </div>
          <h1 className="text-xl font-semibold">Contract Review Assistant</h1>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8 space-y-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          <ContractUpload file={file} onFileChange={setFile} />
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">
              Review Instructions
            </label>
            <input
              type="text"
              value={instructions}
              onChange={(e) => setInstructions(e.target.value)}
              placeholder='e.g. "Find payment risks"'
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-gray-100 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>
          <VoiceNoteInput voiceNote={voiceNote} onVoiceNoteChange={setVoiceNote} />

          <button
            type="submit"
            disabled={!file || loading}
            className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:bg-gray-700 disabled:text-gray-500 text-white font-medium py-3 px-6 rounded-lg transition-colors flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Analyzing...
              </>
            ) : (
              'Analyze Contract'
            )}
          </button>
        </form>

        {error && (
          <div className="bg-red-900/50 border border-red-800 rounded-lg p-4 text-red-300">
            {error}
          </div>
        )}

        {result && (
          <div className="space-y-6">
            <RiskSummary summary={result.risk_summary} score={result.risk_score} />
            <HighlightedClauses clauses={result.highlighted_clauses} />
            <RecommendedRevisions revisions={result.recommended_revisions} />
          </div>
        )}
      </main>
    </div>
  )
}
