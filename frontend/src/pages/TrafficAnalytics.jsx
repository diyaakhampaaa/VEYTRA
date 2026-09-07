import { useEffect, useState } from "react"
import SourceBadge from "../components/SourceBadge"
import { getAnalytics } from "../api/client"

function TrafficAnalytics() {
  const [segments, setSegments] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getAnalytics()
      .then((data) => {
        setSegments(data.segments)
      })
      .catch((error) => {
        console.error("Analytics fetch error:", error)
      })
      .finally(() => {
        setLoading(false)
      })
  }, [])

  const totalVehicles = segments.reduce(
    (total, segment) => total + segment.vehicle_count,
    0
  )

  const averageSpeed =
    segments.length > 0
      ? segments.reduce(
          (total, segment) => total + segment.average_speed,
          0
        ) / segments.length
      : 0

  const averageCongestion =
    segments.length > 0
      ? segments.reduce(
          (total, segment) => total + segment.congestion_score,
          0
        ) / segments.length
      : 0

  const getCongestionLabel = (score) => {
    if (score >= 0.7) return "High"
    if (score >= 0.4) return "Moderate"
    return "Low"
  }

  return (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold">
            Traffic Analytics
          </h2>

          <p className="mt-2 text-slate-400">
            Analyze traffic flow, speed, and congestion.
          </p>
        </div>

        <SourceBadge source="simulated" />
      </div>

      {loading ? (
        <p className="mt-8 text-slate-400">
          Loading traffic analytics...
        </p>
      ) : (
        <>
          <div className="mt-8 grid grid-cols-1 gap-4 md:grid-cols-3">
            <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
              <p className="text-sm text-slate-400">
                Total Vehicles
              </p>

              <p className="mt-2 text-3xl font-semibold">
                {totalVehicles}
              </p>
            </div>

            <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
              <p className="text-sm text-slate-400">
                Average Speed
              </p>

              <p className="mt-2 text-3xl font-semibold">
                {averageSpeed.toFixed(1)}
                <span className="ml-1 text-sm text-slate-400">
                  km/h
                </span>
              </p>
            </div>

            <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
              <p className="text-sm text-slate-400">
                Average Congestion
              </p>

              <p className="mt-2 text-3xl font-semibold">
                {Math.round(averageCongestion * 100)}%
              </p>
            </div>
          </div>

          <div className="mt-8">
            <h3 className="mb-4 text-lg font-medium">
              Road Segments
            </h3>

            <div className="space-y-4">
              {segments.map((segment) => {
                const congestion =
                  segment.congestion_score * 100

                return (
                  <div
                    key={segment.segment_id}
                    className="rounded-xl border border-slate-800 bg-slate-900 p-5"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="text-lg font-semibold">
                          {segment.segment_id}
                        </h4>

                        <p className="mt-1 text-sm text-slate-500">
                          Updated {segment.timestamp}
                        </p>
                      </div>

                      <span className="rounded-full bg-slate-800 px-3 py-1 text-sm">
                        {getCongestionLabel(
                          segment.congestion_score
                        )}
                      </span>
                    </div>

                    <div className="mt-5 grid grid-cols-2 gap-4 md:grid-cols-3">
                      <div>
                        <p className="text-xs text-slate-400">
                          Vehicles
                        </p>

                        <p className="mt-1 text-xl font-semibold">
                          {segment.vehicle_count}
                        </p>
                      </div>

                      <div>
                        <p className="text-xs text-slate-400">
                          Average Speed
                        </p>

                        <p className="mt-1 text-xl font-semibold">
                          {segment.average_speed} km/h
                        </p>
                      </div>

                      <div>
                        <p className="text-xs text-slate-400">
                          Congestion
                        </p>

                        <p className="mt-1 text-xl font-semibold">
                          {Math.round(congestion)}%
                        </p>
                      </div>
                    </div>

                    <div className="mt-5">
                      <div className="mb-2 flex justify-between text-xs text-slate-500">
                        <span>Congestion Level</span>
                        <span>{Math.round(congestion)}%</span>
                      </div>

                      <div className="h-2 overflow-hidden rounded-full bg-slate-800">
                        <div
                          className="h-full rounded-full bg-white"
                          style={{
                            width: `${congestion}%`,
                          }}
                        />
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default TrafficAnalytics