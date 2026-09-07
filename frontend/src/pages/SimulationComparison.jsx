import { useEffect, useState } from "react"
import SourceBadge from "../components/SourceBadge"
import { getSimulationComparison } from "../api/client"

function SimulationComparison() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getSimulationComparison()
      .then((result) => {
        setData(result)
      })
      .catch((error) => {
        console.error(
          "Simulation comparison error:",
          error
        )
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

  if (!data) {
    return (
      <div>
        <h2 className="text-2xl font-semibold">
          Simulation Comparison
        </h2>

        <div className="mt-8 rounded-xl border border-slate-800 bg-slate-900 p-6">
          <p className="text-slate-400">
            Simulation data unavailable.
          </p>
        </div>
      </div>
    )
  }

  const simulation = data.simulation
  const groundTruth = data.ground_truth
  const comparison = data.comparison

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

      {/* Scenario */}

      <div className="mt-8 rounded-xl border border-slate-800 bg-slate-900 p-5">
        <div className="flex items-center justify-between">

          <div>
            <p className="text-xs uppercase tracking-wider text-slate-500">
              Simulation Scenario
            </p>

            <h3 className="mt-1 text-xl font-semibold">
              {simulation.scenario_id}
            </h3>
          </div>

          <div className="rounded-lg bg-slate-800 px-4 py-2">
            <span className="text-sm text-slate-400">
              Overall Accuracy
            </span>

            <span className="ml-3 text-lg font-semibold">
              {Math.round(
                comparison.overall_accuracy * 100
              )}
              %
            </span>
          </div>

        </div>
      </div>

      {/* Main comparison */}

      <div className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-2">

        {/* Simulation */}

        <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">

          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">
              VEYTRA Prediction
            </h3>

            <SourceBadge source="simulated" />
          </div>

          <div className="mt-6 space-y-5">

            <div>
              <p className="text-sm text-slate-400">
                Vehicles
              </p>

              <p className="mt-1 text-3xl font-semibold">
                {simulation.vehicles}
              </p>
            </div>

            <div>
              <p className="text-sm text-slate-400">
                Average Speed
              </p>

              <p className="mt-1 text-3xl font-semibold">
                {simulation.average_speed}
                <span className="ml-2 text-sm text-slate-500">
                  km/h
                </span>
              </p>
            </div>

            <div>
              <p className="text-sm text-slate-400">
                Congestion
              </p>

              <p className="mt-1 text-3xl font-semibold">
                {Math.round(
                  simulation.congestion_score * 100
                )}
                %
              </p>
            </div>

          </div>
        </div>

        {/* Ground truth */}

        <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">

          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">
              Ground Truth
            </h3>

            <span className="rounded-full bg-green-500/20 px-3 py-1 text-xs font-medium text-green-400">
              Reference
            </span>
          </div>

          <div className="mt-6 space-y-5">

            <div>
              <p className="text-sm text-slate-400">
                Vehicles
              </p>

              <p className="mt-1 text-3xl font-semibold">
                {groundTruth.vehicles}
              </p>
            </div>

            <div>
              <p className="text-sm text-slate-400">
                Average Speed
              </p>

              <p className="mt-1 text-3xl font-semibold">
                {groundTruth.average_speed}
                <span className="ml-2 text-sm text-slate-500">
                  km/h
                </span>
              </p>
            </div>

            <div>
              <p className="text-sm text-slate-400">
                Congestion
              </p>

              <p className="mt-1 text-3xl font-semibold">
                {Math.round(
                  groundTruth.congestion_score * 100
                )}
                %
              </p>
            </div>

          </div>
        </div>

      </div>

      {/* Accuracy */}

      <div className="mt-6 rounded-xl border border-slate-800 bg-slate-900 p-6">

        <h3 className="text-lg font-semibold">
          Prediction Accuracy
        </h3>

        <div className="mt-6 grid grid-cols-1 gap-6 md:grid-cols-3">

          <div>
            <div className="flex justify-between">
              <p className="text-sm text-slate-400">
                Vehicle Count
              </p>

              <p className="text-sm font-medium">
                {Math.round(
                  comparison.vehicle_count_accuracy * 100
                )}
                %
              </p>
            </div>

            <div className="mt-2 h-2 rounded-full bg-slate-800">
              <div
                className="h-2 rounded-full bg-white"
                style={{
                  width: `${
                    comparison.vehicle_count_accuracy * 100
                  }%`,
                }}
              />
            </div>

            <p className="mt-2 text-xs text-slate-500">
              Difference:{" "}
              {comparison.vehicle_count_difference}
            </p>
          </div>

          <div>
            <div className="flex justify-between">
              <p className="text-sm text-slate-400">
                Average Speed
              </p>

              <p className="text-sm font-medium">
                {Math.round(
                  comparison.speed_accuracy * 100
                )}
                %
              </p>
            </div>

            <div className="mt-2 h-2 rounded-full bg-slate-800">
              <div
                className="h-2 rounded-full bg-white"
                style={{
                  width: `${
                    comparison.speed_accuracy * 100
                  }%`,
                }}
              />
            </div>

            <p className="mt-2 text-xs text-slate-500">
              Difference:{" "}
              {comparison.speed_difference} km/h
            </p>
          </div>

          <div>
            <div className="flex justify-between">
              <p className="text-sm text-slate-400">
                Congestion
              </p>

              <p className="text-sm font-medium">
                {Math.round(
                  (1 -
                    Math.abs(
                      comparison.congestion_difference
                    )) *
                    100
                )}
                %
              </p>
            </div>

            <div className="mt-2 h-2 rounded-full bg-slate-800">
              <div
                className="h-2 rounded-full bg-white"
                style={{
                  width: `${
                    (1 -
                      Math.abs(
                        comparison.congestion_difference
                      )) *
                    100
                  }%`,
                }}
              />
            </div>

            <p className="mt-2 text-xs text-slate-500">
              Difference:{" "}
              {Math.round(
                comparison.congestion_difference * 100
              )}
              %
            </p>
          </div>

        </div>
      </div>

    </div>
  )
}

export default SimulationComparison