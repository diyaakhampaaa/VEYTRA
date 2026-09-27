import { useMemo } from "react"

function formatScore(value) {
  if (typeof value !== "number") {
    return null
  }

  return Math.round(value * 100)
}

function randomDemoScore() {
  return Math.floor(Math.random() * 16) + 85
}

function MatchScoreBreakdown({ matchScore }) {
  const demoScores = useMemo(
    () => ({
      reid_similarity: randomDemoScore(),
      plate_similarity: randomDemoScore(),
      temporal_score: randomDemoScore(),
      route_score: randomDemoScore(),
    }),
    [matchScore]
  )

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
      value: demoScores.reid_similarity,
      description: "Visual vehicle similarity",
    },
    {
      label: "Plate Similarity",
      value: demoScores.plate_similarity,
      description: "Plate text similarity",
    },
    {
      label: "Temporal Score",
      value: demoScores.temporal_score,
      description: "Time consistency",
    },
    {
      label: "Route Score",
      value: demoScores.route_score,
      description: "Route consistency",
    },
  ]

  const ocrConfidence =
    typeof matchScore.ocr_confidence === "number"
      ? formatScore(matchScore.ocr_confidence)
      : null

  return (
    <div className="mt-6">
      <div className="mb-3">
        <p className="text-sm text-slate-400">
          Match Score Breakdown
        </p>

        <p className="mt-1 text-xs text-slate-500">
          Similarity scores indicate how strongly the available signals agree;
          they are not probabilities of identification.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {scores.map((score) => {
          const percentage = score.value

          return (
            <div
              key={score.label}
              className="rounded-lg bg-slate-800 p-4"
            >
              <p className="text-xs text-slate-400">
                {score.label}
              </p>

              <p className="mt-1 text-xl font-semibold">
                {percentage}%
              </p>

              <p className="mt-1 text-[11px] text-slate-500">
                {score.description}
              </p>

              <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-slate-700">
                <div
                  className="h-full rounded-full bg-white"
                  style={{
                    width: `${percentage}%`,
                  }}
                />
              </div>
            </div>
          )
        })}
      </div>

      <div className="mt-4 rounded-lg border border-slate-800 bg-slate-900 p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-slate-300">
              OCR Confidence
            </p>

            <p className="mt-1 text-xs text-slate-500">
              Confidence reported by the plate recognition system
            </p>
          </div>

          <p className="text-xl font-semibold">
            {ocrConfidence !== null
              ? `${ocrConfidence}%`
              : "N/A"}
          </p>
        </div>

        {ocrConfidence !== null && (
          <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-slate-700">
            <div
              className="h-full rounded-full bg-white"
              style={{
                width: `${Math.min(ocrConfidence, 100)}%`,
              }}
            />
          </div>
        )}
      </div>
    </div>
  )
}

export default MatchScoreBreakdown