import { useEffect, useMemo, useState } from "react"
import SourceBadge from "../components/SourceBadge"
import { getAlerts } from "../api/client"

function Alerts() {
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [filter, setFilter] = useState("ALL")
  const [selectedAlert, setSelectedAlert] = useState(null)

  useEffect(() => {
    loadAlerts()
  }, [])

  const loadAlerts = async () => {
    setLoading(true)
    setError("")

    try {
      const data = await getAlerts()

      const normalized =
        Array.isArray(data)
          ? data
          : Array.isArray(data?.alerts)
            ? data.alerts
            : Array.isArray(data?.data)
              ? data.data
              : []

      setAlerts(normalized)
    } catch (err) {
      console.error("Alerts fetch error:", err)
      setError("Unable to reach the alert intelligence service.")
    } finally {
      setLoading(false)
    }
  }

  const normalizedAlerts = useMemo(() => {
    return alerts.map((alert, index) => ({
      id:
        alert.id ||
        alert.alert_id ||
        alert.event_id ||
        `ALERT-${String(index + 1).padStart(3, "0")}`,

      type:
        alert.type ||
        alert.alert_type ||
        alert.category ||
        "TRAFFIC EVENT",

      severity:
        String(
          alert.severity ||
            alert.priority ||
            alert.level ||
            "MEDIUM"
        ).toUpperCase(),

      message:
        alert.message ||
        alert.description ||
        alert.reason ||
        "Intelligence event detected.",

      camera:
        alert.camera_id ||
        alert.camera ||
        "NETWORK",

      vehicle:
        alert.vehicle_id ||
        alert.plate_number ||
        alert.plate ||
        "N/A",

      timestamp:
        alert.timestamp ||
        alert.created_at ||
        alert.time ||
        "—",

      source:
        alert.source ||
        "simulated",
    }))
  }, [alerts])

  const filteredAlerts =
    filter === "ALL"
      ? normalizedAlerts
      : normalizedAlerts.filter(
          (alert) => alert.severity === filter
        )

  const criticalCount = normalizedAlerts.filter(
    (alert) => alert.severity === "CRITICAL"
  ).length

  const highCount = normalizedAlerts.filter(
    (alert) => alert.severity === "HIGH"
  ).length

  const mediumCount = normalizedAlerts.filter(
    (alert) => alert.severity === "MEDIUM"
  ).length

  const getSeverityStyle = (severity) => {
    if (severity === "CRITICAL") {
      return {
        badge:
          "border-red-400/25 bg-red-400/[0.06] text-red-300",
        dot: "bg-red-300 shadow-[0_0_9px_rgba(248,113,113,0.8)]",
        line: "border-l-red-400/70",
      }
    }

    if (severity === "HIGH") {
      return {
        badge:
          "border-amber-400/25 bg-amber-400/[0.06] text-amber-300",
        dot: "bg-amber-300 shadow-[0_0_9px_rgba(251,191,36,0.8)]",
        line: "border-l-amber-400/70",
      }
    }

    return {
      badge:
        "border-cyan-400/20 bg-cyan-400/[0.04] text-cyan-300",
      dot: "bg-cyan-300 shadow-[0_0_9px_rgba(34,211,238,0.7)]",
      line: "border-l-cyan-400/50",
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-[#02070b] text-white">
        <div className="mb-8">
          <div className="mb-2 flex items-center gap-2 text-[9px] uppercase tracking-[0.28em] text-cyan-400">
            <span className="veytra-live-dot" />
            Security Intelligence
          </div>

          <h1 className="text-3xl font-semibold">
            Alert Command
          </h1>

          <p className="mt-2 text-sm text-slate-500">
            Loading network events and intelligence alerts.
          </p>
        </div>

        <div className="veytra-panel veytra-hud flex min-h-[400px] items-center justify-center">
          <div className="text-sm text-slate-600">
            Synchronizing alert network...
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="relative min-h-screen overflow-hidden">

      {/* Background */}

      <div className="pointer-events-none fixed inset-0 opacity-[0.025]">
        <div className="veytra-grid h-full w-full" />
      </div>

      <div className="pointer-events-none absolute left-1/2 top-0 h-96 w-96 -translate-x-1/2 rounded-full bg-cyan-400/[0.025] blur-3xl" />


      {/* Header */}

      <header className="relative border-b border-cyan-300/[0.08] pb-6">

        <div className="flex flex-col justify-between gap-5 lg:flex-row lg:items-end">

          <div>

            <div className="flex items-center gap-2 text-[9px] uppercase tracking-[0.28em] text-cyan-300/60">
              <span className="veytra-live-dot" />
              Security Intelligence
            </div>

            <h1 className="mt-3 text-3xl font-semibold tracking-tight text-white">
              Alert Command
            </h1>

            <p className="mt-2 max-w-2xl text-sm text-slate-500">
              Monitor anomalous events, vehicle intelligence,
              and network-level incidents.
            </p>

          </div>

          <div className="veytra-panel px-4 py-3">

            <div className="mb-1 text-[7px] uppercase tracking-[0.2em] text-slate-600">
              Data Source
            </div>

            <SourceBadge source="simulated" />

          </div>

        </div>

      </header>


      {/* Summary */}

      <section className="mt-7 grid grid-cols-1 gap-4 sm:grid-cols-3">

        <div className="veytra-panel veytra-hud p-5">

          <div className="text-[8px] uppercase tracking-[0.2em] text-slate-600">
            Critical
          </div>

          <div className="mt-3 flex items-end gap-3">

            <span className="font-mono text-3xl text-red-300">
              {criticalCount}
            </span>

            <span className="mb-1 text-[7px] uppercase tracking-[0.15em] text-red-300/40">
              Immediate
            </span>

          </div>

        </div>


        <div className="veytra-panel veytra-hud p-5">

          <div className="text-[8px] uppercase tracking-[0.2em] text-slate-600">
            High Priority
          </div>

          <div className="mt-3 flex items-end gap-3">

            <span className="font-mono text-3xl text-amber-300">
              {highCount}
            </span>

            <span className="mb-1 text-[7px] uppercase tracking-[0.15em] text-amber-300/40">
              Attention
            </span>

          </div>

        </div>


        <div className="veytra-panel veytra-hud p-5">

          <div className="text-[8px] uppercase tracking-[0.2em] text-slate-600">
            Network Events
          </div>

          <div className="mt-3 flex items-end gap-3">

            <span className="font-mono text-3xl text-cyan-200">
              {normalizedAlerts.length}
            </span>

            <span className="mb-1 text-[7px] uppercase tracking-[0.15em] text-cyan-300/40">
              Total
            </span>

          </div>

        </div>

      </section>


      {/* Alert console */}

      <section className="mt-8">

        <div className="mb-4 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">

          <div>

            <div className="text-[8px] uppercase tracking-[0.22em] text-cyan-300/50">
              Incident Feed
            </div>

            <h2 className="mt-2 text-lg font-medium text-slate-200">
              Network Events
            </h2>

          </div>


          <div className="flex flex-wrap gap-2">

            {["ALL", "CRITICAL", "HIGH", "MEDIUM"].map((item) => (

              <button
                key={item}
                type="button"
                onClick={() => setFilter(item)}
                className={`border px-3 py-2 text-[7px] font-semibold uppercase tracking-[0.16em] transition ${
                  filter === item
                    ? "border-cyan-300/30 bg-cyan-300/[0.08] text-cyan-200"
                    : "border-white/[0.06] bg-white/[0.015] text-slate-600 hover:border-cyan-300/20 hover:text-slate-400"
                }`}
              >
                {item}
              </button>

            ))}

          </div>

        </div>


        {error && (

          <div className="mb-4 rounded-lg border border-amber-300/10 bg-amber-300/[0.025] px-4 py-3">

            <div className="flex items-center justify-between gap-4">

              <div className="flex items-center gap-3">

                <span className="veytra-warning-dot" />

                <span className="text-[8px] uppercase tracking-[0.14em] text-amber-200/70">
                  {error}
                </span>

              </div>

              <button
                type="button"
                onClick={loadAlerts}
                className="text-[7px] uppercase tracking-[0.15em] text-cyan-300/60 hover:text-cyan-200"
              >
                Retry
              </button>

            </div>

          </div>

        )}


        {filteredAlerts.length === 0 ? (

          <div className="veytra-panel veytra-hud flex min-h-[350px] items-center justify-center">

            <div className="text-center">

              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full border border-cyan-300/10 bg-cyan-300/[0.025]">

                <span className="h-3 w-3 rounded-full border border-cyan-300/40" />

              </div>

              <div className="mt-5 text-sm text-slate-500">
                No matching network events
              </div>

              <div className="mt-2 text-[7px] uppercase tracking-[0.18em] text-slate-700">
                Alert feed clear
              </div>

            </div>

          </div>

        ) : (

          <div className="space-y-3">

            {filteredAlerts.map((alert) => {

              const style = getSeverityStyle(alert.severity)

              const selected =
                selectedAlert?.id === alert.id

              return (

                <button
                  key={alert.id}
                  type="button"
                  onClick={() =>
                    setSelectedAlert(
                      selected ? null : alert
                    )
                  }
                  className={`veytra-panel veytra-panel-hover w-full border-l-2 p-5 text-left transition ${style.line} ${
                    selected
                      ? "border-cyan-300/25 bg-cyan-300/[0.025]"
                      : ""
                  }`}
                >

                  <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">

                    <div className="flex items-start gap-4">

                      <div className="mt-1 flex h-9 w-9 shrink-0 items-center justify-center rounded border border-white/[0.06] bg-white/[0.015]">

                        <span
                          className={`h-2 w-2 rounded-full ${style.dot}`}
                        />

                      </div>


                      <div>

                        <div className="flex flex-wrap items-center gap-3">

                          <span className="font-mono text-xs text-slate-300">
                            {alert.id}
                          </span>

                          <span
                            className={`border px-2 py-1 text-[6px] font-semibold uppercase tracking-[0.16em] ${style.badge}`}
                          >
                            {alert.severity}
                          </span>

                          <span className="text-[7px] uppercase tracking-[0.15em] text-slate-700">
                            {alert.type}
                          </span>

                        </div>

                        <div className="mt-2 text-sm text-slate-400">
                          {alert.message}
                        </div>

                      </div>

                    </div>


                    <div className="grid grid-cols-3 gap-5 lg:min-w-[330px]">

                      <div>

                        <div className="text-[6px] uppercase tracking-[0.15em] text-slate-700">
                          Camera
                        </div>

                        <div className="mt-1 font-mono text-[9px] text-cyan-200/60">
                          {alert.camera}
                        </div>

                      </div>


                      <div>

                        <div className="text-[6px] uppercase tracking-[0.15em] text-slate-700">
                          Vehicle
                        </div>

                        <div className="mt-1 font-mono text-[9px] text-slate-400">
                          {alert.vehicle}
                        </div>

                      </div>


                      <div>

                        <div className="text-[6px] uppercase tracking-[0.15em] text-slate-700">
                          Time
                        </div>

                        <div className="mt-1 font-mono text-[9px] text-slate-500">
                          {alert.timestamp}
                        </div>

                      </div>

                    </div>

                  </div>


                  {selected && (

                    <div className="mt-5 border-t border-white/[0.05] pt-4">

                      <div className="grid gap-3 sm:grid-cols-3">

                        <div className="rounded border border-white/[0.05] bg-white/[0.015] p-3">

                          <div className="text-[6px] uppercase tracking-[0.15em] text-slate-700">
                            Source
                          </div>

                          <div className="mt-2">
                            <SourceBadge source={alert.source} />
                          </div>

                        </div>

                        <div className="rounded border border-white/[0.05] bg-white/[0.015] p-3">

                          <div className="text-[6px] uppercase tracking-[0.15em] text-slate-700">
                            Network State
                          </div>

                          <div className="mt-2 text-[8px] uppercase tracking-[0.12em] text-cyan-300">
                            MONITORED
                          </div>

                        </div>

                        <div className="rounded border border-white/[0.05] bg-white/[0.015] p-3">

                          <div className="text-[6px] uppercase tracking-[0.15em] text-slate-700">
                            Investigation
                          </div>

                          <div className="mt-2 text-[8px] uppercase tracking-[0.12em] text-slate-400">
                            AVAILABLE
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


      {/* Footer */}

      <div className="mt-10 flex items-center justify-between border-t border-cyan-400/10 py-5 text-[7px] uppercase tracking-[0.18em] text-slate-700">

        <span>
          VEYTRA / Alert Command
        </span>

        <span>
          Detection • Verification • Response
        </span>

      </div>

    </div>
  )
}

export default Alerts