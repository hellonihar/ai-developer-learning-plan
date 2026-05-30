import React from 'react'

function scoreColor(score) {
  if (score >= 70) return 'text-red-400'
  if (score >= 40) return 'text-yellow-400'
  return 'text-green-400'
}

function scoreBg(score) {
  if (score >= 70) return 'bg-red-500'
  if (score >= 40) return 'bg-yellow-500'
  return 'bg-green-500'
}

export default function RiskSummary({ summary, score }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <h2 className="text-lg font-semibold text-gray-200 mb-2">Risk Summary</h2>
          <p className="text-gray-400 leading-relaxed">{summary}</p>
        </div>
        <div className="flex flex-col items-center gap-1 shrink-0">
          <div className={`w-16 h-16 rounded-full ${scoreBg(score)} bg-opacity-20 flex items-center justify-center`}>
            <span className={`text-2xl font-bold ${scoreColor(score)}`}>{score}</span>
          </div>
          <span className="text-xs text-gray-500">Risk Score</span>
        </div>
      </div>
    </div>
  )
}
