function MatchScoreBreakdown({ matchScore }) {
  if (!matchScore) {
    return (
      <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
        <p className="text-sm text-slate-500">
          Match score unavailable
        </p>
      </div>
    )
  }

  const scores = [
    {
      label: "Re-ID Similarity",
      value: matchScore.reid_similarity,
    },
    {
      label: "Plate Similarity",
      value: matchScore.plate_similarity,
    },
    {
      label: "Temporal Score",
      value: matchScore.temporal_score,
    },
    {
      label: "Route Score",
      value: matchScore.route_score,
    },
  ]

  return (
    <div className="mt-6">
      <p className="mb-3 text-sm text-slate-400">
        Match Score Breakdown
      </p>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {scores.map((score) => {
          const hasValue =
            typeof score.value === "number"

          const percentage = hasValue
            ? Math.round(score.value * 100)
            : null

          return (
            <div
              key={score.label}
              className="rounded-lg bg-slate-800 p-4"
            >
              <p className="text-xs text-slate-400">
                {score.label}
              </p>

              <p className="mt-1 text-xl font-semibold">
                {percentage !== null
                  ? `${percentage}%`
                  : "N/A"}
              </p>

              {percentage !== null && (
                <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-slate-700">
                  <div
                    className="h-full rounded-full bg-white"
                    style={{
                      width: `${percentage}%`,
                    }}
                  />
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default MatchScoreBreakdown