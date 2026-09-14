import { useEffect, useMemo, useState } from "react"
import SourceBadge from "../components/SourceBadge"
import {
  getSimulationComparison,
  runSimulation,
} from "../api/client"

function formatPercent(value, alreadyPercent = false) {
  const number = Number(value ?? 0)
  return `${(alreadyPercent ? number : number * 100).toFixed(1)}%`
}

function sequenceLabel(sequence) {
  return Array.isArray(sequence) && sequence.length
    ? sequence.join(" → ")
    : "No camera sequence"
}

function metricCard(label, value, detail) {
  return (
    <div className="veytra-panel veytra-hud p-5">
      <div className="text-[8px] uppercase tracking-[0.2em] text-slate-600">
        {label}
      </div>
      <div className="mt-3 font-mono text-3xl text-cyan-100">
        {value}
      </div>
      {detail && (
        <div className="mt-2 text-[7px] uppercase tracking-[0.13em] text-slate-600">
          {detail}
        </div>
      )}
    </div>
  )
}

function SimulationComparison() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [running, setRunning] = useState(false)
  const [error, setError] = useState("")
  const [selectedVehicle, setSelectedVehicle] = useState(null)

  async function loadSimulation() {
    setLoading(true)
    setError("")

    try {
      const result = await getSimulationComparison()
      setData(result)
    } catch (err) {
      console.error("Simulation comparison error:", err)
      setError(err.message || "Unable to reach the simulation service.")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadSimulation()
  }, [])

  async function handleRunSimulation() {
    setRunning(true)
    setError("")

    try {
      const result = await runSimulation()
      setData(result)
    } catch (err) {
      console.error("SUMO simulation error:", err)
      setError(
        err.message ||
          "The SUMO simulation could not be completed."
      )
    } finally {
      setRunning(false)
    }
  }

  const metrics = data?.metrics || {}
  const simulation = data?.simulation || {}

  const vehicles = useMemo(
    () => (Array.isArray(data?.comparisons) ? data.comparisons : []),
    [data]
  )

  const matchedCount = vehicles.filter(
    (vehicle) => vehicle.matched
  ).length

  const exactRate =
    Number(metrics.trajectory_reconstruction_accuracy ?? 0)

  const associationRate =
    Number(metrics.correct_cross_camera_association_percent ?? 0)

  const transitionRate =
    Number(metrics.camera_transition_accuracy ?? 0)

  const matchingRate =
    Number(metrics.vehicle_matching_accuracy ?? 0)

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
            Loading the latest SUMO evaluation.
          </p>
        </div>

        <div className="veytra-panel flex min-h-[320px] items-center justify-center">
          <div className="text-center">
            <span className="veytra-live-dot" />
            <div className="mt-4 text-[8px] uppercase tracking-[0.2em] text-slate-600">
              Reading simulation results
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="relative min-h-screen">
      <header className="border-b border-cyan-300/[0.08] pb-6">
        <div className="flex flex-col justify-between gap-5 lg:flex-row lg:items-end">
          <div>
            <div className="flex items-center gap-2 text-[9px] uppercase tracking-[0.28em] text-cyan-300/60">
              <span className="veytra-live-dot" />
              Simulation Intelligence
            </div>

            <h1 className="mt-3 text-3xl font-semibold tracking-tight">
              SUMO Validation
            </h1>

            <p className="mt-2 max-w-3xl text-sm text-slate-500">
              Run the Member 3 pipeline on shuffled and partially dropped
              camera observations, then compare reconstructed trajectories
              against hidden SUMO ground truth.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <div className="veytra-panel px-4 py-3">
              <div className="mb-2 text-[7px] uppercase tracking-[0.2em] text-slate-600">
                Environment
              </div>
              <SourceBadge source="simulated" />
            </div>

            <button
              type="button"
              onClick={handleRunSimulation}
              disabled={running}
              className="border border-cyan-300/20 bg-cyan-300/[0.04] px-4 py-3 text-[8px] uppercase tracking-[0.16em] text-cyan-200 transition hover:border-cyan-300/40 disabled:cursor-wait disabled:opacity-50"
            >
              {running ? "Running SUMO..." : "Run Simulation"}
            </button>

            <button
              type="button"
              onClick={loadSimulation}
              disabled={running}
              className="border border-white/[0.06] bg-white/[0.015] px-4 py-3 text-[8px] uppercase tracking-[0.16em] text-slate-500 transition hover:border-cyan-300/20 hover:text-cyan-300 disabled:opacity-50"
            >
              Refresh
            </button>
          </div>
        </div>
      </header>

      {error && (
        <div className="veytra-panel mt-6 border-red-400/20 bg-red-400/[0.03] p-4">
          <div className="text-[8px] uppercase tracking-[0.18em] text-red-300/70">
            Simulation error
          </div>
          <div className="mt-2 text-sm text-slate-400">
            {error}
          </div>
        </div>
      )}

      {data?.status === "not_run" ? (
        <div className="veytra-panel mt-7 p-8">
          <div className="text-[8px] uppercase tracking-[0.22em] text-cyan-300/50">
            No evaluation yet
          </div>
          <h2 className="mt-2 text-xl font-medium text-slate-200">
            Start the Member 3 simulation
          </h2>
          <p className="mt-2 max-w-2xl text-sm text-slate-500">
            The dashboard is connected to the real SUMO evaluator. Click
            <span className="text-cyan-300"> Run Simulation </span>
            above to generate public observations, prepare local tracks,
            run cross-camera matching, reconstruct trajectories, and
            evaluate them against the hidden ground truth.
          </p>
        </div>
      ) : (
        <>
          <section className="mt-7 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {metricCard(
              "Vehicles Compared",
              simulation.ground_truth_vehicle_count ?? vehicles.length,
              `${simulation.public_observation_count ?? 0} public observations`
            )}

            {metricCard(
              "Vehicle Matching",
              formatPercent(matchingRate),
              `${matchedCount}/${vehicles.length} exact trajectory matches`
            )}

            {metricCard(
              "Cross-Camera Association",
              formatPercent(associationRate, true),
              `${metrics.accepted_cross_camera_associations_evaluated ?? 0} accepted links evaluated`
            )}

            {metricCard(
              "Trajectory Reconstruction",
              formatPercent(exactRate),
              `${metrics.predicted_trajectories ?? 0} predicted trajectories`
            )}
          </section>

          <section className="mt-8">
            <div className="mb-4">
              <div className="text-[8px] uppercase tracking-[0.22em] text-cyan-300/50">
                Validation Pipeline
              </div>
              <h2 className="mt-2 text-lg font-medium text-slate-200">
                Public observations → Matcher → Reconstruction → Ground Truth
              </h2>
            </div>

            <div className="veytra-panel veytra-hud overflow-hidden">
              <div className="grid md:grid-cols-4">
                {[
                  [
                    "01",
                    "SUMO",
                    `${simulation.configured_vehicle_count ?? 0} configured vehicles`,
                  ],
                  [
                    "02",
                    "PUBLIC FEED",
                    `${simulation.public_observation_count ?? 0} shuffled observations`,
                  ],
                  [
                    "03",
                    "MEMBER 3",
                    `${metrics.predicted_trajectories ?? 0} reconstructed trajectories`,
                  ],
                  [
                    "04",
                    "EVALUATION",
                    `${simulation.ground_truth_vehicle_count ?? 0} hidden GT vehicles`,
                  ],
                ].map(([number, title, detail], index) => (
                  <div
                    key={number}
                    className={`p-5 ${
                      index > 0
                        ? "border-t border-white/[0.04] md:border-l md:border-t-0"
                        : ""
                    }`}
                  >
                    <div className="font-mono text-[9px] text-cyan-300/50">
                      {number}
                    </div>
                    <div className="mt-3 text-sm font-medium text-slate-200">
                      {title}
                    </div>
                    <div className="mt-2 text-[7px] uppercase tracking-[0.12em] text-slate-600">
                      {detail}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </section>

          <section className="mt-8">
            <div className="mb-4 flex items-end justify-between">
              <div>
                <div className="text-[8px] uppercase tracking-[0.22em] text-cyan-300/50">
                  Camera Validation
                </div>
                <h2 className="mt-2 text-lg font-medium text-slate-200">
                  Transition Accuracy
                </h2>
              </div>
              <div className="font-mono text-sm text-cyan-200">
                {formatPercent(transitionRate)}
              </div>
            </div>

            <div className="veytra-panel p-5">
              <div className="h-2 overflow-hidden rounded-full bg-white/[0.05]">
                <div
                  className="h-full bg-cyan-300/60 transition-all"
                  style={{
                    width: `${Math.max(
                      0,
                      Math.min(100, transitionRate * 100)
                    )}%`,
                  }}
                />
              </div>

              <div className="mt-3 flex justify-between text-[7px] uppercase tracking-[0.13em] text-slate-600">
                <span>Predicted camera transitions</span>
                <span>
                  {formatPercent(transitionRate)}
                </span>
              </div>
            </div>
          </section>

          <section className="mt-8">
            <div className="mb-4">
              <div className="text-[8px] uppercase tracking-[0.22em] text-cyan-300/50">
                Vehicle Validation
              </div>
              <h2 className="mt-2 text-lg font-medium text-slate-200">
                Reconstructed Trajectory vs Hidden Ground Truth
              </h2>
            </div>

            <div className="space-y-3">
              {vehicles.map((vehicle) => {
                const selected =
                  selectedVehicle?.vehicle_id === vehicle.vehicle_id

                const score = Math.max(
                  0,
                  Math.min(100, Number(vehicle.match_score ?? 0))
                )

                return (
                  <button
                    key={vehicle.vehicle_id}
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
                    <div className="grid gap-5 lg:grid-cols-[120px_1fr_1fr_120px] lg:items-center">
                      <div>
                        <div className="text-[6px] uppercase tracking-[0.18em] text-slate-700">
                          Ground Truth Vehicle
                        </div>
                        <div className="mt-2 font-mono text-sm text-cyan-200">
                          {vehicle.vehicle_id}
                        </div>
                        <div className="mt-1 text-[7px] text-slate-600">
                          {vehicle.trajectory_id || "No trajectory"}
                        </div>
                      </div>

                      <div>
                        <div className="text-[6px] uppercase tracking-[0.18em] text-slate-700">
                          Reconstructed
                        </div>
                        <div className="mt-2 text-[8px] uppercase tracking-[0.12em] text-slate-400">
                          {sequenceLabel(
                            vehicle.predicted_camera_sequence
                          )}
                        </div>
                      </div>

                      <div>
                        <div className="text-[6px] uppercase tracking-[0.18em] text-slate-700">
                          Hidden Ground Truth
                        </div>
                        <div className="mt-2 text-[8px] uppercase tracking-[0.12em] text-slate-400">
                          {sequenceLabel(
                            vehicle.ground_truth_camera_sequence
                          )}
                        </div>
                      </div>

                      <div>
                        <div className="flex items-center justify-between text-[6px] uppercase tracking-[0.14em] text-slate-700">
                          <span>Matcher</span>
                          <span>{score.toFixed(1)}%</span>
                        </div>

                        <div className="mt-2 h-1 overflow-hidden rounded-full bg-white/[0.05]">
                          <div
                            className="h-full bg-cyan-300/60"
                            style={{ width: `${score}%` }}
                          />
                        </div>

                        <div
                          className={`mt-2 text-right text-[7px] uppercase tracking-[0.14em] ${
                            vehicle.matched
                              ? "text-emerald-300/70"
                              : "text-red-300/70"
                          }`}
                        >
                          {vehicle.matched ? "MATCH" : "MISMATCH"}
                        </div>
                      </div>
                    </div>

                    {selected && (
                      <div className="mt-5 border-t border-white/[0.05] pt-4">
                        <div className="grid gap-3 sm:grid-cols-3">
                          <div className="rounded border border-white/[0.05] bg-white/[0.015] p-3">
                            <div className="text-[6px] uppercase tracking-[0.15em] text-slate-700">
                              Observations
                            </div>
                            <div className="mt-2 font-mono text-sm text-cyan-200">
                              {vehicle.observation_count ?? 0}
                            </div>
                          </div>

                          <div className="rounded border border-white/[0.05] bg-white/[0.015] p-3">
                            <div className="text-[6px] uppercase tracking-[0.15em] text-slate-700">
                              Trajectory
                            </div>
                            <div className="mt-2 text-[8px] text-slate-400">
                              {vehicle.trajectory_id || "Not reconstructed"}
                            </div>
                          </div>

                          <div className="rounded border border-white/[0.05] bg-white/[0.015] p-3">
                            <div className="text-[6px] uppercase tracking-[0.15em] text-slate-700">
                              Source
                            </div>
                            <div className="mt-2">
                              <SourceBadge source="simulated" />
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </button>
                )
              })}
            </div>
          </section>

          <div className="mt-10 flex items-center justify-between border-t border-cyan-400/10 py-5 text-[7px] uppercase tracking-[0.18em] text-slate-700">
            <span>VEYTRA / Member 3 Simulation Intelligence</span>
            <span>SUMO • Public Feed • Matching • Reconstruction • GT Evaluation</span>
          </div>
        </>
      )}
    </div>
  )
}

export default SimulationComparison
