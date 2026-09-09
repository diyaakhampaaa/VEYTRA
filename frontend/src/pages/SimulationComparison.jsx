import { useEffect, useState } from "react"
import SourceBadge from "../components/SourceBadge"
import { getSimulationComparison } from "../api/client"

function SimulationComparison() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)

  useEffect(() => {
    getSimulationComparison()
      .then((result) => {
        setData(result)
      })
      .catch((error) => {
        console.error("Simulation comparison error:", error)
        setError(true)
      })
      .finally(() => {
        setLoading(false)
      })
  }, [])

  if (loading) {
    return (
      <div>
        <h2 className="text-2xl font-semibold">
          Simulation Comparison
        </h2>

        <p className="mt-8 text-slate-400">
          Loading simulation data...
        </p>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div>
        <h2 className="text-2xl font-semibold">
          Simulation Comparison
        </h2>

        <p className="mt-2 text-slate-400">
          Compare simulated traffic with ground-truth data.
        </p>

        <div className="mt-8 rounded-xl border border-slate-800 bg-slate-900 p-6">
          <p className="text-slate-400">
            Simulation data unavailable. Make sure the backend is running.
          </p>
        </div>
      </div>
    )
  }

  const simulation = data.simulation
  const groundTruth = data.ground_truth
  const comparison = data.comparison

  const vehicleAccuracy = Math.round(
    comparison.vehicle_count_accuracy * 100
  )

  const speedAccuracy = Math.round(
    comparison.speed_accuracy * 100
  )

  const congestionAccuracy = Math.round(
    (1 - Math.abs(comparison.congestion_difference)) * 100
  )

  const overallAccuracy = Math.round(
    comparison.overall_accuracy * 100
  )

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold">
            Simulation Comparison
          </h2>

          <p className="mt-2 text-slate-400">
            Compare simulated traffic with ground-truth data.
          </p>
        </div>

        <SourceBadge source="simulated" />
      </div>

      {/* Scenario Summary */}
      <div className="mt-8 rounded-xl border border-slate-800 bg-slate-900 p-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs uppercase tracking-wider text-slate-500">
              Simulation Scenario
            </p>

            <h3 className="mt-1 text-xl font-semibold">
              {simulation.scenario_id}
            </h3>

            <p className="mt-2 text-sm text-slate-500">
              SUMO traffic simulation compared against reference
              ground-truth measurements.
            </p>
          </div>

          <div className="rounded-xl border border-slate-700 bg-slate-800 px-6 py-4">
            <p className="text-xs uppercase tracking-wider text-slate-500">
              Overall Accuracy
            </p>

            <p className="mt-1 text-3xl font-semibold">
              {overallAccuracy}%
            </p>
          </div>
        </div>
      </div>

      {/* Main Comparison */}
      <div className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-2">
        {/* VEYTRA Prediction */}
        <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-wider text-slate-500">
                Predicted
              </p>

              <h3 className="mt-1 text-lg font-semibold">
                VEYTRA Prediction
              </h3>
            </div>

            <SourceBadge source="simulated" />
          </div>

          <div className="mt-6 grid grid-cols-1 gap-5 sm:grid-cols-3">
            <div className="rounded-lg bg-slate-800 p-4">
              <p className="text-sm text-slate-400">
                Vehicles
              </p>

              <p className="mt-2 text-3xl font-semibold">
                {simulation.vehicles}
              </p>
            </div>

            <div className="rounded-lg bg-slate-800 p-4">
              <p className="text-sm text-slate-400">
                Avg. Speed
              </p>

              <p className="mt-2 text-3xl font-semibold">
                {simulation.average_speed}
              </p>

              <p className="mt-1 text-xs text-slate-500">
                km/h
              </p>
            </div>

            <div className="rounded-lg bg-slate-800 p-4">
              <p className="text-sm text-slate-400">
                Congestion
              </p>

              <p className="mt-2 text-3xl font-semibold">
                {Math.round(simulation.congestion_score * 100)}%
              </p>
            </div>
          </div>
        </div>

        {/* Ground Truth */}
        <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-wider text-slate-500">
                Reference
              </p>

              <h3 className="mt-1 text-lg font-semibold">
                Ground Truth
              </h3>
            </div>

            <span className="rounded-full bg-green-500/20 px-3 py-1 text-xs font-medium text-green-400">
              Reference
            </span>
          </div>

          <div className="mt-6 grid grid-cols-1 gap-5 sm:grid-cols-3">
            <div className="rounded-lg bg-slate-800 p-4">
              <p className="text-sm text-slate-400">
                Vehicles
              </p>

              <p className="mt-2 text-3xl font-semibold">
                {groundTruth.vehicles}
              </p>
            </div>

            <div className="rounded-lg bg-slate-800 p-4">
              <p className="text-sm text-slate-400">
                Avg. Speed
              </p>

              <p className="mt-2 text-3xl font-semibold">
                {groundTruth.average_speed}
              </p>

              <p className="mt-1 text-xs text-slate-500">
                km/h
              </p>
            </div>

            <div className="rounded-lg bg-slate-800 p-4">
              <p className="text-sm text-slate-400">
                Congestion
              </p>

              <p className="mt-2 text-3xl font-semibold">
                {Math.round(groundTruth.congestion_score * 100)}%
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Accuracy Breakdown */}
      <div className="mt-6 rounded-xl border border-slate-800 bg-slate-900 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold">
              Prediction Accuracy
            </h3>

            <p className="mt-1 text-sm text-slate-500">
              How closely VEYTRA matches the simulation ground truth.
            </p>
          </div>

          <span className="text-2xl font-semibold">
            {overallAccuracy}%
          </span>
        </div>

        <div className="mt-8 grid grid-cols-1 gap-8 md:grid-cols-3">
          {/* Vehicle Count */}
          <div>
            <div className="flex items-center justify-between">
              <p className="text-sm text-slate-400">
                Vehicle Count
              </p>

              <p className="text-sm font-medium">
                {vehicleAccuracy}%
              </p>
            </div>

            <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-800">
              <div
                className="h-2 rounded-full bg-white"
                style={{
                  width: `${vehicleAccuracy}%`,
                }}
              />
            </div>

            <p className="mt-2 text-xs text-slate-500">
              Difference: {comparison.vehicle_count_difference}
            </p>
          </div>

          {/* Average Speed */}
          <div>
            <div className="flex items-center justify-between">
              <p className="text-sm text-slate-400">
                Average Speed
              </p>

              <p className="text-sm font-medium">
                {speedAccuracy}%
              </p>
            </div>

            <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-800">
              <div
                className="h-2 rounded-full bg-white"
                style={{
                  width: `${speedAccuracy}%`,
                }}
              />
            </div>

            <p className="mt-2 text-xs text-slate-500">
              Difference: {comparison.speed_difference} km/h
            </p>
          </div>

          {/* Congestion */}
          <div>
            <div className="flex items-center justify-between">
              <p className="text-sm text-slate-400">
                Congestion
              </p>

              <p className="text-sm font-medium">
                {congestionAccuracy}%
              </p>
            </div>

            <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-800">
              <div
                className="h-2 rounded-full bg-white"
                style={{
                  width: `${Math.max(0, congestionAccuracy)}%`,
                }}
              />
            </div>

            <p className="mt-2 text-xs text-slate-500">
              Difference:{" "}
              {Math.round(comparison.congestion_difference * 100)}%
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SimulationComparison