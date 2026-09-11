import { useEffect, useMemo, useState } from "react"
import SourceBadge from "../components/SourceBadge"
import { getAnalytics } from "../api/client"

function TrafficAnalytics() {
  const [segments, setSegments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)
  const [selectedSegment, setSelectedSegment] = useState(null)

  useEffect(() => {
    getAnalytics()
      .then((data) => {
        setSegments(data.segments || [])
      })
      .catch((error) => {
        console.error("🔥 VEYTRA ANALYTICS ERROR:", error)
        setError(true)
      })
      .finally(() => {
        setLoading(false)
      })
  }, [])

  const totalVehicles = segments.reduce(
    (total, segment) => total + (segment.vehicle_count || 0),
    0
  )

  const averageSpeed =
    segments.length > 0
      ? segments.reduce(
          (total, segment) =>
            total + (segment.average_speed || 0),
          0
        ) / segments.length
      : 0

  const averageCongestion =
    segments.length > 0
      ? segments.reduce(
          (total, segment) =>
            total + (segment.congestion_score || 0),
          0
        ) / segments.length
      : 0

  const getCongestionLabel = (score) => {
  if (score >= 0.7) return "SEVERE"
  if (score >= 0.4) return "HIGH"
  if (score >= 0.2) return "MODERATE"
  return "LOW"
}

 const getCongestionStyle = (score) => {
  if (score >= 0.7) {
    return "border-red-400/20 bg-red-400/5 text-red-300"
  }

  if (score >= 0.4) {
    return "border-amber-400/20 bg-amber-400/5 text-amber-300"
  }

  if (score >= 0.2) {
    return "border-cyan-400/20 bg-cyan-400/5 text-cyan-300"
  }

  return "border-slate-500/20 bg-slate-500/5 text-slate-400"
}
  const getHeatColor = (score) => {
    if (score >= 0.7) return "#ef4444"
    if (score >= 0.4) return "#f59e0b"
    if (score >= 0.2) return "#22d3ee"
    return "#64748b"
  }

  const heatmapSegments = useMemo(() => {
    return segments.map((segment, index) => ({
      ...segment,
      heatScore: Number(segment.congestion_score || 0),
      x: [18, 35, 52, 70, 84][index % 5],
      y: [28, 57, 35, 68, 46][index % 5],
    }))
  }, [segments])

  if (loading) {
    return (
      <div className="min-h-screen bg-[#02070b] text-white">
        <div className="mb-8">
          <div className="mb-2 flex items-center gap-2 text-xs uppercase tracking-[0.28em] text-cyan-400">
            <span className="veytra-live-dot" />
            Traffic Intelligence
          </div>

          <h1 className="text-3xl font-semibold tracking-tight">
            Traffic Analytics
          </h1>

          <p className="mt-2 text-sm text-slate-400">
            Analyze traffic flow, speed, and congestion.
          </p>
        </div>

        <div className="veytra-panel veytra-hud flex min-h-[300px] items-center justify-center">
          <div className="text-sm text-slate-500">
            Loading traffic intelligence...
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[#02070b] text-white">
        <div className="flex items-end justify-between">
          <div>
            <div className="mb-2 flex items-center gap-2 text-xs uppercase tracking-[0.28em] text-cyan-400">
              <span className="veytra-warning-dot" />
              Traffic Intelligence
            </div>

            <h1 className="text-3xl font-semibold tracking-tight">
              Traffic Analytics
            </h1>

            <p className="mt-2 text-sm text-slate-400">
              Analyze traffic flow, speed, and congestion.
            </p>
          </div>

          <SourceBadge source="simulated" />
        </div>

        <div className="veytra-panel veytra-hud mt-8 p-8">
          <div className="flex items-start gap-4">
            <div className="flex h-10 w-10 items-center justify-center border border-amber-400/20 bg-amber-400/5 text-amber-300">
              !
            </div>

            <div>
              <h2 className="text-lg font-medium">
                Analytics service unavailable
              </h2>

              <p className="mt-2 text-sm text-slate-500">
                Traffic analytics could not be retrieved. Make sure the
                backend is running and the analytics endpoint is available.
              </p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#02070b] text-white">

      {/* HEADER */}
      <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <div className="mb-2 flex items-center gap-2 text-xs uppercase tracking-[0.28em] text-cyan-400">
            <span className="veytra-live-dot" />
            Traffic Intelligence
          </div>

          <h1 className="text-3xl font-semibold tracking-tight">
            Traffic Analytics
          </h1>

          <p className="mt-2 max-w-2xl text-sm text-slate-400">
            Network-level analysis of vehicle flow, average speed,
            and congestion conditions.
          </p>
        </div>

        <div className="veytra-panel px-4 py-3">
          <div className="mb-1 text-[9px] uppercase tracking-[0.22em] text-slate-600">
            Data Source
          </div>

          <SourceBadge source="simulated" />
        </div>
      </div>

      {/* SUMMARY */}
      <div className="mt-8 grid grid-cols-1 gap-4 md:grid-cols-3">

        <div className="veytra-panel veytra-panel-hover veytra-hud p-5">
          <div className="text-[10px] uppercase tracking-[0.2em] text-slate-500">
            Total Vehicles
          </div>

          <div className="mt-4 text-3xl font-semibold tracking-tight">
            {totalVehicles}
          </div>

          <div className="mt-2 text-xs text-slate-600">
            Across monitored segments
          </div>
        </div>

        <div className="veytra-panel veytra-panel-hover veytra-hud p-5">
          <div className="text-[10px] uppercase tracking-[0.2em] text-slate-500">
            Average Speed
          </div>

          <div className="mt-4 text-3xl font-semibold tracking-tight">
            {averageSpeed.toFixed(1)}
            <span className="ml-2 text-sm font-normal text-slate-500">
              km/h
            </span>
          </div>

          <div className="mt-2 text-xs text-slate-600">
            Network-wide average
          </div>
        </div>

        <div className="veytra-panel veytra-panel-hover veytra-hud p-5">
          <div className="text-[10px] uppercase tracking-[0.2em] text-slate-500">
            Average Congestion
          </div>

          <div className="mt-4 text-3xl font-semibold tracking-tight">
            {Math.round(averageCongestion * 100)}
            <span className="ml-1 text-sm font-normal text-slate-500">
              %
            </span>
          </div>

          <div className="mt-2 text-xs text-slate-600">
            Across monitored segments
          </div>
        </div>
      </div>

      {/* ========================================================= */}
      {/* TRAFFIC HEATMAP                                           */}
      {/* ========================================================= */}

      <div className="mt-10">

        <div className="mb-4 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
          <div>
            <div className="mb-1 text-[10px] uppercase tracking-[0.22em] text-cyan-500/60">
              Spatial Intelligence
            </div>

            <h2 className="text-lg font-medium">
              Traffic Heatmap
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Geographic congestion intensity across the monitored network.
            </p>
          </div>

          <div className="flex items-center gap-4 text-[9px] uppercase tracking-[0.15em]">
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-slate-500" />
              Low
            </div>

            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-cyan-400" />
              Moderate
            </div>

            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-amber-400" />
              High
            </div>

            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-red-500" />
              Severe
            </div>
          </div>
        </div>

        <div className="veytra-panel veytra-hud relative min-h-[520px] overflow-hidden">

          {/* MAP GRID */}
          <div
            className="absolute inset-0 opacity-40"
            style={{
              backgroundImage: `
                linear-gradient(rgba(34,211,238,0.055) 1px, transparent 1px),
                linear-gradient(90deg, rgba(34,211,238,0.055) 1px, transparent 1px)
              `,
              backgroundSize: "42px 42px",
            }}
          />

          {/* CITY SHAPE */}
          <svg
            className="absolute inset-0 h-full w-full"
            viewBox="0 0 100 100"
            preserveAspectRatio="none"
          >

            {/* district blocks */}
            <g opacity="0.25" fill="none" stroke="#334155">
              <path d="M5 10 L28 10 L28 30 L5 30 Z" />
              <path d="M34 8 L57 8 L57 25 L34 25 Z" />
              <path d="M64 12 L94 12 L94 31 L64 31 Z" />

              <path d="M7 42 L25 42 L25 67 L7 67 Z" />
              <path d="M33 35 L58 35 L58 64 L33 64 Z" />
              <path d="M66 39 L92 39 L92 69 L66 69 Z" />

              <path d="M10 76 L31 76 L31 94 L10 94 Z" />
              <path d="M39 72 L62 72 L62 94 L39 94 Z" />
              <path d="M69 76 L94 76 L94 94 L69 94 Z" />
            </g>

            {/* major roads */}
            <g
              fill="none"
              stroke="#263943"
              strokeWidth="1.2"
            >
              <path d="M0 50 C18 45 30 54 45 49 C62 43 77 50 100 44" />
              <path d="M0 72 C19 68 34 76 49 69 C68 61 81 72 100 65" />
              <path d="M22 0 C25 20 20 32 27 48 C34 63 27 79 31 100" />
              <path d="M69 0 C65 18 72 33 66 48 C61 64 70 79 67 100" />
              <path d="M0 24 C20 28 34 20 49 28 C66 36 81 21 100 28" />
            </g>

            {/* road center markings */}
            <g
              fill="none"
              stroke="#475569"
              strokeWidth="0.25"
              strokeDasharray="2 2"
            >
              <path d="M0 50 C18 45 30 54 45 49 C62 43 77 50 100 44" />
              <path d="M0 72 C19 68 34 76 49 69 C68 61 81 72 100 65" />
              <path d="M22 0 C25 20 20 32 27 48 C34 63 27 79 31 100" />
              <path d="M69 0 C65 18 72 33 66 48 C61 64 70 79 67 100" />
            </g>

            {/* HEAT CORRIDORS */}
            {heatmapSegments.map((segment, index) => {
              const color = getHeatColor(segment.heatScore)

              const paths = [
                "M0 50 C18 45 30 54 45 49 C62 43 77 50 100 44",
                "M0 72 C19 68 34 76 49 69 C68 61 81 72 100 65",
                "M22 0 C25 20 20 32 27 48 C34 63 27 79 31 100",
                "M69 0 C65 18 72 33 66 48 C61 64 70 79 67 100",
                "M0 24 C20 28 34 20 49 28 C66 36 81 21 100 28",
              ]

              const path = paths[index % paths.length]

              return (
                <g key={segment.segment_id || index}>
                  {/* blurred heat */}
                  <path
                    d={path}
                    fill="none"
                    stroke={color}
                    strokeWidth="5"
                    opacity="0.16"
                    style={{
                      filter: "blur(9px)",
                    }}
                  />

                  {/* heat intensity */}
                  <path
                    d={path}
                    fill="none"
                    stroke={color}
                    strokeWidth="2.2"
                    opacity="0.75"
                    style={{
                      filter: "blur(2px)",
                    }}
                  />

                  {/* road core */}
                  <path
                    d={path}
                    fill="none"
                    stroke={color}
                    strokeWidth="0.7"
                    opacity="0.95"
                  />
                </g>
              )
            })}
          </svg>

          {/* HEATMAP NODES */}
          {heatmapSegments.map((segment, index) => {
            const color = getHeatColor(segment.heatScore)
            const isSelected =
              selectedSegment?.segment_id === segment.segment_id

            return (
              <button
                key={segment.segment_id || index}
                onClick={() => setSelectedSegment(segment)}
                className="absolute -translate-x-1/2 -translate-y-1/2 text-left"
                style={{
                  left: `${segment.x}%`,
                  top: `${segment.y}%`,
                }}
              >
                <span
                  className="absolute -inset-4 rounded-full opacity-30"
                  style={{
                    background: color,
                    filter: "blur(10px)",
                  }}
                />

                <span
                  className={`relative block h-3 w-3 rounded-full border-2 border-[#02070b] transition-transform ${
                    isSelected ? "scale-150" : ""
                  }`}
                  style={{
                    background: color,
                    boxShadow: `0 0 16px ${color}`,
                  }}
                />
              </button>
            )
          })}

          {/* CORNER HUD */}
          <div className="absolute left-5 top-5 font-mono text-[9px] uppercase tracking-[0.18em] text-cyan-400/50">
            SPATIAL CONGESTION MODEL
          </div>

          <div className="absolute right-5 top-5 font-mono text-[9px] uppercase tracking-[0.18em] text-slate-600">
            {segments.length.toString().padStart(2, "0")} ACTIVE SEGMENTS
          </div>

          <div className="absolute bottom-5 left-5 font-mono text-[9px] uppercase tracking-[0.16em] text-slate-700">
            VEYTRA / TRAFFIC INTELLIGENCE
          </div>

          <div className="absolute bottom-5 right-5 font-mono text-[9px] uppercase tracking-[0.16em] text-slate-700">
            HEAT INDEX
          </div>

          {/* SELECTED SEGMENT */}
          {selectedSegment && (
            <div className="absolute right-5 top-16 w-[280px] border border-cyan-400/15 bg-[#061016]/95 p-4 shadow-2xl backdrop-blur-xl">

              <div className="flex items-start justify-between">
                <div>
                  <div className="text-[8px] uppercase tracking-[0.2em] text-cyan-400/60">
                    Selected Corridor
                  </div>

                  <div className="mt-1 font-mono text-sm text-slate-200">
                    {selectedSegment.segment_id}
                  </div>

                  {selectedSegment.road_name && (
                    <div className="mt-1 text-xs text-slate-500">
                      {selectedSegment.road_name}
                    </div>
                  )}
                </div>

                <button
                  onClick={() => setSelectedSegment(null)}
                  className="text-xs text-slate-600 transition hover:text-slate-300"
                >
                  ×
                </button>
              </div>

              <div className="mt-4 grid grid-cols-2 gap-px bg-cyan-400/10">
                <div className="bg-[#08141b] p-3">
                  <div className="text-[8px] uppercase tracking-widest text-slate-600">
                    Vehicles
                  </div>

                  <div className="mt-1 font-mono text-lg text-slate-200">
                    {selectedSegment.vehicle_count ?? 0}
                  </div>
                </div>

                <div className="bg-[#08141b] p-3">
                  <div className="text-[8px] uppercase tracking-widest text-slate-600">
                    Speed
                  </div>

                  <div className="mt-1 font-mono text-lg text-slate-200">
                    {Number(
                      selectedSegment.average_speed || 0
                    ).toFixed(1)}
                  </div>
                </div>
              </div>

              <div className="mt-3">
                <div className="flex justify-between text-[8px] uppercase tracking-widest text-slate-600">
                  <span>Congestion</span>
                  <span>
                    {Math.round(
                      selectedSegment.heatScore * 100
                    )}%
                  </span>
                </div>

                <div className="mt-2 h-1 bg-slate-800">
                  <div
                    className="h-full"
                    style={{
                      width: `${Math.min(
                        selectedSegment.heatScore * 100,
                        100
                      )}%`,
                      background: getHeatColor(
                        selectedSegment.heatScore
                      ),
                    }}
                  />
                </div>
              </div>

              <div className="mt-3">
                <SourceBadge source="simulated" />
              </div>
            </div>
          )}

        </div>
      </div>

      {/* ========================================================= */}
      {/* NETWORK OVERVIEW                                           */}
      {/* ========================================================= */}

      <div className="mt-10">

        <div className="mb-4 flex items-end justify-between">
          <div>
            <div className="mb-1 text-[10px] uppercase tracking-[0.22em] text-cyan-500/60">
              Network Analysis
            </div>

            <h2 className="text-lg font-medium">
              Road Segments
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Segment-level traffic conditions.
            </p>
          </div>

          <div className="font-mono text-xs text-slate-600">
            {segments.length.toString().padStart(2, "0")} SEGMENTS
          </div>
        </div>

        {segments.length === 0 ? (
          <div className="veytra-panel veytra-hud p-8">
            <p className="text-sm text-slate-500">
              No traffic segment data available.
            </p>
          </div>
        ) : (
          <div className="space-y-4">

            {segments.map((segment, index) => {
              const congestion = Math.round(
                (segment.congestion_score || 0) * 100
              )

              const label = getCongestionLabel(
                segment.congestion_score || 0
              )

              return (
                <div
                  key={segment.segment_id || index}
                  className="veytra-panel veytra-panel-hover veytra-hud overflow-hidden"
                >

                  {/* SEGMENT HEADER */}
                  <div className="flex flex-col gap-4 border-b border-cyan-400/10 p-5 md:flex-row md:items-center md:justify-between">

                    <div className="flex items-center gap-4">

                      <div className="flex h-10 w-10 items-center justify-center border border-cyan-400/10 bg-cyan-400/5 font-mono text-xs text-cyan-400">
                        {String(index + 1).padStart(2, "0")}
                      </div>

                      <div>

                        <div className="text-[9px] uppercase tracking-[0.2em] text-slate-600">
                          Road Segment
                        </div>

                        <h3 className="mt-1 font-mono text-base text-slate-200">
                          {segment.segment_id}
                        </h3>

                        {segment.road_name && (
                          <p className="mt-1 text-xs text-slate-500">
                            {segment.road_name}
                          </p>
                        )}

                        {segment.timestamp && (
                          <p className="mt-1 font-mono text-[10px] text-slate-700">
                            {segment.timestamp}
                          </p>
                        )}

                      </div>
                    </div>

                    <div
                      className={`w-fit border px-3 py-1.5 text-[9px] uppercase tracking-[0.18em] ${getCongestionStyle(
                        segment.congestion_score || 0
                      )}`}
                    >
                      {label}
                    </div>

                  </div>

                  {/* METRICS */}
                  <div className="grid grid-cols-1 gap-px bg-cyan-400/5 md:grid-cols-3">

                    <div className="bg-[#061016] p-5">
                      <div className="text-[9px] uppercase tracking-[0.2em] text-slate-600">
                        Vehicles
                      </div>

                      <div className="mt-3 font-mono text-2xl text-slate-200">
                        {segment.vehicle_count ?? 0}
                      </div>

                      <div className="mt-1 text-[10px] text-slate-600">
                        Observed vehicles
                      </div>
                    </div>

                    <div className="bg-[#061016] p-5">
                      <div className="text-[9px] uppercase tracking-[0.2em] text-slate-600">
                        Average Speed
                      </div>

                      <div className="mt-3 font-mono text-2xl text-slate-200">
                        {Number(
                          segment.average_speed || 0
                        ).toFixed(1)}

                        <span className="ml-2 text-xs text-slate-600">
                          km/h
                        </span>
                      </div>

                      <div className="mt-1 text-[10px] text-slate-600">
                        Current segment flow
                      </div>
                    </div>

                    <div className="bg-[#061016] p-5">
                      <div className="text-[9px] uppercase tracking-[0.2em] text-slate-600">
                        Congestion Score
                      </div>

                      <div className="mt-3 font-mono text-2xl text-cyan-300">
                        {congestion}

                        <span className="ml-1 text-xs text-cyan-500/50">
                          %
                        </span>
                      </div>

                      <div className="mt-1 text-[10px] text-slate-600">
                        Computed network condition
                      </div>
                    </div>

                  </div>

                  {/* CONGESTION BAR */}
                  <div className="p-5">

                    <div className="mb-2 flex items-center justify-between">

                      <span className="text-[9px] uppercase tracking-[0.2em] text-slate-600">
                        Congestion Level
                      </span>

                      <span className="font-mono text-[10px] text-cyan-400/70">
                        {congestion}%
                      </span>

                    </div>

                    <div className="relative h-1.5 overflow-hidden bg-slate-800/80">

                      <div
                        className="h-full bg-cyan-400/70 shadow-[0_0_12px_rgba(34,211,238,0.35)]"
                        style={{
                          width: `${Math.min(
                            Math.max(congestion, 0),
                            100
                          )}%`,
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

      {/* FOOTER */}
      <div className="mt-10 flex items-center justify-between border-t border-cyan-400/10 pt-4 text-[9px] uppercase tracking-[0.18em] text-slate-700">
        <span>VEYTRA / Traffic Intelligence</span>
        <span>Flow • Speed • Congestion</span>
      </div>

    </div>
  )
}

export default TrafficAnalytics