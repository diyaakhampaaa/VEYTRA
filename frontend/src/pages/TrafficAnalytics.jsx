import { useEffect, useState } from "react"
import SourceBadge from "../components/SourceBadge"
import { getAnalytics } from "../api/client"

function TrafficAnalytics() {
  const [segments, setSegments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)

  useEffect(() => {
    getAnalytics()
      .then((data) => {
        setSegments(data.segments || [])
      })
      .catch((error) => {
        console.error("Analytics fetch error:", error)
        setError(true)
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

  if (loading) {
    return (
      <div>
        <h2 className="text-2xl font-semibold">
          Traffic Analytics
        </h2>

        <p className="mt-2 text-slate-400">
          Analyze traffic flow, speed, and congestion.
        </p>

        <p className="mt-8 text-slate-400">
          Loading traffic analytics...
        </p>
      </div>
    )
  }

  if (error) {
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

        <div className="mt-8 rounded-xl border border-slate-800 bg-slate-900 p-6">
          <p className="text-slate-400">
            Traffic analytics unavailable. Make sure the backend is running.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div>
      {/* Header */}
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

      {/* Summary Cards */}
      <div className="mt-8 grid grid-cols-1 gap-4 md:grid-cols-3">
        <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
          <p className="text-sm text-slate-400">
            Total Vehicles
          </p>

          <p className="mt-2 text-3xl font-semibold">
            {totalVehicles}
          </p>

          <p className="mt-1 text-xs text-slate-500">
            Across monitored segments
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

          <p className="mt-1 text-xs text-slate-500">
            Network-wide average
          </p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
          <p className="text-sm text-slate-400">
            Average Congestion
          </p>

          <p className="mt-2 text-3xl font-semibold">
            {Math.round(averageCongestion * 100)}%
          </p>

          <p className="mt-1 text-xs text-slate-500">
            Across monitored segments
          </p>
        </div>
      </div>

      {/* Road Segments */}
      <div className="mt-8">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h3 className="text-lg font-medium">
              Road Segments
            </h3>

            <p className="mt-1 text-sm text-slate-500">
              Segment-level traffic conditions.
            </p>
          </div>

          <span className="text-sm text-slate-500">
            {segments.length} segments
          </span>
        </div>

        {segments.length === 0 ? (
          <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
            <p className="text-slate-400">
              No traffic segment data available.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {segments.map((segment) => {
              const congestion = Math.round(
                segment.congestion_score * 100
              )

              const label = getCongestionLabel(
                segment.congestion_score
              )

              return (
                <div
                  key={segment.segment_id}
                  className="rounded-xl border border-slate-800 bg-slate-900 p-5"
                >
                  {/* Segment Header */}
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
                      {label}
                    </span>
                  </div>

                  {/* Metrics */}
                  <div className="mt-5 grid grid-cols-2 gap-4 md:grid-cols-3">
                    <div className="rounded-lg bg-slate-800 p-4">
                      <p className="text-xs text-slate-400">
                        Vehicles
                      </p>

                      <p className="mt-1 text-xl font-semibold">
                        {segment.vehicle_count}
                      </p>
                    </div>

                    <div className="rounded-lg bg-slate-800 p-4">
                      <p className="text-xs text-slate-400">
                        Average Speed
                      </p>

                      <p className="mt-1 text-xl font-semibold">
                        {segment.average_speed}
                        <span className="ml-1 text-xs text-slate-500">
                          km/h
                        </span>
                      </p>
                    </div>

                    <div className="rounded-lg bg-slate-800 p-4">
                      <p className="text-xs text-slate-400">
                        Congestion
                      </p>

                      <p className="mt-1 text-xl font-semibold">
                        {congestion}%
                      </p>
                    </div>
                  </div>

                  {/* Congestion Bar */}
                  <div className="mt-5">
                    <div className="mb-2 flex justify-between text-xs text-slate-500">
                      <span>Congestion Level</span>
                      <span>{congestion}%</span>
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
        )}
      </div>
    </div>
  )
}

export default TrafficAnalytics