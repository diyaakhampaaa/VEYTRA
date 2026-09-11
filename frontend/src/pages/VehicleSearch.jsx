import { useState } from "react"
import { searchVehicle } from "../api/client"
import SourceBadge from "../components/SourceBadge"
import MatchScoreBreakdown from "../components/MatchScoreBreakdown"

function VehicleSearch() {
  const [plate, setPlate] = useState("")
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleSearch = async (event) => {
    event.preventDefault()

    if (!plate.trim()) {
      setError("Enter a vehicle registration number.")
      setResult(null)
      return
    }

    setLoading(true)
    setError("")
    setResult(null)

    try {
      const data = await searchVehicle(plate.trim())
      setResult(data)

      if (!data?.found) {
        setError("No matching vehicle trajectory found.")
      }
    } catch (err) {
      console.error(err)
      setError("Unable to reach the vehicle intelligence service.")
    } finally {
      setLoading(false)
    }
  }

  const vehicle = result?.vehicle

  return (
    <div className="relative min-h-screen overflow-hidden">

      {/* =====================================================
          BACKGROUND
          ===================================================== */}

      <div className="pointer-events-none fixed inset-0 opacity-[0.025]">
        <div className="veytra-grid h-full w-full" />
      </div>

      <div className="pointer-events-none absolute left-1/2 top-0 h-96 w-96 -translate-x-1/2 rounded-full bg-cyan-400/[0.025] blur-3xl" />


      {/* =====================================================
          HEADER
          ===================================================== */}

      <header className="relative border-b border-cyan-300/[0.08] pb-6">

        <div className="flex items-center gap-2 text-[8px] uppercase tracking-[0.28em] text-cyan-300/50">

          <span className="h-1.5 w-1.5 rounded-full bg-cyan-300 shadow-[0_0_8px_#22d3ee]" />

          Vehicle Intelligence

        </div>

        <div className="mt-3 flex flex-col justify-between gap-4 lg:flex-row lg:items-end">

          <div>

            <h1 className="text-3xl font-semibold tracking-[-0.03em] text-white">
              Vehicle Search
            </h1>

            <p className="mt-2 max-w-xl text-sm text-slate-500">
              Search registered observations and reconstruct a vehicle's
              movement across connected camera nodes.
            </p>

          </div>

          <div className="flex items-center gap-3">

            <div className="veytra-panel rounded-lg px-4 py-2.5">

              <div className="text-[7px] uppercase tracking-[0.2em] text-slate-600">
                Search Engine
              </div>

              <div className="mt-1 flex items-center gap-2">

                <span className="veytra-live-dot" />

                <span className="text-[9px] uppercase tracking-[0.15em] text-cyan-200/70">
                  Operational
                </span>

              </div>

            </div>

          </div>

        </div>

      </header>


      {/* =====================================================
          SEARCH CONSOLE
          ===================================================== */}

      <section className="relative mt-7">

        <div className="veytra-panel veytra-hud rounded-xl p-5 sm:p-6">

          <div className="flex items-center gap-3">

            <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-cyan-300/15 bg-cyan-300/[0.04] text-cyan-300">
              ⌕
            </div>

            <div>

              <div className="text-[8px] uppercase tracking-[0.22em] text-slate-600">
                Query Interface
              </div>

              <div className="mt-1 text-sm font-medium text-slate-300">
                Locate vehicle trajectory
              </div>

            </div>

          </div>


          <form
            onSubmit={handleSearch}
            className="mt-6 flex flex-col gap-3 sm:flex-row"
          >

            <div className="relative flex-1">

              <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-[9px] uppercase tracking-[0.18em] text-cyan-300/30">
                ID
              </span>

              <input
                value={plate}
                onChange={(event) => setPlate(event.target.value)}
                placeholder="DL01AB1234"
                className="w-full rounded-lg border border-white/[0.08] bg-[#02080c] py-3.5 pl-12 pr-4 font-mono text-sm uppercase tracking-[0.15em] text-cyan-100 outline-none transition placeholder:text-slate-700 focus:border-cyan-300/30 focus:bg-cyan-300/[0.02] focus:shadow-[0_0_25px_rgba(34,211,238,0.04)]"
              />

            </div>

            <button
              type="submit"
              disabled={loading}
              className="rounded-lg bg-gradient-to-r from-cyan-300 to-teal-300 px-7 py-3.5 text-[9px] font-bold uppercase tracking-[0.16em] text-[#031016] transition hover:scale-[1.01] disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? "Searching..." : "Search Vehicle →"}
            </button>

          </form>


          <div className="mt-4 flex flex-wrap gap-4 text-[7px] uppercase tracking-[0.16em] text-slate-700">

            <span>
              PLATE RECOGNITION
            </span>

            <span>•</span>

            <span>
              CROSS-CAMERA RE-ID
            </span>

            <span>•</span>

            <span>
              TRAJECTORY RECONSTRUCTION
            </span>

          </div>

        </div>

      </section>


      {/* =====================================================
          ERROR
          ===================================================== */}

      {error && (
        <div className="mt-5 rounded-lg border border-amber-300/10 bg-amber-300/[0.025] px-4 py-3">

          <div className="flex items-center gap-3">

            <span className="veytra-warning-dot" />

            <span className="text-[9px] uppercase tracking-[0.14em] text-amber-200/70">
              {error}
            </span>

          </div>

        </div>
      )}


      {/* =====================================================
          EMPTY STATE
          ===================================================== */}

      {!vehicle && !loading && !error && (

        <div className="relative mt-8 flex min-h-[360px] items-center justify-center">

          <div className="text-center">

            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full border border-cyan-300/10 bg-cyan-300/[0.025]">

              <div className="h-5 w-5 rounded-full border border-cyan-300/40" />

            </div>

            <div className="mt-5 text-sm font-medium text-slate-500">
              Awaiting vehicle query
            </div>

            <div className="mt-2 text-[8px] uppercase tracking-[0.18em] text-slate-700">
              Enter a registration number to begin analysis
            </div>

          </div>

        </div>

      )}


      {/* =====================================================
          RESULT
          ===================================================== */}

      {vehicle && (

        <div className="relative mt-8 space-y-5">

          {/* Vehicle identity */}

          <div className="veytra-panel veytra-hud rounded-xl p-5 sm:p-6">

            <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-start">

              <div>

                <div className="flex items-center gap-3">

                  <div className="flex h-11 w-11 items-center justify-center rounded-lg border border-cyan-300/15 bg-cyan-300/[0.04] text-lg text-cyan-300/70">
                    ◉
                  </div>

                  <div>

                    <div className="text-[8px] uppercase tracking-[0.22em] text-slate-600">
                      Vehicle Identified
                    </div>

                    <div className="mt-1 font-mono text-2xl font-semibold tracking-[0.12em] text-cyan-100">
                      {vehicle.plate}
                    </div>

                  </div>

                </div>

              </div>


              <div className="flex items-center gap-3">

                <SourceBadge source={vehicle.source} />

                <div className="rounded-lg border border-teal-300/10 bg-teal-300/[0.035] px-3 py-2">

                  <div className="text-[7px] uppercase tracking-[0.18em] text-slate-600">
                    Vehicle ID
                  </div>

                  <div className="mt-1 font-mono text-[9px] text-teal-200/70">
                    {vehicle.vehicle_id}
                  </div>

                </div>

              </div>

            </div>


            {/* Time range */}

            <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-3">

              <div className="rounded-lg border border-white/[0.05] bg-white/[0.015] p-4">

                <div className="text-[7px] uppercase tracking-[0.18em] text-slate-600">
                  First Seen
                </div>

                <div className="mt-2 font-mono text-sm text-slate-300">
                  {vehicle.start_time}
                </div>

              </div>


              <div className="rounded-lg border border-white/[0.05] bg-white/[0.015] p-4">

                <div className="text-[7px] uppercase tracking-[0.18em] text-slate-600">
                  Last Seen
                </div>

                <div className="mt-2 font-mono text-sm text-slate-300">
                  {vehicle.end_time}
                </div>

              </div>


              <div className="col-span-2 rounded-lg border border-cyan-300/[0.07] bg-cyan-300/[0.02] p-4 sm:col-span-1">

                <div className="text-[7px] uppercase tracking-[0.18em] text-slate-600">
                  Camera Coverage
                </div>

                <div className="mt-2 text-sm font-semibold text-cyan-200">
                  {vehicle.camera_sequence?.length || 0} NODES
                </div>

              </div>

            </div>

          </div>


          {/* =================================================
              TRAJECTORY
              ================================================= */}

          <div className="veytra-panel veytra-hud rounded-xl p-5 sm:p-6">

            <div className="flex items-end justify-between">

              <div>

                <div className="text-[8px] uppercase tracking-[0.22em] text-cyan-300/50">
                  Cross-Camera Analysis
                </div>

                <h2 className="mt-2 text-lg font-medium text-slate-200">
                  Vehicle Trajectory
                </h2>

              </div>

              <div className="hidden text-[7px] uppercase tracking-[0.18em] text-slate-700 sm:block">
                TEMPORAL SEQUENCE
              </div>

            </div>


            {/* Timeline */}

            <div className="relative mt-8">

              {/* Connecting line */}

              <div className="absolute left-5 right-5 top-5 hidden h-px bg-gradient-to-r from-cyan-300/10 via-cyan-300/30 to-cyan-300/10 sm:block" />


              <div className="grid gap-4 sm:grid-cols-3">

                {vehicle.camera_sequence?.map((camera, index) => (

                  <div
                    key={`${camera.camera_id}-${camera.timestamp}-${index}`}
                    className="relative rounded-lg border border-white/[0.06] bg-[#02080c] p-4 transition hover:border-cyan-300/20"
                  >

                    <div className="flex items-center justify-between">

                      <div className="flex items-center gap-3">

                        <div className="relative z-10 flex h-10 w-10 items-center justify-center rounded-full border border-cyan-300/30 bg-[#02070b]">

                          <span className="text-[9px] font-semibold text-cyan-300">
                            0{index + 1}
                          </span>

                        </div>

                        <div>

                          <div className="font-mono text-xs font-semibold text-slate-200">
                            {camera.camera_id}
                          </div>

                          <div className="mt-1 text-[7px] uppercase tracking-[0.15em] text-cyan-300/40">
                            Camera Node
                          </div>

                        </div>

                      </div>

                    </div>


                    <div className="mt-5 border-t border-white/[0.05] pt-4">

                      <div className="flex justify-between">

                        <span className="text-[7px] uppercase tracking-[0.16em] text-slate-700">
                          Timestamp
                        </span>

                        <span className="font-mono text-[9px] text-slate-400">
                          {camera.timestamp}
                        </span>

                      </div>

                      <div className="mt-3 flex justify-between">

                        <span className="text-[7px] uppercase tracking-[0.16em] text-slate-700">
                          Direction
                        </span>

                        <span className="text-[9px] uppercase tracking-[0.1em] text-cyan-200/60">
                          {camera.direction}
                        </span>

                      </div>

                    </div>

                  </div>

                ))}

              </div>

            </div>

          </div>


          {/* =================================================
              MATCH SCORE
              ================================================= */}

          {vehicle.match_score && (

            <div className="veytra-panel veytra-hud rounded-xl p-5 sm:p-6">

              <div className="mb-5">

                <div className="text-[8px] uppercase tracking-[0.22em] text-cyan-300/50">
                  Intelligence Confidence
                </div>

                <h2 className="mt-2 text-lg font-medium text-slate-200">
                  Cross-Camera Match Analysis
                </h2>

              </div>

              <MatchScoreBreakdown
                matchScore={vehicle.match_score}
              />

            </div>

          )}

        </div>

      )}


      {/* =====================================================
          FOOTER
          ===================================================== */}

      <div className="flex items-center justify-between py-8 text-[7px] uppercase tracking-[0.2em] text-slate-700">

        <span>
          VEYTRA // VEHICLE INTELLIGENCE
        </span>

        <span>
          ANPR • RE-ID • TRAJECTORY
        </span>

      </div>

    </div>
  )
}

export default VehicleSearch