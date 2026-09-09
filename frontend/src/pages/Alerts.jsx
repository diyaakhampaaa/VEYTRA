import { useEffect, useState } from "react"
import SourceBadge from "../components/SourceBadge"
import { getAlerts } from "../api/client"

function Alerts() {
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)
  const [filter, setFilter] = useState("All")

  useEffect(() => {
    getAlerts()
      .then((data) => {
        setAlerts(data.alerts)
      })
      .catch((error) => {
        console.error("Alerts fetch error:", error)
        setError(true)
      })
      .finally(() => {
        setLoading(false)
      })
  }, [])

  const filteredAlerts =
    filter === "All"
      ? alerts
      : alerts.filter(
          (alert) => alert.severity === filter
        )

  const activeAlerts = alerts.filter(
    (alert) => alert.status === "Active"
  ).length

  const highAlerts = alerts.filter(
    (alert) => alert.severity === "High"
  ).length

  const mediumAlerts = alerts.filter(
    (alert) => alert.severity === "Medium"
  ).length

  const getSeverityStyle = (severity) => {
    if (severity === "High") {
      return "border-red-500/30 bg-red-500/10 text-red-400"
    }

    if (severity === "Medium") {
      return "border-yellow-500/30 bg-yellow-500/10 text-yellow-400"
    }

    return "border-green-500/30 bg-green-500/10 text-green-400"
  }

  const getSeverityDot = (severity) => {
    if (severity === "High") {
      return "bg-red-400"
    }

    if (severity === "Medium") {
      return "bg-yellow-400"
    }

    return "bg-green-400"
  }

  return (
    <div>
      {/* Header */}

      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold">
            Alerts
          </h2>

          <p className="mt-2 text-slate-400">
            Monitor anomalies and important traffic events.
          </p>
        </div>

        <SourceBadge source="simulated" />
      </div>

      {/* Backend Error */}

      {error && (
        <div className="mt-6 rounded-xl border border-red-500/30 bg-red-500/10 p-4">
          <p className="text-sm text-red-400">
            Unable to load alerts. Please check that the backend is running.
          </p>
        </div>
      )}

      {/* Summary Cards */}

      <div className="mt-8 grid grid-cols-1 gap-4 md:grid-cols-3">

        <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
          <p className="text-sm text-slate-400">
            Active Alerts
          </p>

          <p className="mt-2 text-3xl font-semibold">
            {activeAlerts}
          </p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
          <p className="text-sm text-slate-400">
            High Severity
          </p>

          <p className="mt-2 text-3xl font-semibold text-red-400">
            {highAlerts}
          </p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
          <p className="text-sm text-slate-400">
            Medium Severity
          </p>

          <p className="mt-2 text-3xl font-semibold text-yellow-400">
            {mediumAlerts}
          </p>
        </div>

      </div>

      {/* Filters */}

      <div className="mt-8 flex items-center gap-2">
        {["All", "High", "Medium", "Low"].map(
          (severity) => (
            <button
              key={severity}
              onClick={() => setFilter(severity)}
              className={`rounded-lg px-4 py-2 text-sm font-medium transition ${
                filter === severity
                  ? "bg-white text-slate-950"
                  : "bg-slate-900 text-slate-400 hover:bg-slate-800 hover:text-white"
              }`}
            >
              {severity}
            </button>
          )
        )}
      </div>

      {/* Alert List */}

      <div className="mt-6">

        {loading && (
          <p className="text-slate-400">
            Loading alerts...
          </p>
        )}

        {!loading && !error && filteredAlerts.length === 0 && (
          <div className="rounded-xl border border-slate-800 bg-slate-900 p-8 text-center">
            <p className="text-slate-400">
              No alerts found.
            </p>
          </div>
        )}

        <div className="space-y-4">

          {filteredAlerts.map((alert) => (
            <div
              key={alert.alert_id}
              className="rounded-xl border border-slate-800 bg-slate-900 p-6"
            >

              {/* Alert Header */}

              <div className="flex items-start justify-between">

                <div className="flex items-start gap-4">

                  <div
                    className={`mt-1 h-3 w-3 rounded-full ${getSeverityDot(
                      alert.severity
                    )}`}
                  />

                  <div>
                    <div className="flex items-center gap-3">

                      <h3 className="text-lg font-semibold">
                        {alert.type}
                      </h3>

                      <span
                        className={`rounded-full border px-2 py-1 text-xs font-medium ${getSeverityStyle(
                          alert.severity
                        )}`}
                      >
                        {alert.severity}
                      </span>

                    </div>

                    <p className="mt-1 text-xs text-slate-500">
                      {alert.alert_id}
                    </p>
                  </div>

                </div>

                <SourceBadge source={alert.source} />

              </div>

              {/* Message */}

              <div className="mt-5 rounded-lg bg-slate-800 p-4">

                <p className="text-sm text-slate-300">
                  {alert.message}
                </p>

              </div>

              {/* Details */}

              <div className="mt-5 grid grid-cols-2 gap-4 md:grid-cols-4">

                <div>
                  <p className="text-xs text-slate-500">
                    Camera
                  </p>

                  <p className="mt-1 font-medium">
                    {alert.camera_id}
                  </p>
                </div>

                <div>
                  <p className="text-xs text-slate-500">
                    Vehicles
                  </p>

                  <p className="mt-1 font-medium">
                    {alert.vehicle_count}
                  </p>
                </div>

                <div>
                  <p className="text-xs text-slate-500">
                    Congestion
                  </p>

                  <p className="mt-1 font-medium">
                    {Math.round(
                      alert.congestion_score * 100
                    )}
                    %
                  </p>
                </div>

                <div>
                  <p className="text-xs text-slate-500">
                    Time
                  </p>

                  <p className="mt-1 font-medium">
                    {alert.timestamp}
                  </p>
                </div>

              </div>

              {/* Status */}

              <div className="mt-5 flex items-center justify-between border-t border-slate-800 pt-4">

                <div className="flex items-center gap-2">

                  <span
                    className={`h-2 w-2 rounded-full ${
                      alert.status === "Active"
                        ? "bg-red-400"
                        : "bg-slate-500"
                    }`}
                  />

                  <span className="text-sm text-slate-400">
                    {alert.status}
                  </span>

                </div>

                <button
                  className="rounded-lg border border-slate-700 px-4 py-2 text-sm transition hover:bg-slate-800"
                  onClick={() =>
                    console.log(
                      "Alert selected:",
                      alert.alert_id
                    )
                  }
                >
                  View Details
                </button>

              </div>

            </div>
          ))}

        </div>
      </div>
    </div>
  )
}

export default Alerts