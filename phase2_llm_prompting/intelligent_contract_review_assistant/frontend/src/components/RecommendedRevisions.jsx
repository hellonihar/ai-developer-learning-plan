import React from 'react'

export default function RecommendedRevisions({ revisions }) {
  if (!revisions || revisions.length === 0) return null

  return (
    <div>
      <h2 className="text-lg font-semibold text-gray-200 mb-4">Recommended Revisions</h2>
      <div className="space-y-3">
        {revisions.map((r, i) => (
          <div key={i} className="border border-gray-800 rounded-xl p-5">
            <p className="text-sm font-medium text-indigo-400 mb-3">{r.clause}</p>

            <div className="space-y-2">
              <div>
                <span className="text-xs text-gray-500 uppercase tracking-wide">Current</span>
                <p className="text-sm text-red-300 bg-red-950/30 border border-red-900/50 rounded-lg p-3 mt-1">
                  {r.current_text}
                </p>
              </div>

              <div>
                <span className="text-xs text-gray-500 uppercase tracking-wide">Suggested</span>
                <p className="text-sm text-green-300 bg-green-950/30 border border-green-900/50 rounded-lg p-3 mt-1">
                  {r.suggested_revision}
                </p>
              </div>
            </div>

            <p className="text-xs text-gray-500 mt-3">{r.reason}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
