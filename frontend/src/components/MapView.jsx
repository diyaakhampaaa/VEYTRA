import SourceBadge from "./SourceBadge"

function MapView() {
  const cameras = [
    {
      id: "CAM_01",
      x: "20%",
      y: "65%",
      vehicles: 12,
      status: "Active",
    },
    {
      id: "CAM_02",
      x: "50%",
      y: "35%",
      vehicles: 8,
      status: "Active",
    },
    {
      id: "CAM_03",
      x: "78%",
      y: "65%",
      vehicles: 15,
      status: "Active",
    },
  ]

  const vehicles = [
    {
      id: "V1",
      x: "28%",
      y: "60%",
    },
    {
      id: "V2",
      x: "38%",
      y: "48%",
    },
    {
      id: "V3",
      x: "52%",
      y: "40%",
    },
    {
      id: "V4",
      x: "64%",
      y: "48%",
    },
    {
      id: "V5",
      x: "72%",
      y: "59%",
    },
  ]

  return (
    <div className="relative h-[500px] overflow-hidden rounded-xl border border-slate-800 bg-slate-900">

      {/* Map background */}

      <div className="absolute inset-0 bg-slate-950">

        {/* Horizontal road */}

        <div className="absolute left-0 right-0 top-[58%] h-16 -translate-y-1/2 bg-slate-800">
          <div className="absolute left-0 right-0 top-1/2 border-t-2 border-dashed border-slate-600" />
        </div>

        {/* Diagonal road */}

        <div
          className="absolute left-[20%] top-[15%] h-[420px] w-16 rotate-[45deg] bg-slate-800"
        >
          <div className="absolute left-1/2 top-0 h-full border-l-2 border-dashed border-slate-600" />
        </div>

        {/* Vertical road */}

        <div className="absolute bottom-0 left-1/2 top-0 w-14 -translate-x-1/2 bg-slate-800">
          <div className="absolute bottom-0 left-1/2 top-0 border-l-2 border-dashed border-slate-600" />
        </div>

        {/* Grid */}

        <div className="absolute inset-0 opacity-20">
          <div
            className="h-full w-full"
            style={{
              backgroundImage:
                "linear-gradient(to right, #475569 1px, transparent 1px), linear-gradient(to bottom, #475569 1px, transparent 1px)",
              backgroundSize: "50px 50px",
            }}
          />
        </div>
      </div>

      {/* Header */}

      <div className="absolute left-5 top-5 z-10">
        <div className="rounded-lg border border-slate-700 bg-slate-950/90 px-4 py-3 backdrop-blur">

          <p className="text-sm font-semibold">
            Live Traffic Network
          </p>

          <div className="mt-2 flex items-center gap-3">
            <SourceBadge source="simulated" />

            <span className="text-xs text-slate-500">
              3 cameras
            </span>
          </div>

        </div>
      </div>

      {/* Camera markers */}

      {cameras.map((camera) => (
        <div
          key={camera.id}
          className="absolute z-20 -translate-x-1/2 -translate-y-1/2"
          style={{
            left: camera.x,
            top: camera.y,
          }}
        >
          <div className="relative">

            <div className="flex h-10 w-10 items-center justify-center rounded-full border-2 border-green-400 bg-slate-950 shadow-lg shadow-green-400/20">
              <span className="h-3 w-3 rounded-full bg-green-400" />
            </div>

            <div className="absolute left-1/2 top-12 -translate-x-1/2 whitespace-nowrap rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-xs shadow-lg">

              <p className="font-semibold">
                {camera.id}
              </p>

              <p className="mt-1 text-slate-500">
                {camera.vehicles} vehicles
              </p>

            </div>

          </div>
        </div>
      ))}

      {/* Vehicle markers */}

      {vehicles.map((vehicle) => (
        <div
          key={vehicle.id}
          className="absolute z-30 -translate-x-1/2 -translate-y-1/2"
          style={{
            left: vehicle.x,
            top: vehicle.y,
          }}
        >
          <div className="flex h-7 w-7 items-center justify-center rounded-full bg-white text-xs font-bold text-slate-950 shadow-lg">
            🚗
          </div>
        </div>
      ))}

      {/* Legend */}

      <div className="absolute bottom-5 right-5 z-10 rounded-lg border border-slate-700 bg-slate-950/90 p-4 backdrop-blur">

        <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-500">
          Legend
        </p>

        <div className="space-y-2">

          <div className="flex items-center gap-2">
            <span className="h-3 w-3 rounded-full bg-green-400" />
            <span className="text-xs text-slate-400">
              Camera
            </span>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs">
              🚗
            </span>
            <span className="text-xs text-slate-400">
              Detected Vehicle
            </span>
          </div>

        </div>
      </div>

    </div>
  )
}

export default MapView