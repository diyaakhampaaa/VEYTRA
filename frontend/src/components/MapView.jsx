import { useEffect, useState } from "react"
import SourceBadge from "./SourceBadge"

function MapView() {
  const [selectedCamera, setSelectedCamera] = useState(null)
  const [selectedVehicle, setSelectedVehicle] = useState(null)
  const [simulationRunning, setSimulationRunning] = useState(true)
  const [tick, setTick] = useState(0)

  const cameras = [
    {
      id: "CAM_01",
      x: "20%",
      y: "65%",
      vehicles: 12,
      status: "ACTIVE",
      location: "NEHRU PLACE",
      road: "MAIN ROAD",
      coverage: "92%",
    },
    {
      id: "CAM_02",
      x: "50%",
      y: "35%",
      vehicles: 8,
      status: "ACTIVE",
      location: "RING ROAD",
      road: "RING ROAD",
      coverage: "87%",
    },
    {
      id: "CAM_03",
      x: "78%",
      y: "65%",
      vehicles: 15,
      status: "ACTIVE",
      location: "ITO",
      road: "ITO CORRIDOR",
      coverage: "95%",
    },
  ]

  const vehicles = [
    {
      id: "V1",
      x: "28%",
      y: "60%",
      speed: 34,
      direction: "EAST",
      type: "CAR",
    },
    {
      id: "V2",
      x: "38%",
      y: "48%",
      speed: 29,
      direction: "NORTH-EAST",
      type: "CAR",
    },
    {
      id: "V3",
      x: "52%",
      y: "40%",
      speed: 21,
      direction: "EAST",
      type: "SUV",
    },
    {
      id: "V4",
      x: "64%",
      y: "48%",
      speed: 18,
      direction: "EAST",
      type: "CAR",
    },
    {
      id: "V5",
      x: "72%",
      y: "59%",
      speed: 25,
      direction: "SOUTH-EAST",
      type: "SUV",
    },
  ]

  useEffect(() => {
    if (!simulationRunning) return

    const interval = setInterval(() => {
      setTick((value) => value + 1)
    }, 900)

    return () => clearInterval(interval)
  }, [simulationRunning])

  const selectCamera = (camera) => {
    setSelectedCamera(camera)
    setSelectedVehicle(null)
  }

  const selectVehicle = (vehicle) => {
    setSelectedVehicle(vehicle)
    setSelectedCamera(null)
  }

  const clearSelection = () => {
    setSelectedCamera(null)
    setSelectedVehicle(null)
  }

  return (
    <div className="relative h-full min-h-[520px] overflow-hidden rounded-lg border border-cyan-300/[0.08] bg-[#02070b]">

      {/* =====================================================
          MAP BACKGROUND
          ===================================================== */}

      <div className="absolute inset-0">

        <div className="absolute inset-0 bg-[#030b10]" />

        <div className="absolute inset-0 opacity-[0.13]">
          <div
            className="h-full w-full"
            style={{
              backgroundImage:
                "linear-gradient(to right, rgba(34,211,238,0.14) 1px, transparent 1px), linear-gradient(to bottom, rgba(34,211,238,0.14) 1px, transparent 1px)",
              backgroundSize: "55px 55px",
            }}
          />
        </div>

        {/* =================================================
            CITY BLOCKS
            ================================================= */}

        <div className="absolute left-[6%] top-[14%] h-24 w-32 border border-cyan-300/[0.05] bg-white/[0.012]" />

        <div className="absolute left-[10%] top-[29%] h-16 w-20 border border-cyan-300/[0.04] bg-white/[0.01]" />

        <div className="absolute left-[27%] top-[17%] h-20 w-28 border border-cyan-300/[0.035] bg-white/[0.008]" />

        <div className="absolute right-[7%] top-[16%] h-28 w-28 border border-cyan-300/[0.05] bg-white/[0.012]" />

        <div className="absolute right-[17%] top-[33%] h-20 w-24 border border-cyan-300/[0.04] bg-white/[0.01]" />

        <div className="absolute bottom-[10%] left-[7%] h-20 w-36 border border-cyan-300/[0.04] bg-white/[0.01]" />

        <div className="absolute bottom-[14%] right-[8%] h-24 w-32 border border-cyan-300/[0.04] bg-white/[0.01]" />

        {/* =================================================
            CITY ROAD NETWORK
            ================================================= */}

        <svg
          className="absolute inset-0 h-full w-full"
          viewBox="0 0 100 100"
          preserveAspectRatio="none"
        >

          {/* Main horizontal corridor */}

          <path
            d="M -5 59 C 20 58, 35 57, 50 58 C 68 59, 84 58, 105 57"
            fill="none"
            stroke="#09171e"
            strokeWidth="9"
          />

          <path
            d="M -5 59 C 20 58, 35 57, 50 58 C 68 59, 84 58, 105 57"
            fill="none"
            stroke="rgba(34,211,238,0.12)"
            strokeWidth="0.35"
            strokeDasharray="2 2"
          />

          {/* Central vertical corridor */}

          <path
            d="M 51 -5 C 50 18, 51 35, 50 58 C 49 75, 51 88, 50 105"
            fill="none"
            stroke="#09171e"
            strokeWidth="8"
          />

          <path
            d="M 51 -5 C 50 18, 51 35, 50 58 C 49 75, 51 88, 50 105"
            fill="none"
            stroke="rgba(34,211,238,0.11)"
            strokeWidth="0.3"
            strokeDasharray="2 2"
          />

          {/* North-west diagonal */}

          <path
            d="M 8 5 C 20 20, 31 34, 50 58"
            fill="none"
            stroke="#08151b"
            strokeWidth="7"
          />

          <path
            d="M 8 5 C 20 20, 31 34, 50 58"
            fill="none"
            stroke="rgba(34,211,238,0.08)"
            strokeWidth="0.3"
            strokeDasharray="2 2"
          />

          {/* South-east diagonal */}

          <path
            d="M 50 58 C 65 66, 79 82, 94 101"
            fill="none"
            stroke="#08151b"
            strokeWidth="7"
          />

          <path
            d="M 50 58 C 65 66, 79 82, 94 101"
            fill="none"
            stroke="rgba(34,211,238,0.08)"
            strokeWidth="0.3"
            strokeDasharray="2 2"
          />

          {/* North-east corridor */}

          <path
            d="M 92 4 C 78 20, 65 36, 50 58"
            fill="none"
            stroke="#071319"
            strokeWidth="6"
          />

          <path
            d="M 92 4 C 78 20, 65 36, 50 58"
            fill="none"
            stroke="rgba(255,255,255,0.05)"
            strokeWidth="0.25"
            strokeDasharray="2 2"
          />

        </svg>

        {/* =================================================
            ORIGINAL TRAFFIC MAP HEAT ZONES
            ================================================= */}

        <div className="absolute left-[14%] top-[52%] h-16 w-32 rounded-full bg-cyan-400/[0.05] blur-2xl" />

        <div className="absolute left-[40%] top-[52%] h-20 w-40 rounded-full bg-amber-300/[0.07] blur-2xl" />

        <div className="absolute right-[12%] top-[51%] h-20 w-32 rounded-full bg-orange-300/[0.06] blur-2xl" />

        <div className="absolute left-[47%] top-[25%] h-20 w-16 rounded-full bg-cyan-300/[0.035] blur-2xl" />

        {/* Center glow */}

        <div className="absolute left-1/2 top-1/2 h-72 w-72 -translate-x-1/2 -translate-y-1/2 rounded-full bg-cyan-400/[0.025] blur-3xl" />

        {/* Scanlines */}

        <div className="absolute inset-0 bg-[linear-gradient(transparent_50%,rgba(34,211,238,0.018)_50%)] bg-[length:100%_4px]" />

        {/* Vignette */}

        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_20%,rgba(0,0,0,0.72)_100%)]" />

      </div>

      {/* =====================================================
          TOP LEFT NETWORK STATUS
          ===================================================== */}

      <div className="absolute left-4 top-4 z-40">

        <div className="rounded-lg border border-cyan-300/[0.12] bg-[#02070b]/90 px-4 py-3 backdrop-blur-xl">

          <div className="flex items-center gap-2">

            <span className="veytra-live-dot" />

            <span className="text-[9px] font-semibold uppercase tracking-[0.2em] text-slate-200">
              Live Traffic Network
            </span>

          </div>

          <div className="mt-2 flex items-center gap-3">

            <SourceBadge source="simulated" />

            <span className="text-[8px] uppercase tracking-[0.15em] text-slate-600">
              03 CAMERA NODES
            </span>

          </div>

        </div>

      </div>

      {/* =====================================================
          TOP RIGHT COORDINATES
          ===================================================== */}

      <div className="absolute right-4 top-4 z-40 hidden sm:block">

        <div className="rounded-lg border border-white/[0.06] bg-[#02070b]/80 px-4 py-3 backdrop-blur-xl">

          <div className="text-[7px] uppercase tracking-[0.2em] text-slate-600">
            Network Coordinates
          </div>

          <div className="mt-1 font-mono text-[9px] text-cyan-300/60">
            28.6139° N
          </div>

          <div className="font-mono text-[9px] text-cyan-300/60">
            77.2090° E
          </div>

          <div className="mt-2 flex items-center gap-2">

            <span className="h-1.5 w-1.5 rounded-full bg-cyan-300 animate-pulse" />

            <span className="text-[7px] uppercase tracking-[0.15em] text-slate-600">
              NODE SYNC {tick.toString().padStart(3, "0")}
            </span>

          </div>

        </div>

      </div>

      {/* =====================================================
          CAMERA NODES
          ===================================================== */}

      {cameras.map((camera) => {

        const selected = selectedCamera?.id === camera.id

        return (
          <button
            key={camera.id}
            type="button"
            onClick={() => selectCamera(camera)}
            className="absolute z-30 -translate-x-1/2 -translate-y-1/2 outline-none"
            style={{
              left: camera.x,
              top: camera.y,
            }}
          >

            <div className="group relative">

              <div
                className={`absolute left-1/2 top-1/2 h-16 w-16 -translate-x-1/2 -translate-y-1/2 rounded-full border ${
                  selected
                    ? "border-cyan-300/40"
                    : "border-cyan-300/10"
                } ${simulationRunning ? "animate-ping" : ""}`}
              />

              {selected && (
                <div className="absolute left-1/2 top-1/2 h-14 w-14 -translate-x-1/2 -translate-y-1/2 rounded-full border border-cyan-300/30" />
              )}

              {/* Camera information */}

              <div
                className={`absolute bottom-[calc(100%+14px)] left-1/2 -translate-x-1/2 whitespace-nowrap rounded-md border bg-[#02070b]/95 px-3 py-2 backdrop-blur-xl transition ${
                  selected
                    ? "border-cyan-300/35 opacity-100"
                    : "border-cyan-300/[0.10] opacity-70 group-hover:border-cyan-300/30 group-hover:opacity-100"
                }`}
              >

                <div className="flex items-center gap-2">

                  <span className="text-[8px] font-semibold tracking-[0.15em] text-cyan-200">
                    {camera.id}
                  </span>

                  <span className="veytra-live-dot" />

                </div>

                <div className="mt-1 text-[7px] uppercase tracking-[0.14em] text-slate-600">
                  {camera.location}
                </div>

                <div className="mt-2 flex items-center justify-between gap-4">

                  <span className="text-[7px] uppercase tracking-[0.12em] text-slate-600">
                    Vehicles
                  </span>

                  <span className="text-[8px] font-semibold text-slate-300">
                    {camera.vehicles}
                  </span>

                </div>

              </div>

              <div className="absolute bottom-[calc(100%+5px)] left-1/2 h-3 w-px -translate-x-1/2 bg-cyan-300/20" />

              <div
                className={`relative flex h-10 w-10 items-center justify-center rounded-full border ${
                  selected
                    ? "border-cyan-200 bg-cyan-300/[0.12] shadow-[0_0_30px_rgba(34,211,238,0.35)]"
                    : "border-cyan-300/60 bg-[#02070b]/95 shadow-[0_0_18px_rgba(34,211,238,0.15)]"
                }`}
              >

                <span className="h-2.5 w-2.5 rounded-full bg-cyan-300 shadow-[0_0_10px_#22d3ee]" />

              </div>

            </div>

          </button>
        )
      })}

      {/* =====================================================
          VEHICLE TRAJECTORY
          ===================================================== */}

      <svg
        className="pointer-events-none absolute inset-0 z-10 h-full w-full"
        viewBox="0 0 100 100"
        preserveAspectRatio="none"
      >

        <path
          d="M 27 60 C 34 57, 35 50, 40 48 C 46 45, 48 42, 52 40 C 57 42, 61 46, 64 48 C 68 52, 70 57, 72 59"
          fill="none"
          stroke="rgba(34,211,238,0.10)"
          strokeWidth="1.1"
        />

        <path
          d="M 27 60 C 34 57, 35 50, 40 48 C 46 45, 48 42, 52 40 C 57 42, 61 46, 64 48 C 68 52, 70 57, 72 59"
          fill="none"
          stroke="rgba(34,211,238,0.55)"
          strokeWidth="0.3"
          strokeDasharray="2 2"
          style={{
            strokeDashoffset: simulationRunning ? tick * -3 : 0,
          }}
        />

      </svg>

      {/* =====================================================
          VEHICLES
          ===================================================== */}

      {vehicles.map((vehicle, index) => {

        const selected = selectedVehicle?.id === vehicle.id

        const movement = simulationRunning
          ? Math.sin((tick + index) * 0.7) * 0.35
          : 0

        return (
          <button
            key={vehicle.id}
            type="button"
            onClick={() => selectVehicle(vehicle)}
            className="absolute z-30 -translate-x-1/2 -translate-y-1/2 outline-none transition-all duration-700"
            style={{
              left: vehicle.x,
              top: `calc(${vehicle.y} + ${movement}px)`,
            }}
          >

            <div className="group relative">

              {selected && (
                <div className="absolute left-1/2 top-1/2 h-12 w-12 -translate-x-1/2 -translate-y-1/2 rounded-full border border-cyan-300/30 animate-ping" />
              )}

              <div
                className={`flex h-8 w-6 items-center justify-center border transition ${
                  selected
                    ? "border-cyan-200 bg-cyan-300/[0.12] shadow-[0_0_20px_rgba(34,211,238,0.25)]"
                    : "border-cyan-300/40 bg-cyan-300/[0.035] group-hover:border-cyan-200/80"
                }`}
              >

                <div className="h-1.5 w-1.5 rounded-full bg-cyan-300/80 shadow-[0_0_7px_#22d3ee]" />

              </div>

              <div className="absolute left-1/2 top-9 -translate-x-1/2 whitespace-nowrap rounded bg-[#02070b]/90 px-1.5 py-1 text-[6px] uppercase tracking-[0.12em] text-cyan-300/60">

                {vehicle.id} // TRACKED

              </div>

            </div>

          </button>
        )
      })}

      {/* =====================================================
          SELECTED INTELLIGENCE PANEL
          ===================================================== */}

      {(selectedCamera || selectedVehicle) && (

        <div className="absolute bottom-16 left-4 z-50 w-[230px] rounded-lg border border-cyan-300/[0.15] bg-[#02070b]/95 p-4 shadow-[0_0_35px_rgba(34,211,238,0.08)] backdrop-blur-xl">

          <div className="flex items-center justify-between">

            <div className="text-[7px] uppercase tracking-[0.22em] text-cyan-300/50">
              Intelligence Target
            </div>

            <button
              type="button"
              onClick={clearSelection}
              className="text-xs text-slate-600 transition hover:text-slate-300"
            >
              ×
            </button>

          </div>

          {/* Selected camera */}

          {selectedCamera && (
            <>

              <div className="mt-2 flex items-center gap-2">

                <span className="veytra-live-dot" />

                <span className="font-mono text-sm font-semibold text-cyan-100">
                  {selectedCamera.id}
                </span>

              </div>

              <div className="mt-1 text-[7px] uppercase tracking-[0.15em] text-slate-600">
                {selectedCamera.location}
              </div>

              <div className="mt-4 grid grid-cols-2 gap-2">

                <div className="rounded border border-white/[0.05] bg-white/[0.015] p-2">

                  <div className="text-[6px] uppercase tracking-[0.15em] text-slate-700">
                    Vehicles
                  </div>

                  <div className="mt-1 font-mono text-sm text-slate-300">
                    {selectedCamera.vehicles}
                  </div>

                </div>

                <div className="rounded border border-white/[0.05] bg-white/[0.015] p-2">

                  <div className="text-[6px] uppercase tracking-[0.15em] text-slate-700">
                    Coverage
                  </div>

                  <div className="mt-1 font-mono text-sm text-cyan-200">
                    {selectedCamera.coverage}
                  </div>

                </div>

              </div>

              <div className="mt-3 flex items-center justify-between">

                <span className="text-[7px] uppercase tracking-[0.14em] text-slate-700">
                  Status
                </span>

                <span className="text-[7px] uppercase tracking-[0.14em] text-cyan-300">
                  {selectedCamera.status}
                </span>

              </div>

            </>
          )}

          {/* Selected vehicle */}

          {selectedVehicle && (
            <>

              <div className="mt-2 flex items-center gap-2">

                <span className="h-2 w-2 rounded-full bg-cyan-300 shadow-[0_0_8px_#22d3ee]" />

                <span className="font-mono text-sm font-semibold text-cyan-100">
                  {selectedVehicle.id}
                </span>

              </div>

              <div className="mt-1 text-[7px] uppercase tracking-[0.15em] text-slate-600">
                Tracked Vehicle
              </div>

              <div className="mt-4 grid grid-cols-2 gap-2">

                <div className="rounded border border-white/[0.05] bg-white/[0.015] p-2">

                  <div className="text-[6px] uppercase tracking-[0.15em] text-slate-700">
                    Speed
                  </div>

                  <div className="mt-1 font-mono text-sm text-slate-300">
                    {selectedVehicle.speed}

                    <span className="ml-1 text-[7px] text-slate-600">
                      KM/H
                    </span>

                  </div>

                </div>

                <div className="rounded border border-white/[0.05] bg-white/[0.015] p-2">

                  <div className="text-[6px] uppercase tracking-[0.15em] text-slate-700">
                    Type
                  </div>

                  <div className="mt-1 font-mono text-sm text-cyan-200">
                    {selectedVehicle.type}
                  </div>

                </div>

              </div>

              <div className="mt-3 flex items-center justify-between">

                <span className="text-[7px] uppercase tracking-[0.14em] text-slate-700">
                  Direction
                </span>

                <span className="text-[7px] uppercase tracking-[0.14em] text-cyan-300">
                  {selectedVehicle.direction}
                </span>

              </div>

            </>
          )}

        </div>
      )}

      {/* =====================================================
          SIMULATION CONTROLS
          ===================================================== */}

      <div className="absolute bottom-4 left-1/2 z-40 -translate-x-1/2">

        <div className="flex items-center gap-3 rounded-lg border border-white/[0.07] bg-[#02070b]/90 px-4 py-2.5 backdrop-blur-xl">

          <button
            type="button"
            onClick={() => setSimulationRunning((value) => !value)}
            className="flex items-center gap-2 rounded border border-cyan-300/15 bg-cyan-300/[0.04] px-3 py-1.5 text-[7px] font-semibold uppercase tracking-[0.16em] text-cyan-200 transition hover:border-cyan-300/35 hover:bg-cyan-300/[0.08]"
          >

            <span>
              {simulationRunning ? "Ⅱ" : "▶"}
            </span>

            {simulationRunning ? "Pause" : "Resume"}

          </button>

          <div className="h-4 w-px bg-white/[0.08]" />

          <div className="text-[7px] uppercase tracking-[0.16em] text-slate-600">
            Simulation
          </div>

          <div className="font-mono text-[8px] text-cyan-300/60">
            T+{tick}s
          </div>

        </div>

      </div>

      {/* =====================================================
          BOTTOM LEFT STATUS
          ===================================================== */}

      <div className="absolute bottom-4 left-4 z-20 hidden sm:block">

        <div className="flex items-center gap-4 rounded-lg border border-white/[0.05] bg-[#02070b]/80 px-4 py-2.5 backdrop-blur-xl">

          <div className="flex items-center gap-2">

            <span
              className={`h-1.5 w-1.5 rounded-full ${
                simulationRunning
                  ? "bg-cyan-300 shadow-[0_0_8px_#22d3ee]"
                  : "bg-slate-600"
              }`}
            />

            <span className="text-[7px] uppercase tracking-[0.16em] text-slate-500">
              {simulationRunning
                ? "Network Active"
                : "Network Paused"}
            </span>

          </div>

          <div className="h-3 w-px bg-white/[0.08]" />

          <span className="text-[7px] uppercase tracking-[0.16em] text-cyan-300/50">
            5 tracked vehicles
          </span>

        </div>

      </div>

      {/* =====================================================
          LEGEND
          ===================================================== */}

      <div className="absolute bottom-4 right-4 z-20">

        <div className="rounded-lg border border-white/[0.06] bg-[#02070b]/85 p-3 backdrop-blur-xl">

          <div className="mb-2 text-[7px] font-semibold uppercase tracking-[0.2em] text-slate-600">
            Network Legend
          </div>

          <div className="space-y-2">

            <div className="flex items-center gap-2">

              <span className="h-2 w-2 rounded-full bg-cyan-300 shadow-[0_0_7px_#22d3ee]" />

              <span className="text-[7px] uppercase tracking-[0.12em] text-slate-500">
                Camera Node
              </span>

            </div>

            <div className="flex items-center gap-2">

              <span className="h-2 w-2 border border-cyan-300/50 bg-cyan-300/[0.08]" />

              <span className="text-[7px] uppercase tracking-[0.12em] text-slate-500">
                Vehicle Track
              </span>

            </div>

            <div className="flex items-center gap-2">

              <span className="h-2 w-5 rounded-full bg-amber-300/20 blur-[2px]" />

              <span className="text-[7px] uppercase tracking-[0.12em] text-slate-500">
                Traffic Density
              </span>

            </div>

          </div>

        </div>

      </div>

      {/* =====================================================
          HUD CORNERS
          ===================================================== */}

      <div className="pointer-events-none absolute left-3 top-3 h-8 w-8 border-l border-t border-cyan-300/20" />

      <div className="pointer-events-none absolute right-3 top-3 h-8 w-8 border-r border-t border-cyan-300/20" />

      <div className="pointer-events-none absolute bottom-3 left-3 h-8 w-8 border-b border-l border-cyan-300/20" />

      <div className="pointer-events-none absolute bottom-3 right-3 h-8 w-8 border-b border-r border-cyan-300/20" />

    </div>
  )
}

export default MapView