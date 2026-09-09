import { useEffect, useState } from "react"
import SourceBadge from "../components/SourceBadge"
import { getVerificationEvents } from "../api/client"

function SmartVerification() {
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)

  useEffect(() => {
    getVerificationEvents()
      .then((data) => {
        setEvents(data.events || [])
      })
      .catch((error) => {
        console.error("Verification fetch error:", error)
        setError(true)
      })
      .finally(() => {
        setLoading(false)
      })
  }, [])

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold">
            Smart Verification
          </h2>

          <p className="mt-2 text-slate-400">
            Verify and reconstruct uncertain vehicle identities.
          </p>
        </div>

        <SourceBadge source="simulated" />
      </div>

      {/* Loading */}
      {loading && (
        <p className="mt-8 text-slate-400">
          Loading verification events...
        </p>
      )}

      {/* Error */}
      {!loading && error && (
        <div className="mt-8 rounded-xl border border-slate-800 bg-slate-900 p-6">
          <p className="text-slate-400">
            Verification data unavailable. Make sure the backend is running.
          </p>
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && events.length === 0 && (
        <div className="mt-8 rounded-xl border border-slate-800 bg-slate-900 p-6">
          <p className="text-slate-400">
            No verification events found.
          </p>
        </div>
      )}

      {/* Verification Events */}
      {!loading && !error && events.length > 0 && (
        <div className="mt-8 space-y-4">
          {events.map((event) => {
            const reidScore = Math.round(
              event.reid_similarity * 100
            )

            const confidence = Math.round(
              event.verification_confidence * 100
            )

            return (
              <div
                key={event.event_id}
                className="rounded-xl border border-slate-800 bg-slate-900 p-6"
              >
                {/* Event Header */}
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-xs uppercase tracking-wider text-slate-500">
                      {event.event_id}
                    </p>

                    <h3 className="mt-1 text-lg font-semibold">
                      Plate Correction
                    </h3>
                  </div>

                  <div className="rounded-full bg-green-500/20 px-3 py-1 text-sm text-green-400">
                    Verified
                  </div>
                </div>

                {/* Plate Comparison */}
                <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2">
                  <div className="rounded-lg border border-red-500/10 bg-slate-800 p-4">
                    <p className="text-xs uppercase tracking-wider text-slate-400">
                      Original OCR Result
                    </p>

                    <p className="mt-2 text-2xl font-semibold">
                      {event.original_plate}
                    </p>

                    <p className="mt-1 text-xs text-red-400">
                      Initial observation
                    </p>
                  </div>

                  <div className="rounded-lg border border-green-500/10 bg-slate-800 p-4">
                    <p className="text-xs uppercase tracking-wider text-slate-400">
                      VEYTRA Corrected Plate
                    </p>

                    <p className="mt-2 text-2xl font-semibold">
                      {event.corrected_plate}
                    </p>

                    <p className="mt-1 text-xs text-green-400">
                      Cross-camera verified
                    </p>
                  </div>
                </div>

                {/* Verification Flow */}
                <div className="mt-6 rounded-lg bg-slate-800 p-4">
                  <p className="text-xs uppercase tracking-wider text-slate-500">
                    Verification Pipeline
                  </p>

                  <div className="mt-4 flex flex-wrap items-center gap-2">
                    <span className="rounded-lg border border-slate-700 px-3 py-2 text-sm">
                      OCR
                    </span>

                    <span className="text-slate-600">
                      →
                    </span>

                    <span className="rounded-lg border border-slate-700 px-3 py-2 text-sm">
                      Re-ID
                    </span>

                    <span className="text-slate-600">
                      →
                    </span>

                    <span className="rounded-lg border border-slate-700 px-3 py-2 text-sm">
                      Cross-Camera Match
                    </span>

                    <span className="text-slate-600">
                      →
                    </span>

                    <span className="rounded-lg bg-green-500/10 px-3 py-2 text-sm text-green-400">
                      Verified
                    </span>
                  </div>
                </div>

                {/* Supporting Cameras */}
                <div className="mt-6">
                  <p className="text-sm text-slate-400">
                    Supporting Cameras
                  </p>

                  <div className="mt-2 flex flex-wrap gap-2">
                    {event.supporting_cameras?.map((camera) => (
                      <span
                        key={camera}
                        className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm"
                      >
                        {camera}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Scores */}
                <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2">
                  <div className="rounded-lg bg-slate-800 p-4">
                    <div className="flex items-center justify-between">
                      <p className="text-sm text-slate-400">
                        Re-ID Similarity
                      </p>

                      <p className="font-semibold">
                        {reidScore}%
                      </p>
                    </div>

                    <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-700">
                      <div
                        className="h-full rounded-full bg-white"
                        style={{
                          width: `${reidScore}%`,
                        }}
                      />
                    </div>
                  </div>

                  <div className="rounded-lg bg-slate-800 p-4">
                    <div className="flex items-center justify-between">
                      <p className="text-sm text-slate-400">
                        Verification Confidence
                      </p>

                      <p className="font-semibold">
                        {confidence}%
                      </p>
                    </div>

                    <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-700">
                      <div
                        className="h-full rounded-full bg-white"
                        style={{
                          width: `${confidence}%`,
                        }}
                      />
                    </div>
                  </div>
                </div>

                {/* Reason */}
                <div className="mt-6 border-t border-slate-800 pt-5">
                  <p className="text-xs uppercase tracking-wider text-slate-500">
                    Verification Reason
                  </p>

                  <p className="mt-2 text-sm leading-6 text-slate-300">
                    {event.reason}
                  </p>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

export default SmartVerification