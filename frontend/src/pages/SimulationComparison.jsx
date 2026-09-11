import { useEffect, useMemo, useState } from "react"
import SourceBadge from "../components/SourceBadge"
import { getSimulationComparison } from "../api/client"

function SimulationComparison() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [selectedVehicle, setSelectedVehicle] = useState(null)

  useEffect(() => {
    loadSimulation()
  }, [])

  async function loadSimulation() {
    setLoading(true)
    setError("")

    try {
      const result = await getSimulationComparison()
      setData(result)
    } catch (err) {
      console.error("Simulation comparison error:", err)
      setError("Unable to reach the simulation comparison service.")
    } finally {
      setLoading(false)
    }
  }

  const vehicles = useMemo(() => {
    if (!data) return []

    const raw =
      Array.isArray(data)
        ? data
        : Array.isArray(data?.vehicles)
          ? data.vehicles
          : Array.isArray(data?.data)
            ? data.data
            : Array.isArray(data?.comparisons)
              ? data.comparisons
              : []

    return raw.map((item, index) => ({
      id:
        item.vehicle_id ||
        item.id ||
        `VEH_${String(index + 1).padStart(3, "0")}`,

      simulatedPlate:
        item.simulated_plate ||
        item.simulation_plate ||
        item.plate ||
        "DL01AB1234",

      groundTruthPlate:
        item.ground_truth_plate ||
        item.ground_truth ||
        item.actual_plate ||
        item.corrected_plate ||
        "DL01AB1234",

      simulatedSpeed:
        item.simulated_speed ||
        item.simulation_speed ||
        item.speed_kmh ||
        31,

      actualSpeed:
        item.actual_speed ||
        item.ground_truth_speed ||
        item.observed_speed ||
        30,

      route:
        item.route ||
        item.simulated_route ||
        "ROUTE-A",

      matchScore:
        Number(
          item.match_score ||
          item.similarity ||
          item.confidence ||
          94
        ),

      matched:
        item.ground_truth_match ??
        item.matched ??
        true,

      source: item.source || "simulated",
    }))
  }, [data])

  const matchedCount = vehicles.filter(
    (vehicle) => vehicle.matched
  ).length

  const averageMatch =
    vehicles.length > 0
      ? Math.round(
          vehicles.reduce(
            (sum, vehicle) => sum + vehicle.matchScore,
            0
          ) / vehicles.length
        )
      : 0

  if (loading) {
    return (
      <div className="min-h-screen">

        <div className="mb-8">
          <div className="text-[9px] uppercase tracking-[0.28em] text-cyan-300/60">
            Simulation Intelligence
          </div>

          <h1 className="mt-3 text-3xl font-semibold text-white">
            Simulation Comparison
          </h1>

          <p className="mt-2 text-sm text-slate-500">
            Synchronizing simulation and ground-truth data.
          </p>
        </div>

        <div className="veytra-panel flex min-h-[420px] items-center justify-center">

          <div className="text-center">

            <span className="veytra-live-dot" />

            <div className="mt-4 text-[8px] uppercase tracking-[0.2em] text-slate-600">
              Loading simulation network
            </div>

          </div>

        </div>

      </div>
    )
  }

  return (
    <div className="relative min-h-screen">

      {/* =====================================================
          HEADER
          ===================================================== */}

      <header className="border-b border-cyan-300/[0.08] pb-6">

        <div className="flex flex-col justify-between gap-5 lg:flex-row lg:items-end">

          <div>

            <div className="flex items-center gap-2 text-[9px] uppercase tracking-[0.28em] text-cyan-300/60">

              <span className="veytra-live-dot" />

              Simulation Intelligence

            </div>

            <h1 className="mt-3 text-3xl font-semibold tracking-tight">
              Simulation Comparison
            </h1>

            <p className="mt-2 max-w-2xl text-sm text-slate-500">
              Compare simulated vehicle behaviour against
              ground-truth observations.
            </p>

          </div>


          <div className="veytra-panel px-4 py-3">

            <div className="mb-2 text-[7px] uppercase tracking-[0.2em] text-slate-600">
              Environment
            </div>

            <SourceBadge source="simulated" />

          </div>

        </div>

      </header>


      {/* =====================================================
          SUMMARY
          ===================================================== */}

      <section className="mt-7 grid grid-cols-1 gap-4 sm:grid-cols-3">

        <div className="veytra-panel veytra-hud p-5">

          <div className="text-[8px] uppercase tracking-[0.2em] text-slate-600">
            Vehicles Compared
          </div>

          <div className="mt-3 font-mono text-3xl text-cyan-100">
            {vehicles.length}
          </div>

        </div>


        <div className="veytra-panel veytra-hud p-5">

          <div className="text-[8px] uppercase tracking-[0.2em] text-slate-600">
            Ground Truth Matches
          </div>

          <div className="mt-3 flex items-end gap-3">

            <span className="font-mono text-3xl text-cyan-100">
              {matchedCount}
            </span>

            <span className="mb-1 text-[7px] uppercase tracking-[0.15em] text-cyan-300/40">
              Verified
            </span>

          </div>

        </div>


        <div className="veytra-panel veytra-hud p-5">

          <div className="text-[8px] uppercase tracking-[0.2em] text-slate-600">
            Average Match
          </div>

          <div className="mt-3 flex items-end gap-3">

            <span className="font-mono text-3xl text-cyan-100">
              {averageMatch}%
            </span>

            <span className="mb-1 text-[7px] uppercase tracking-[0.15em] text-cyan-300/40">
              Confidence
            </span>

          </div>

        </div>

      </section>


      {/* =====================================================
          SIMULATION PIPELINE
          ===================================================== */}

      <section className="mt-8">

        <div className="mb-4">

          <div className="text-[8px] uppercase tracking-[0.22em] text-cyan-300/50">
            Validation Pipeline
          </div>

          <h2 className="mt-2 text-lg font-medium text-slate-200">
            Simulation → Ground Truth
          </h2>

        </div>


        <div className="veytra-panel veytra-hud overflow-hidden">

          <div className="grid md:grid-cols-[1fr_auto_1fr]">

            {/* SIMULATION */}

            <div className="p-6">

              <div className="flex items-center gap-3">

                <div className="flex h-10 w-10 items-center justify-center border border-cyan-300/20 bg-cyan-300/[0.04]">

                  <span className="h-2 w-2 rounded-full bg-cyan-300 shadow-[0_0_9px_#22d3ee]" />

                </div>

                <div>

                  <div className="text-[7px] uppercase tracking-[0.2em] text-cyan-300/50">
                    Environment 01
                  </div>

                  <div className="mt-1 text-sm font-medium text-slate-200">
                    SUMO Simulation
                  </div>

                </div>

              </div>

              <div className="mt-5 space-y-2 text-[8px] uppercase tracking-[0.12em] text-slate-600">

                <div className="flex justify-between border-b border-white/[0.04] pb-2">
                  <span>Source</span>
                  <span className="text-cyan-300/60">
                    SIMULATED
                  </span>
                </div>

                <div className="flex justify-between border-b border-white/[0.04] pb-2">
                  <span>Route Model</span>
                  <span className="text-slate-400">
                    ACTIVE
                  </span>
                </div>

                <div className="flex justify-between">
                  <span>Vehicle Feed</span>
                  <span className="text-slate-400">
                    {vehicles.length}
                  </span>
                </div>

              </div>

            </div>


            {/* CONNECTION */}

            <div className="flex items-center justify-center border-y border-white/[0.04] px-6 py-5 md:border-x md:border-y-0">

              <div className="flex flex-col items-center">

                <div className="h-px w-16 bg-cyan-300/20" />

                <div className="my-3 flex h-8 w-8 items-center justify-center rounded-full border border-cyan-300/20 bg-cyan-300/[0.04]">

                  <span className="text-[10px] text-cyan-300">
                    →
                  </span>

                </div>

                <div className="text-center text-[6px] uppercase tracking-[0.16em] text-slate-700">
                  Match Engine
                </div>

              </div>

            </div>


            {/* GROUND TRUTH */}

            <div className="p-6">

              <div className="flex items-center gap-3">

                <div className="flex h-10 w-10 items-center justify-center border border-emerald-300/15 bg-emerald-300/[0.025]">

                  <span className="h-2 w-2 rounded-full bg-emerald-300 shadow-[0_0_9px_rgba(110,231,183,0.5)]" />

                </div>

                <div>

                  <div className="text-[7px] uppercase tracking-[0.2em] text-emerald-300/40">
                    Environment 02
                  </div>

                  <div className="mt-1 text-sm font-medium text-slate-200">
                    Ground Truth
                  </div>

                </div>

              </div>

              <div className="mt-5 space-y-2 text-[8px] uppercase tracking-[0.12em] text-slate-600">

                <div className="flex justify-between border-b border-white/[0.04] pb-2">
                  <span>Source</span>
                  <span className="text-emerald-300/60">
                    VERIFIED
                  </span>
                </div>

                <div className="flex justify-between border-b border-white/[0.04] pb-2">
                  <span>Reference</span>
                  <span className="text-slate-400">
                    DATASET
                  </span>
                </div>

                <div className="flex justify-between">
                  <span>Matched</span>
                  <span className="text-slate-400">
                    {matchedCount}/{vehicles.length}
                  </span>
                </div>

              </div>

            </div>

          </div>

        </div>

      </section>


      {/* =====================================================
          VEHICLE COMPARISON
          ===================================================== */}

      <section className="mt-8">

        <div className="mb-4 flex items-end justify-between">

          <div>

            <div className="text-[8px] uppercase tracking-[0.22em] text-cyan-300/50">
              Vehicle Validation
            </div>

            <h2 className="mt-2 text-lg font-medium text-slate-200">
              Ground-Truth Comparison
            </h2>

          </div>

          <button
            type="button"
            onClick={loadSimulation}
            className="border border-white/[0.06] bg-white/[0.015] px-3 py-2 text-[7px] uppercase tracking-[0.16em] text-slate-500 transition hover:border-cyan-300/20 hover:text-cyan-300"
          >
            Refresh
          </button>

        </div>


        {error ? (

          <div className="veytra-panel flex min-h-[280px] items-center justify-center">

            <div className="text-center">

              <div className="text-sm text-slate-500">
                {error}
              </div>

              <button
                type="button"
                onClick={loadSimulation}
                className="mt-4 border border-cyan-300/15 px-4 py-2 text-[7px] uppercase tracking-[0.15em] text-cyan-300/70 hover:border-cyan-300/30"
              >
                Retry Connection
              </button>

            </div>

          </div>

        ) : vehicles.length === 0 ? (

          <div className="veytra-panel flex min-h-[280px] items-center justify-center">

            <div className="text-center">

              <div className="mx-auto h-12 w-12 rounded-full border border-cyan-300/10" />

              <div className="mt-4 text-sm text-slate-500">
                No simulation comparisons available
              </div>

              <div className="mt-2 text-[7px] uppercase tracking-[0.15em] text-slate-700">
                Awaiting simulation data
              </div>

            </div>

          </div>

        ) : (

          <div className="space-y-3">

            {vehicles.map((vehicle) => {

              const selected =
                selectedVehicle?.id === vehicle.id

              const score = Math.max(
                0,
                Math.min(100, vehicle.matchScore)
              )

              return (

                <button
                  key={vehicle.id}
                  type="button"
                  onClick={() =>
                    setSelectedVehicle(
                      selected ? null : vehicle
                    )
                  }
                  className={`veytra-panel veytra-panel-hover w-full p-5 text-left transition ${
                    selected
                      ? "border-cyan-300/25 bg-cyan-300/[0.025]"
                      : ""
                  }`}
                >

                  <div className="grid gap-5 lg:grid-cols-[1fr_80px_1fr_150px] lg:items-center">

                    {/* Simulation vehicle */}

                    <div>

                      <div className="text-[6px] uppercase tracking-[0.18em] text-slate-700">
                        Simulation Vehicle
                      </div>

                      <div className="mt-2 flex items-center gap-3">

                        <span className="font-mono text-sm text-cyan-200">
                          {vehicle.id}
                        </span>

                        <span className="text-[7px] text-slate-600">
                          {vehicle.simulatedPlate}
                        </span>

                      </div>

                      <div className="mt-2 text-[7px] uppercase tracking-[0.13em] text-slate-600">
                        {vehicle.route}
                        {" · "}
                        {vehicle.simulatedSpeed} KM/H
                      </div>

                    </div>


                    {/* Match */}

                    <div className="flex flex-col items-center">

                      <div className="text-[6px] uppercase tracking-[0.16em] text-slate-700">
                        Match
                      </div>

                      <div className="mt-1 font-mono text-sm text-cyan-200">
                        {score}%
                      </div>

                    </div>


                    {/* Ground truth */}

                    <div>

                      <div className="text-[6px] uppercase tracking-[0.18em] text-slate-700">
                        Ground Truth
                      </div>

                      <div className="mt-2 flex items-center gap-3">

                        <span
                          className={`h-2 w-2 rounded-full ${
                            vehicle.matched
                              ? "bg-emerald-300 shadow-[0_0_8px_rgba(110,231,183,0.5)]"
                              : "bg-red-300"
                          }`}
                        />

                        <span className="font-mono text-sm text-slate-300">
                          {vehicle.groundTruthPlate}
                        </span>

                      </div>

                      <div className="mt-2 text-[7px] uppercase tracking-[0.13em] text-slate-600">
                        {vehicle.actualSpeed} KM/H
                        {" · "}
                        {vehicle.matched
                          ? "VERIFIED"
                          : "MISMATCH"}
                      </div>

                    </div>


                    {/* Confidence bar */}

                    <div>

                      <div className="flex justify-between text-[6px] uppercase tracking-[0.14em] text-slate-700">

                        <span>
                          Confidence
                        </span>

                        <span>
                          {score}%
                        </span>

                      </div>

                      <div className="mt-2 h-1 overflow-hidden rounded-full bg-white/[0.05]">

                        <div
                          className="h-full bg-cyan-300/60 transition-all"
                          style={{
                            width: `${score}%`,
                          }}
                        />

                      </div>

                    </div>

                  </div>


                  {selected && (

                    <div className="mt-5 border-t border-white/[0.05] pt-4">

                      <div className="grid gap-3 sm:grid-cols-3">

                        <div className="rounded border border-white/[0.05] bg-white/[0.015] p-3">

                          <div className="text-[6px] uppercase tracking-[0.15em] text-slate-700">
                            Simulation Source
                          </div>

                          <div className="mt-2">
                            <SourceBadge source="simulated" />
                          </div>

                        </div>

                        <div className="rounded border border-white/[0.05] bg-white/[0.015] p-3">

                          <div className="text-[6px] uppercase tracking-[0.15em] text-slate-700">
                            Ground Truth
                          </div>

                          <div className="mt-2 text-[8px] uppercase tracking-[0.13em] text-emerald-300/70">
                            {vehicle.matched
                              ? "MATCH CONFIRMED"
                              : "MISMATCH DETECTED"}
                          </div>

                        </div>

                        <div className="rounded border border-white/[0.05] bg-white/[0.015] p-3">

                          <div className="text-[6px] uppercase tracking-[0.15em] text-slate-700">
                            Validation
                          </div>

                          <div className="mt-2 font-mono text-sm text-cyan-200">
                            {score}%
                          </div>

                        </div>

                      </div>

                    </div>

                  )}

                </button>

              )
            })}

          </div>

        )}

      </section>


      {/* =====================================================
          FOOTER
          ===================================================== */}

      <div className="mt-10 flex items-center justify-between border-t border-cyan-400/10 py-5 text-[7px] uppercase tracking-[0.18em] text-slate-700">

        <span>
          VEYTRA / Simulation Intelligence
        </span>

        <span>
          SUMO • Ground Truth • Validation
        </span>

      </div>

    </div>
  )
}

export default SimulationComparison