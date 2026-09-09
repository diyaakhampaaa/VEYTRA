import { useEffect, useState } from "react"
import SourceBadge from "./SourceBadge"
import { getCameras } from "../api/client"

function MapView() {
  const [cameras, setCameras] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedCamera, setSelectedCamera] = useState(null)

  useEffect(() => {
    getCameras()
      .then((data) => {
        setCameras(data.cameras || [])
      })
      .catch((error) => {
        console.error("Map camera fetch error:", error)
      })
      .finally(() => {
        setLoading(false)
      })
  }, [])

  /*
   * Convert geographic coordinates into positions
   * inside our simulated map.
   */
  const camerasWithPositions = (() => {
    const camerasWithLocation = cameras.filter(
      (camera) => camera.location
    )

    if (camerasWithLocation.length === 0) {
      return []
    }

    const longitudes = camerasWithLocation.map(
      (camera) => camera.location.longitude
    )

    const latitudes = camerasWithLocation.map(
      (camera) => camera.location.latitude
    )

    const minLongitude = Math.min(...longitudes)
    const maxLongitude = Math.max(...longitudes)

    const minLatitude = Math.min(...latitudes)
    const maxLatitude = Math.max(...latitudes)

    const longitudeRange = maxLongitude - minLongitude || 1
    const latitudeRange = maxLatitude - minLatitude || 1

    return camerasWithLocation.map((camera) => {
      const x =
        15 +
        ((camera.location.longitude - minLongitude) /
          longitudeRange) *
          70

      const y =
        75 -
        ((camera.location.latitude - minLatitude) /
          latitudeRange) *
          50

      return {
        ...camera,
        x: `${x}%`,
        y: `${y}%`,
      }
    })
  })()

  /*
   * These vehicles are still simulated visual markers.
   * They will later be replaced with actual tracking data
   * from Member 3.
   */
  const vehicles = [
    { id: "V1", x: "28%", y: "60%" },
    { id: "V2", x: "38%", y: "48%" },
    { id: "V3", x: "52%", y: "40%" },
    { id: "V4", x: "64%", y: "48%" },
    { id: "V5", x: "72%", y: "59%" },
  ]

  return (
    <div className="relative h-[500px] overflow-hidden rounded-xl border border-slate-800 bg-slate-900">

      {/* Map Background */}

      <div className="absolute inset-0 bg-slate-950">

        {/* Horizontal Road */}

        <div className="absolute left-0 right-0 top-[58%] h-16 -translate-y-1/2 bg-slate-800">
          <div className="absolute left-0 right-0 top-1/2 border-t-2 border-dashed border-slate-600" />
        </div>

        {/* Diagonal Road */}

        <div className="absolute left-[20%] top-[15%] h-[420px] w-16 rotate-[45deg] bg-slate-800">
          <div className="absolute left-1/2 top-0 h-full border-l-2 border-dashed border-slate-600" />
        </div>

        {/* Vertical Road */}

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

      {/* Map Header */}

      <div className="absolute left-5 top-5 z-10">
        <div className="rounded-lg border border-slate-700 bg-slate-950/90 px-4 py-3 backdrop-blur">

          <p className="text-sm font-semibold">
            Live Traffic Network
          </p>

          <div className="mt-2 flex items-center gap-3">
            <SourceBadge source="simulated" />

            <span className="text-xs text-slate-500">
              {loading
                ? "Loading..."
                : `${cameras.length} cameras`}
            </span>
          </div>

        </div>
      </div>

      {/* Camera Markers */}

      {!loading &&
        camerasWithPositions.map((camera) => {
          const isSelected =
            selectedCamera?.camera_id === camera.camera_id

          return (
            <button
              key={camera.camera_id}
              onClick={() => setSelectedCamera(camera)}
              className="absolute z-20 -translate-x-1/2 -translate-y-1/2"
              style={{
                left: camera.x,
                top: camera.y,
              }}
            >
              <div className="relative">

                {/* Camera Marker */}

                <div
                  className={`flex h-10 w-10 items-center justify-center rounded-full border-2 bg-slate-950 shadow-lg transition ${
                    isSelected
                      ? "scale-110 border-blue-400 shadow-blue-400/30"
                      : "border-green-400 shadow-green-400/20"
                  }`}
                >
                  <span
                    className={`h-3 w-3 rounded-full ${
                      isSelected
                        ? "bg-blue-400"
                        : "bg-green-400"
                    }`}
                  />
                </div>

                {/* Camera Label */}

                <div className="absolute left-1/2 top-12 -translate-x-1/2 whitespace-nowrap rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-xs shadow-lg">

                  <p className="font-semibold">
                    {camera.camera_id}
                  </p>

                  <p className="mt-1 text-slate-500">
                    {camera.vehicles_detected} vehicles
                  </p>

                </div>

              </div>
            </button>
          )
        })}

      {/* Detected Vehicles */}

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

      {/* Selected Camera Panel */}

      {selectedCamera && (
        <div className="absolute right-5 top-5 z-40 w-64 rounded-xl border border-slate-700 bg-slate-950/95 p-5 shadow-2xl backdrop-blur">

          <div className="flex items-start justify-between">

            <div>
              <p className="text-xs uppercase tracking-wider text-slate-500">
                Camera
              </p>

              <h3 className="mt-1 text-xl font-semibold">
                {selectedCamera.camera_id}
              </h3>
            </div>

            <button
              onClick={() => setSelectedCamera(null)}
              className="text-slate-500 transition hover:text-white"
            >
              ✕
            </button>

          </div>

          <div className="mt-5 space-y-4">

            {/* Status */}

            <div>
              <p className="text-xs text-slate-500">
                Status
              </p>

              <p className="mt-1 text-sm text-green-400">
                ● {selectedCamera.status}
              </p>
            </div>

            {/* Vehicles */}

            <div>
              <p className="text-xs text-slate-500">
                Vehicles Detected
              </p>

              <p className="mt-1 text-2xl font-semibold">
                {selectedCamera.vehicles_detected}
              </p>
            </div>

            {/* Coordinates */}

            {selectedCamera.location && (
              <div>
                <p className="text-xs text-slate-500">
                  Coordinates
                </p>

                <p className="mt-1 text-sm text-slate-300">
                  {selectedCamera.location.latitude.toFixed(4)},{" "}
                  {selectedCamera.location.longitude.toFixed(4)}
                </p>
              </div>
            )}

            {/* Source */}

            <div>
              <p className="mb-2 text-xs text-slate-500">
                Data Source
              </p>

              <SourceBadge source={selectedCamera.source} />
            </div>

          </div>

        </div>
      )}

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