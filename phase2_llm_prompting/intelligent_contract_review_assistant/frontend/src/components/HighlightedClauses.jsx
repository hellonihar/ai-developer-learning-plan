import React from 'react'

const riskColors = {
  high: 'border-red-800 bg-red-950/30',
  medium: 'border-yellow-800 bg-yellow-950/30',
  low: 'border-green-800 bg-green-950/30',
}

const riskBadge = {
  high: 'bg-red-900/60 text-red-300',
  medium: 'bg-yellow-900/60 text-yellow-300',
  low: 'bg-green-900/60 text-green-300',
}

export default function HighlightedClauses({ clauses }) {
  if (!clauses || clauses.length === 0) return null

  return (
    <div>
      <h2 className="text-lg font-semibold text-gray-200 mb-4">Highlighted Clauses</h2>
      <div className="space-y-3">
        {clauses.map((c, i) => (
          <div key={i} className={`border-l-4 rounded-lg p-4 ${riskColors[c.risk_level]}`}>
            <div className="flex items-start justify-between gap-3">
              <p className="text-sm font-medium text-gray-200 flex-1">{c.clause}</p>
              <span className={`text-xs font-medium px-2 py-0.5 rounded-full shrink-0 ${riskBadge[c.risk_level]}`}>
                {c.risk_level}
              </span>
            </div>
            <p className="text-sm text-gray-400 mt-2">{c.explanation}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
