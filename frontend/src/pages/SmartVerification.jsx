import { useEffect, useState } from "react"
import { getVerificationEvents } from "../api/client"
import SourceBadge from "../components/SourceBadge"

function SmartVerification() {
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    const loadEvents = async () => {
      try {
        setLoading(true)
        const data = await getVerificationEvents()

        setEvents(
          Array.isArray(data)
            ? data
            : data?.events || data?.results || []
        )
      } catch (err) {
        setError("Unable to load verification events.")
      } finally {
        setLoading(false)
      }
    }

    loadEvents()
  }, [])

  const suspiciousCount = events.filter(
    (event) =>
      event.verification_status === "suspicious" ||
      event.status === "suspicious"
  ).length

  return (
    <div className="min-h-screen bg-[#02070b] text-white">
      {/* HEADER */}
      <div className="mb-8 flex items-end justify-between">
        <div>
          <div className="mb-2 flex items-center gap-2 text-xs uppercase tracking-[0.28em] text-cyan-400">
            <span className="veytra-live-dot" />
            Verification Intelligence
          </div>

          <h1 className="text-3xl font-semibold tracking-tight">
            Smart Plate Verification
          </h1>

          <p className="mt-2 max-w-2xl text-sm text-slate-400">
            Cross-camera verification for suspicious, corrected, and
            low-confidence vehicle plate observations.
          </p>
        </div>

        <div className="veytra-panel px-5 py-3">
          <div className="text-[10px] uppercase tracking-[0.2em] text-slate-500">
            Verification Nodes
          </div>

          <div className="mt-1 flex items-center gap-2">
            <span className="veytra-live-dot" />
            <span className="text-sm text-cyan-300">
              Pipeline Active
            </span>
          </div>
        </div>
      </div>

      {/* SUMMARY */}
      <div className="mb-8 grid grid-cols-1 gap-4 md:grid-cols-3">
        <div className="veytra-panel veytra-hud p-5">
          <div className="text-[10px] uppercase tracking-[0.2em] text-slate-500">
            Verification Events
          </div>

          <div className="mt-3 text-3xl font-semibold">
            {loading ? "—" : events.length}
          </div>

          <div className="mt-2 text-xs text-slate-500">
            Cross-camera observations processed
          </div>
        </div>

        <div className="veytra-panel veytra-hud p-5">
          <div className="text-[10px] uppercase tracking-[0.2em] text-slate-500">
            Suspicious Reads
          </div>

          <div className="mt-3 text-3xl font-semibold text-amber-300">
            {loading ? "—" : suspiciousCount}
          </div>

          <div className="mt-2 text-xs text-slate-500">
            Requiring verification review
          </div>
        </div>

        <div className="veytra-panel veytra-hud p-5">
          <div className="text-[10px] uppercase tracking-[0.2em] text-slate-500">
            Verification Mode
          </div>

          <div className="mt-3 text-lg font-medium text-cyan-300">
            Multi-Camera
          </div>

          <div className="mt-2 text-xs text-slate-500">
            OCR + Re-ID + temporal evidence
          </div>
        </div>
      </div>

      {/* ERROR */}
      {error && (
        <div className="mb-6 border border-red-400/20 bg-red-400/5 px-5 py-4 text-sm text-red-300">
          {error}
        </div>
      )}

      {/* LOADING */}
      {loading && (
        <div className="veytra-panel flex min-h-[220px] items-center justify-center">
          <div className="text-sm text-slate-500">
            Loading verification intelligence...
          </div>
        </div>
      )}

      {/* EMPTY */}
      {!loading && !error && events.length === 0 && (
        <div className="veytra-panel veytra-hud flex min-h-[260px] flex-col items-center justify-center text-center">
          <div className="mb-4 flex h-12 w-12 items-center justify-center border border-cyan-400/20 bg-cyan-400/5">
            <span className="text-xl text-cyan-400">✓</span>
          </div>

          <h2 className="text-lg font-medium">
            No verification anomalies detected
          </h2>

          <p className="mt-2 max-w-md text-sm text-slate-500">
            The verification pipeline has not returned any events requiring
            review.
          </p>
        </div>
      )}

      {/* EVENTS */}
      {!loading && events.length > 0 && (
        <div className="space-y-4">
          {events.map((event, index) => {
            const originalPlate =
              event.original_plate ||
              event.plate ||
              event.originalPlate ||
              "UNKNOWN"

            const correctedPlate =
              event.corrected_plate ||
              event.correctedPlate ||
              event.corrected ||
              "N/A"

            const confidence =
              event.verification_confidence ??
              event.confidence ??
              null

            const reidSimilarity =
              event.reid_similarity ??
              event.match_score?.reid_similarity ??
              null

            const supportingCameras =
              event.supporting_cameras ||
              event.supportingCameras ||
              []

            const reason =
              event.reason ||
              event.verification_reason ||
              "Cross-camera verification evidence available."

            const suspicious =
              event.verification_status === "suspicious" ||
              event.status === "suspicious" ||
              originalPlate !== correctedPlate

            return (
              <div
                key={event.event_id || event.id || index}
                className="veytra-panel veytra-panel-hover veytra-hud overflow-hidden"
              >
                {/* TOP BAR */}
                <div className="flex flex-col gap-4 border-b border-cyan-400/10 p-5 lg:flex-row lg:items-center lg:justify-between">
                  <div className="flex items-center gap-4">
                    <div
                      className={`flex h-10 w-10 items-center justify-center border ${
                        suspicious
                          ? "border-amber-400/20 bg-amber-400/5 text-amber-300"
                          : "border-cyan-400/20 bg-cyan-400/5 text-cyan-300"
                      }`}
                    >
                      {suspicious ? "!" : "✓"}
                    </div>

                    <div>
                      <div className="text-[10px] uppercase tracking-[0.2em] text-slate-500">
                        Verification Event
                      </div>

                      <div className="mt-1 font-mono text-sm text-slate-300">
                        {event.event_id || event.id || `EVENT-${index + 1}`}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <span
                      className={`border px-3 py-1 text-[10px] uppercase tracking-[0.16em] ${
                        suspicious
                          ? "border-amber-400/20 bg-amber-400/5 text-amber-300"
                          : "border-cyan-400/20 bg-cyan-400/5 text-cyan-300"
                      }`}
                    >
                      {suspicious ? "Review Required" : "Verified"}
                    </span>

                    {event.source && (
                      <SourceBadge source={event.source} />
                    )}
                  </div>
                </div>

                {/* BODY */}
                <div className="grid gap-6 p-5 lg:grid-cols-[1.1fr_1fr_1fr]">
                  {/* PLATE */}
                  <div>
                    <div className="text-[10px] uppercase tracking-[0.2em] text-slate-500">
                      Plate Observation
                    </div>

                    <div className="mt-4 flex items-center gap-4">
                      <div>
                        <div className="font-mono text-xl tracking-wider text-slate-300">
                          {originalPlate}
                        </div>

                        <div className="mt-1 text-[10px] uppercase tracking-wider text-slate-600">
                          Original OCR
                        </div>
                      </div>

                      {correctedPlate !== "N/A" &&
                        correctedPlate !== originalPlate && (
                          <>
                            <div className="text-cyan-500/50">→</div>

                            <div>
                              <div className="font-mono text-xl tracking-wider text-cyan-300">
                                {correctedPlate}
                              </div>

                              <div className="mt-1 text-[10px] uppercase tracking-wider text-slate-600">
                                Corrected
                              </div>
                            </div>
                          </>
                        )}
                    </div>
                  </div>

                  {/* EVIDENCE */}
                  <div>
                    <div className="text-[10px] uppercase tracking-[0.2em] text-slate-500">
                      Evidence
                    </div>

                    <div className="mt-4 space-y-3">
                      <div className="flex items-center justify-between border-b border-white/5 pb-2">
                        <span className="text-xs text-slate-500">
                          Re-ID similarity
                        </span>

                        <span className="font-mono text-sm text-cyan-300">
                          {reidSimilarity !== null
                            ? `${(Number(reidSimilarity) * 100).toFixed(1)}%`
                            : "N/A"}
                        </span>
                      </div>

                      <div className="flex items-center justify-between border-b border-white/5 pb-2">
                        <span className="text-xs text-slate-500">
                          Verification confidence
                        </span>

                        <span className="font-mono text-sm text-cyan-300">
                          {confidence !== null
                            ? `${(Number(confidence) * 100).toFixed(1)}%`
                            : "N/A"}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* CAMERAS */}
                  <div>
                    <div className="text-[10px] uppercase tracking-[0.2em] text-slate-500">
                      Supporting Cameras
                    </div>

                    <div className="mt-4 flex flex-wrap gap-2">
                      {Array.isArray(supportingCameras) &&
                      supportingCameras.length > 0 ? (
                        supportingCameras.map((camera, cameraIndex) => {
                          const cameraName =
                            typeof camera === "string"
                              ? camera
                              : camera.camera_id ||
                                camera.cameraId ||
                                `CAM_${cameraIndex + 1}`

                          return (
                            <span
                              key={cameraIndex}
                              className="border border-cyan-400/10 bg-cyan-400/5 px-3 py-2 font-mono text-xs text-cyan-300"
                            >
                              {cameraName}
                            </span>
                          )
                        })
                      ) : (
                        <span className="text-xs text-slate-600">
                          No supporting camera data
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* REASON */}
                <div className="border-t border-cyan-400/10 bg-black/10 px-5 py-4">
                  <div className="flex gap-3">
                    <span className="text-cyan-400">/</span>

                    <div>
                      <div className="text-[10px] uppercase tracking-[0.2em] text-slate-600">
                        Verification Reason
                      </div>

                      <p className="mt-1 text-sm leading-6 text-slate-400">
                        {reason}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* FOOTER */}
      <div className="mt-8 flex items-center justify-between border-t border-cyan-400/10 pt-4 text-[10px] uppercase tracking-[0.18em] text-slate-600">
        <span>VEYTRA / Smart Verification</span>
        <span>OCR • Re-ID • Temporal Evidence</span>
      </div>
    </div>
  )
}

export default SmartVerification