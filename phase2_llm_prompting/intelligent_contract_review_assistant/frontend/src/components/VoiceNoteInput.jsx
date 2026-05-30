import React, { useRef, useState } from 'react'

export default function VoiceNoteInput({ voiceNote, onVoiceNoteChange }) {
  const inputRef = useRef(null)
  const [recording, setRecording] = useState(false)
  const mediaRecorder = useRef(null)
  const chunks = useRef([])

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorder = new MediaRecorder(stream, { mimeType: 'audio/webm' })
      mediaRecorder.current = recorder
      chunks.current = []

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunks.current.push(e.data)
      }

      recorder.onstop = () => {
        const blob = new Blob(chunks.current, { type: 'audio/webm' })
        const file = new File([blob], 'voice-note.webm', { type: 'audio/webm' })
        onVoiceNoteChange(file)
        stream.getTracks().forEach((t) => t.stop())
      }

      recorder.start()
      setRecording(true)
    } catch (err) {
      alert('Microphone access denied. Upload an audio file instead.')
    }
  }

  const stopRecording = () => {
    mediaRecorder.current?.stop()
    setRecording(false)
  }

  const handleFilePick = (e) => {
    if (e.target.files[0]) onVoiceNoteChange(e.target.files[0])
  }

  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-gray-400">Voice Note (optional)</label>

      <div className="flex items-center gap-3">
        <button
          type="button"
          onMouseDown={startRecording}
          onMouseUp={stopRecording}
          onMouseLeave={recording ? stopRecording : undefined}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition-colors text-sm ${
            recording
              ? 'bg-red-900/50 border-red-700 text-red-300 animate-pulse'
              : 'bg-gray-800 border-gray-700 text-gray-300 hover:border-gray-600'
          }`}
        >
          <span className={`w-3 h-3 rounded-full ${recording ? 'bg-red-500' : 'bg-gray-500'}`} />
          {recording ? 'Recording... (release)' : 'Hold to Record'}
        </button>

        <span className="text-gray-600 text-sm">or</span>

        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          className="px-4 py-2 rounded-lg border border-gray-700 text-gray-300 hover:border-gray-600 transition-colors text-sm"
        >
          Upload Audio
        </button>
        <input ref={inputRef} type="file" accept="audio/*" onChange={handleFilePick} className="hidden" />
      </div>

      {voiceNote && (
        <p className="text-xs text-indigo-400">{voiceNote.name} ({(voiceNote.size / 1024).toFixed(1)} KB)</p>
      )}
    </div>
  )
}
