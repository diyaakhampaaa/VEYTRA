import { useEffect, useState } from "react"

import SourceBadge from "../components/SourceBadge"
import MapView from "../components/GISMapView"
import { checkBackend, getCameras } from "../api/client"

function CommandCenter() {
  const [backendStatus, setBackendStatus] = useState("Checking...")
  const [cameras, setCameras] = useState([])
  const [selectedCameraId, setSelectedCameraId] = useState(null)

  useEffect(() => {
    checkBackend()
      .then(() => setBackendStatus("Connected"))
      .catch(() => setBackendStatus("Offline"))

    getCameras()
      .then((data) => {
        const cameraList = Array.isArray(data)
          ? data
          : data?.cameras || []

        setCameras(cameraList)
      })
      .catch((error) => {
        console.error("Camera fetch error:", error)
        setCameras([])
      })
  }, [])

  const totalVehicles = cameras.reduce(
    (total, camera) => total + (camera.vehicles_detected || 0),
    0
  )

  const activeCameras = cameras.filter(
    (camera) =>
      camera.status?.toLowerCase() === "active"
  ).length

  const isConnected = backendStatus === "Connected"

  const handleViewCamera = (cameraId) => {
    setSelectedCameraId(cameraId)

    setTimeout(() => {
      document
        .getElementById("live-traffic-map")
        ?.scrollIntoView({
          behavior: "smooth",
          block: "center",
        })
    }, 50)
  }

  return (
    <div className="relative min-h-screen overflow-hidden">

      {/* =====================================================
          BACKGROUND GRID
          ===================================================== */}

      <div className="pointer-events-none fixed inset-0 opacity-[0.025]">
        <div className="veytra-grid h-full w-full" />
      </div>

      <div className="pointer-events-none absolute left-1/2 top-0 h-[500px] w-[700px] -translate-x-1/2 rounded-full bg-[var(--veytra-teal)]/[0.05] blur-3xl" />

      {/* =====================================================
          HEADER
          ===================================================== */}

      <header className="relative flex flex-col gap-5 border-b border-[var(--veytra-border)] pb-6 lg:flex-row lg:items-end lg:justify-between">

        <div>

          <div className="mb-3 flex items-center gap-2 text-[8px] uppercase tracking-[0.28em] text-[var(--veytra-cyan)]">
            <span className="h-1.5 w-1.5 rounded-full bg-[var(--veytra-cyan)]" />
            City Intelligence Network
          </div>

          <h1 className="text-3xl font-semibold tracking-[-0.03em] text-[var(--veytra-heading)]">
            Command Center
          </h1>

          <p className="mt-2 max-w-xl text-sm text-[var(--veytra-muted)]">
            One connected view of cameras, vehicles and city movement.
          </p>

        </div>

        {/* System status */}

        <div className="flex items-center gap-3">

          <div className="veytra-panel rounded-lg px-4 py-2.5">

            <div className="flex items-center gap-2">

              <span
                className={
                  isConnected
                    ? "veytra-live-dot"
                    : "veytra-warning-dot"
                }
              />

              <div>

                <div className="text-[8px] uppercase tracking-[0.18em] text-[var(--veytra-label)]">
                  Backend
                </div>

                <div
                  className={`mt-0.5 text-[10px] font-medium ${
                    isConnected
                      ? "text-[var(--veytra-teal)]"
                      : "text-[var(--veytra-warning)]"
                  }`}
                >
                  {backendStatus}
                </div>

              </div>

            </div>

          </div>

          <SourceBadge source="simulated" />

        </div>

      </header>

      {/* =====================================================
          SYSTEM METRICS
          ===================================================== */}

<section className="relative mt-8 grid grid-cols-1 gap-3 md:grid-cols-3">
        {/* Cameras */}

        <div className="veytra-panel veytra-panel-hover veytra-hud rounded-xl p-5">

          <div className="flex items-start justify-between">

            <div>

              <div className="text-[8px] uppercase tracking-[0.22em] text-[var(--veytra-dim)]">
                Connected Nodes
              </div>

              <div className="veytra-stat-value mt-3 text-3xl font-semibold">
                {String(activeCameras).padStart(2, "0")}
              </div>

            </div>

            <div className="rounded-lg border border-[var(--veytra-border)] bg-[var(--veytra-cyan)]/[0.08] px-2 py-1 text-[7px] uppercase tracking-widest text-[var(--veytra-cyan)]">
              LIVE
            </div>

          </div>

          <div className="mt-4 h-px bg-gradient-to-r from-[var(--veytra-border-strong)] to-transparent" />

          <div className="mt-3 text-[8px] text-[var(--veytra-dim)]">
            Active camera infrastructure
          </div>

        </div>

        {/* Vehicles */}

        <div className="veytra-panel veytra-panel-hover veytra-hud rounded-xl p-5">

          <div className="flex items-start justify-between">

            <div>

              <div className="text-[8px] uppercase tracking-[0.22em] text-[var(--veytra-dim)]">
                Vehicles Detected
              </div>

              <div className="veytra-stat-value mt-3 text-3xl font-semibold">
                {String(totalVehicles).padStart(2, "0")}
              </div>

            </div>

            <div className="rounded-lg border border-[var(--veytra-border)] bg-[var(--veytra-teal)]/[0.08] px-2 py-1 text-[7px] uppercase tracking-widest text-[var(--veytra-teal)]">
              TRACKING
            </div>

          </div>

          <div className="mt-4 h-px bg-gradient-to-r from-[var(--veytra-border-strong)] to-transparent" />

          <div className="mt-3 text-[8px] text-[var(--veytra-dim)]">
            Cross-camera vehicle activity
          </div>

        </div>

        {/* System */}

        <div className="veytra-panel veytra-panel-hover veytra-hud rounded-xl p-5">

          <div className="flex items-start justify-between">

            <div>

              <div className="text-[8px] uppercase tracking-[0.22em] text-[var(--veytra-dim)]">
                Intelligence Pipeline
              </div>

              <div className="mt-3 text-2xl font-semibold text-[var(--veytra-cyan)]">
                OPERATIONAL
              </div>

            </div>

            <div className="flex h-8 w-8 items-center justify-center rounded-lg border border-[var(--veytra-border)] bg-[var(--veytra-cyan)]/[0.08]">
              <span className="veytra-live-dot" />
            </div>

          </div>

          <div className="mt-4 h-px bg-gradient-to-r from-[var(--veytra-border-strong)] to-transparent" />

          <div className="mt-3 text-[8px] text-[var(--veytra-dim)]">
            DETECT → READ → TRACK → VERIFY → ANALYZE
          </div>

        </div>

      </section>

      {/* =====================================================
          MAP
          ===================================================== */}

      <section
        id="live-traffic-map"
        className="relative mt-8"
      >

        <div className="mb-3 flex items-end justify-between">

          <div>

            <div className="flex items-center gap-2">

              <span className="text-[8px] uppercase tracking-[0.25em] text-[var(--veytra-cyan)]">
                Network Visualization
              </span>

              <span className="h-px w-8 bg-[var(--veytra-border-strong)]" />

            </div>

            <h2 className="mt-2 text-lg font-medium text-[var(--veytra-heading)]">
              Live Traffic Map
            </h2>

            <p className="mt-1 text-xs text-[var(--veytra-dim)]">
              Cross-camera vehicle activity and network overview.
            </p>

          </div>

          <div className="hidden items-center gap-4 text-[7px] uppercase tracking-[0.16em] text-[var(--veytra-dim)] sm:flex">

            <div className="flex items-center gap-2">
              <span className="veytra-live-dot" />
              Active
            </div>

            <div className="flex items-center gap-2">
              <span className="veytra-sim-dot" />
              Simulated
            </div>

          </div>

        </div>

        <div className="veytra-panel veytra-hud overflow-hidden rounded-xl p-2">

          <div className="h-[430px] overflow-hidden rounded-lg">

            <MapView
              cameras={cameras}
              selectedCameraId={selectedCameraId}
              onCameraSelect={setSelectedCameraId}
            />

          </div>

        </div>

      </section>

      {/* =====================================================
          CAMERA NETWORK
          ===================================================== */}

      <section className="relative mt-8 pb-10">

        <div className="mb-4 flex items-end justify-between">

          <div>

            <div className="text-[8px] uppercase tracking-[0.25em] text-[var(--veytra-cyan)]">
              Infrastructure
            </div>

            <h2 className="mt-2 text-lg font-medium text-[var(--veytra-heading)]">
              Camera Network
            </h2>

          </div>

          <div className="text-[8px] uppercase tracking-[0.16em] text-[var(--veytra-dim)]">
            {cameras.length} nodes connected
          </div>

        </div>

        <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-3">

          {cameras.map((camera) => (

            <div
              key={camera.camera_id}
              className="veytra-panel veytra-panel-hover veytra-hud group rounded-xl p-4"
            >

              {/* Camera header */}

              <div className="flex items-start justify-between">

                <div className="flex items-center gap-3">

                  <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-[var(--veytra-border)] bg-[var(--veytra-cyan)]/[0.06] text-[11px] text-[var(--veytra-cyan)]">
                    ◉
                  </div>

                  <div>

                    <h3 className="text-sm font-semibold tracking-wide text-[var(--veytra-heading)]">
                      {camera.camera_id}
                    </h3>

                    <div className="mt-1 flex items-center gap-2">

                      <span
                        className={
                          camera.status?.toLowerCase() === "active"
                            ? "veytra-live-dot"
                            : "veytra-sim-dot"
                        }
                      />

                      <span className="text-[8px] uppercase tracking-[0.15em] text-[var(--veytra-muted)]">
                        {camera.status || "Unknown"}
                      </span>

                    </div>

                  </div>

                </div>

                <SourceBadge source={camera.source || "simulated"} />

              </div>

              {/* Camera visual */}

              <div className="relative mt-4 h-28 overflow-hidden rounded-lg border border-[var(--veytra-border)] bg-[#0c1116]">

                {/* Road */}

                <div className="absolute left-1/2 top-[-20%] h-[150%] w-[34%] -translate-x-1/2 rotate-[3deg] bg-white/[0.06]" />

                {/* Road divider */}

                <div className="absolute left-1/2 top-0 h-full -translate-x-1/2 border-l border-dashed border-white/[0.10]" />

                {/* Vehicle marker */}

                <div className="absolute left-[42%] top-[42%] h-7 w-4 rounded-sm border border-[var(--veytra-cyan)]/50 bg-[var(--veytra-cyan)]/[0.12]">

                  <div className="absolute -left-px -top-px h-2 w-2 border-l border-t border-[var(--veytra-cyan)]" />
                  <div className="absolute -right-px -top-px h-2 w-2 border-r border-t border-[var(--veytra-cyan)]" />
                  <div className="absolute -bottom-px -left-px h-2 w-2 border-b border-l border-[var(--veytra-cyan)]" />
                  <div className="absolute -bottom-px -right-px h-2 w-2 border-b border-r border-[var(--veytra-cyan)]" />

                </div>

                {/* Scan lines */}

                <div className="absolute inset-0 bg-[linear-gradient(transparent_50%,rgba(35,139,139,0.05)_50%)] bg-[length:100%_4px]" />

                <div className="absolute left-3 top-3 text-[7px] uppercase tracking-[0.18em] text-[var(--veytra-cyan)]/70">
                  {camera.camera_id} // FEED
                </div>

                <div className="absolute bottom-3 right-3 text-[7px] uppercase tracking-[0.15em] text-white/40">
                  ANPR • RE-ID
                </div>

              </div>

              {/* Stats */}

              <div className="mt-3 grid grid-cols-2 gap-2">

                <div className="rounded-lg border border-[var(--veytra-border)] bg-black/[0.02] p-3">

                  <div className="text-[7px] uppercase tracking-[0.16em] text-[var(--veytra-dim)]">
                    Vehicles
                  </div>

                  <div className="veytra-stat-value mt-1 text-lg font-semibold">
                    {camera.vehicles_detected || 0}
                  </div>

                </div>

                <div className="rounded-lg border border-[var(--veytra-border)] bg-black/[0.02] p-3">

                  <div className="text-[7px] uppercase tracking-[0.16em] text-[var(--veytra-dim)]">
                    Source
                  </div>

                  <div className="mt-1 text-[10px] font-medium uppercase text-[var(--veytra-cyan)]">
                    {camera.source || "simulated"}
                  </div>

                </div>

              </div>

              {/* Button */}

              <button
                type="button"
                onClick={() => handleViewCamera(camera.camera_id)}
                className="mt-3 w-full rounded-lg border border-[var(--veytra-border)] bg-black/[0.02] px-4 py-2.5 text-[8px] font-medium uppercase tracking-[0.18em] text-[var(--veytra-muted)] transition hover:border-[var(--veytra-cyan)]/40 hover:bg-[var(--veytra-cyan)]/[0.06] hover:text-[var(--veytra-cyan)]"
              >
                View Camera →
              </button>

            </div>

          ))}

        </div>

      </section>

    </div>
  )
}

export default CommandCenter
