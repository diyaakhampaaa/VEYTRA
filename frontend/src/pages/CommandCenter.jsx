import { useEffect, useState } from "react"

import SourceBadge from "../components/SourceBadge"
import MapView from "../components/MapView"
import { checkBackend, getCameras } from "../api/client"

function CommandCenter() {
  const [backendStatus, setBackendStatus] = useState("Checking...")
  const [cameras, setCameras] = useState([])

  useEffect(() => {
    checkBackend()
      .then(() => setBackendStatus("Connected"))
      .catch(() => setBackendStatus("Offline"))

    getCameras()
      .then((data) => {
        setCameras(data.cameras)
      })
      .catch((error) => {
        console.error("Camera fetch error:", error)
      })
  }, [])

  const totalVehicles = cameras.reduce(
    (total, camera) => total + camera.vehicles_detected,
    0
  )

  const activeCameras = cameras.filter(
    (camera) => camera.status === "Active"
  ).length

  const isConnected = backendStatus === "Connected"

  return (
    <div className="relative min-h-screen overflow-hidden">

      {/* =====================================================
          BACKGROUND GRID
          ===================================================== */}

      <div className="pointer-events-none fixed inset-0 opacity-[0.025]">
        <div className="veytra-grid h-full w-full" />
      </div>

      <div className="pointer-events-none absolute left-1/2 top-0 h-[500px] w-[700px] -translate-x-1/2 rounded-full bg-cyan-400/[0.025] blur-3xl" />


      {/* =====================================================
          HEADER
          ===================================================== */}

      <header className="relative flex flex-col gap-5 border-b border-cyan-300/[0.08] pb-6 lg:flex-row lg:items-end lg:justify-between">

        <div>

          <div className="mb-3 flex items-center gap-2 text-[8px] uppercase tracking-[0.28em] text-cyan-300/50">
            <span className="h-1.5 w-1.5 rounded-full bg-cyan-300 shadow-[0_0_8px_#22d3ee]" />
            City Intelligence Network
          </div>

          <h1 className="text-3xl font-semibold tracking-[-0.03em] text-white">
            Command Center
          </h1>

          <p className="mt-2 max-w-xl text-sm text-slate-500">
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

                <div className="text-[8px] uppercase tracking-[0.18em] text-slate-500">
                  Backend
                </div>

                <div
                  className={`mt-0.5 text-[10px] font-medium ${
                    isConnected
                      ? "text-cyan-200"
                      : "text-amber-300"
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

      <section className="relative mt-6 grid grid-cols-1 gap-3 sm:grid-cols-3">

        {/* Cameras */}

        <div className="veytra-panel veytra-panel-hover veytra-hud rounded-xl p-5">

          <div className="flex items-start justify-between">

            <div>
              <div className="text-[8px] uppercase tracking-[0.22em] text-slate-600">
                Connected Nodes
              </div>

              <div className="mt-3 text-3xl font-semibold text-white">
                {String(activeCameras).padStart(2, "0")}
              </div>
            </div>

            <div className="rounded-lg border border-cyan-300/10 bg-cyan-300/[0.04] px-2 py-1 text-[7px] uppercase tracking-widest text-cyan-300/60">
              LIVE
            </div>

          </div>

          <div className="mt-4 h-px bg-gradient-to-r from-cyan-300/20 to-transparent" />

          <div className="mt-3 text-[8px] text-slate-600">
            Active camera infrastructure
          </div>

        </div>


        {/* Vehicles */}

        <div className="veytra-panel veytra-panel-hover veytra-hud rounded-xl p-5">

          <div className="flex items-start justify-between">

            <div>
              <div className="text-[8px] uppercase tracking-[0.22em] text-slate-600">
                Vehicles Detected
              </div>

              <div className="mt-3 text-3xl font-semibold text-white">
                {String(totalVehicles).padStart(2, "0")}
              </div>
            </div>

            <div className="rounded-lg border border-teal-300/10 bg-teal-300/[0.04] px-2 py-1 text-[7px] uppercase tracking-widest text-teal-300/60">
              TRACKING
            </div>

          </div>

          <div className="mt-4 h-px bg-gradient-to-r from-teal-300/20 to-transparent" />

          <div className="mt-3 text-[8px] text-slate-600">
            Cross-camera vehicle activity
          </div>

        </div>


        {/* System */}

        <div className="veytra-panel veytra-panel-hover veytra-hud rounded-xl p-5">

          <div className="flex items-start justify-between">

            <div>
              <div className="text-[8px] uppercase tracking-[0.22em] text-slate-600">
                Intelligence Pipeline
              </div>

              <div className="mt-3 text-2xl font-semibold text-cyan-200">
                OPERATIONAL
              </div>
            </div>

            <div className="flex h-8 w-8 items-center justify-center rounded-lg border border-cyan-300/10 bg-cyan-300/[0.04]">
              <span className="veytra-live-dot" />
            </div>

          </div>

          <div className="mt-4 h-px bg-gradient-to-r from-cyan-300/20 to-transparent" />

          <div className="mt-3 text-[8px] text-slate-600">
            DETECT → READ → TRACK → VERIFY → ANALYZE
          </div>

        </div>

      </section>


      {/* =====================================================
          MAP
          ===================================================== */}

      <section className="relative mt-8">

        <div className="mb-3 flex items-end justify-between">

          <div>

            <div className="flex items-center gap-2">

              <span className="text-[8px] uppercase tracking-[0.25em] text-cyan-300/50">
                Network Visualization
              </span>

              <span className="h-px w-8 bg-cyan-300/20" />

            </div>

            <h2 className="mt-2 text-lg font-medium text-slate-200">
              Live Traffic Map
            </h2>

            <p className="mt-1 text-xs text-slate-600">
              Cross-camera vehicle activity and network overview.
            </p>

          </div>

          <div className="hidden items-center gap-4 text-[7px] uppercase tracking-[0.16em] text-slate-600 sm:flex">

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
            <MapView />
          </div>

        </div>

      </section>


      {/* =====================================================
          CAMERA NETWORK
          ===================================================== */}

      <section className="relative mt-8 pb-10">

        <div className="mb-4 flex items-end justify-between">

          <div>

            <div className="text-[8px] uppercase tracking-[0.25em] text-cyan-300/50">
              Infrastructure
            </div>

            <h2 className="mt-2 text-lg font-medium text-slate-200">
              Camera Network
            </h2>

          </div>

          <div className="text-[8px] uppercase tracking-[0.16em] text-slate-600">
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

                  <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-cyan-300/10 bg-cyan-300/[0.035] text-[11px] text-cyan-300/70">
                    ◉
                  </div>

                  <div>

                    <h3 className="text-sm font-semibold tracking-wide text-slate-200">
                      {camera.camera_id}
                    </h3>

                    <div className="mt-1 flex items-center gap-2">

                      <span
                        className={
                          camera.status === "Active"
                            ? "veytra-live-dot"
                            : "veytra-sim-dot"
                        }
                      />

                      <span className="text-[8px] uppercase tracking-[0.15em] text-slate-500">
                        {camera.status}
                      </span>

                    </div>

                  </div>

                </div>

                <SourceBadge source={camera.source} />

              </div>


              {/* Camera visual */}

              <div className="relative mt-4 h-28 overflow-hidden rounded-lg border border-white/[0.05] bg-[#02080c]">

                {/* Road */}
                <div className="absolute left-1/2 top-[-20%] h-[150%] w-[34%] -translate-x-1/2 rotate-[3deg] bg-slate-500/[0.07]" />

                {/* Road divider */}
                <div className="absolute left-1/2 top-0 h-full -translate-x-1/2 border-l border-dashed border-white/[0.08]" />

                {/* Vehicle marker */}
                <div className="absolute left-[42%] top-[42%] h-7 w-4 rounded-sm border border-cyan-300/25 bg-cyan-300/[0.06]">

                  <div className="absolute -left-px -top-px h-2 w-2 border-l border-t border-cyan-300/60" />
                  <div className="absolute -right-px -top-px h-2 w-2 border-r border-t border-cyan-300/60" />
                  <div className="absolute -bottom-px -left-px h-2 w-2 border-b border-l border-cyan-300/60" />
                  <div className="absolute -bottom-px -right-px h-2 w-2 border-b border-r border-cyan-300/60" />

                </div>

                {/* Scan lines */}
                <div className="absolute inset-0 bg-[linear-gradient(transparent_50%,rgba(34,211,238,0.025)_50%)] bg-[length:100%_4px]" />

                <div className="absolute left-3 top-3 text-[7px] uppercase tracking-[0.18em] text-cyan-300/40">
                  {camera.camera_id} // FEED
                </div>

                <div className="absolute bottom-3 right-3 text-[7px] uppercase tracking-[0.15em] text-slate-700">
                  ANPR • RE-ID
                </div>

              </div>


              {/* Stats */}

              <div className="mt-3 grid grid-cols-2 gap-2">

                <div className="rounded-lg border border-white/[0.05] bg-white/[0.015] p-3">

                  <div className="text-[7px] uppercase tracking-[0.16em] text-slate-600">
                    Vehicles
                  </div>

                  <div className="mt-1 text-lg font-semibold text-slate-200">
                    {camera.vehicles_detected}
                  </div>

                </div>


                <div className="rounded-lg border border-white/[0.05] bg-white/[0.015] p-3">

                  <div className="text-[7px] uppercase tracking-[0.16em] text-slate-600">
                    Source
                  </div>

                  <div className="mt-1 text-[10px] font-medium uppercase text-cyan-300/60">
                    {camera.source}
                  </div>

                </div>

              </div>


              {/* Button */}

              <button
                className="mt-3 w-full rounded-lg border border-white/[0.07] bg-white/[0.015] px-4 py-2.5 text-[8px] font-medium uppercase tracking-[0.18em] text-slate-500 transition hover:border-cyan-300/20 hover:bg-cyan-300/[0.035] hover:text-cyan-200"
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