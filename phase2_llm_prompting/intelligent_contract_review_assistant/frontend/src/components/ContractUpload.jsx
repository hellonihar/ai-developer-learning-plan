import React, { useRef } from 'react'

export default function ContractUpload({ file, onFileChange }) {
  const inputRef = useRef(null)

  const handleDrop = (e) => {
    e.preventDefault()
    const f = e.dataTransfer.files[0]
    if (f && f.type === 'application/pdf') onFileChange(f)
  }

  const handleChange = (e) => {
    if (e.target.files[0]) onFileChange(e.target.files[0])
  }

  return (
    <div
      onDrop={handleDrop}
      onDragOver={(e) => e.preventDefault()}
      onClick={() => inputRef.current?.click()}
      className="border-2 border-dashed border-gray-700 hover:border-indigo-500 rounded-xl p-10 text-center cursor-pointer transition-colors"
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf"
        onChange={handleChange}
        className="hidden"
      />
      {file ? (
        <div>
          <p className="text-indigo-400 font-medium text-lg">{file.name}</p>
          <p className="text-gray-500 text-sm mt-1">
            {(file.size / 1024).toFixed(1)} KB
          </p>
          <p className="text-gray-600 text-xs mt-2">Click to change file</p>
        </div>
      ) : (
        <div>
          <svg className="w-12 h-12 mx-auto text-gray-600 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
          </svg>
          <p className="text-gray-400 font-medium">Drop PDF here or click to upload</p>
          <p className="text-gray-600 text-sm mt-1">PDF files only</p>
        </div>
      )}
    </div>
  )
}
