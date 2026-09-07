import { useEffect, useState } from "react"
import SourceBadge from "../components/SourceBadge"
import { getVerificationEvents } from "../api/client"

function SmartVerification() {
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getVerificationEvents()
      .then((data) => {
        setEvents(data.events)
      })
      .catch((error) => {
        console.error("Verification fetch error:", error)
      })
      .finally(() => {
        setLoading(false)
      })
  }, [])

  return (
    <div>
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

      {loading && (
        <p className="mt-8 text-slate-400">
          Loading verification events...
        </p>
      )}

      {!loading && events.length === 0 && (
        <div className="mt-8 rounded-xl border border-slate-800 bg-slate-900 p-6">
          <p className="text-slate-400">
            No verification events found.
          </p>
        </div>
      )}

      <div className="mt-8 space-y-4">
        {events.map((event) => (
          <div
            key={event.event_id}
            className="rounded-xl border border-slate-800 bg-slate-900 p-6"
          >
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

            <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2">
              <div className="rounded-lg bg-slate-800 p-4">
                <p className="text-xs text-slate-400">
                  Original Plate
                </p>

                <p className="mt-1 text-xl font-semibold text-red-400">
                  {event.original_plate}
                </p>
              </div>

              <div className="rounded-lg bg-slate-800 p-4">
                <p className="text-xs text-slate-400">
                  Corrected Plate
                </p>

                <p className="mt-1 text-xl font-semibold text-green-400">
                  {event.corrected_plate}
                </p>
              </div>
            </div>

            <div className="mt-4">
              <p className="text-sm text-slate-400">
                Supporting Cameras
              </p>

              <div className="mt-2 flex gap-2">
                {event.supporting_cameras.map((camera) => (
                  <span
                    key={camera}
                    className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm"
                  >
                    {camera}
                  </span>
                ))}
              </div>
            </div>

            <div className="mt-4 grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-slate-400">
                  Re-ID Similarity
                </p>

                <p className="mt-1 text-lg font-semibold">
                  {Math.round(event.reid_similarity * 100)}%
                </p>
              </div>

              <div>
                <p className="text-xs text-slate-400">
                  Verification Confidence
                </p>

                <p className="mt-1 text-lg font-semibold">
                  {Math.round(event.verification_confidence * 100)}%
                </p>
              </div>
            </div>

            <div className="mt-5 border-t border-slate-800 pt-4">
              <p className="text-xs uppercase tracking-wider text-slate-500">
                Reason
              </p>

              <p className="mt-2 text-sm text-slate-300">
                {event.reason}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default SmartVerification