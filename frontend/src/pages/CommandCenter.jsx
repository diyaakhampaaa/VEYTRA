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

  return (
    <div>
      {/* Header */}

      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold">
            Command Center
          </h2>

          <p className="mt-2 text-slate-400">
            Monitor cameras and live traffic activity.
          </p>
        </div>

        <div className="flex items-center gap-4">
          <div className="text-sm">
            Backend:{" "}
            <span
              className={
                backendStatus === "Connected"
                  ? "text-green-400"
                  : "text-yellow-400"
              }
            >
              {backendStatus}
            </span>
          </div>

          <SourceBadge source="simulated" />
        </div>
      </div>

      {/* Summary Cards */}

      <div className="mt-8 grid grid-cols-1 gap-4 md:grid-cols-3">
        <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
          <p className="text-sm text-slate-400">
            Active Cameras
          </p>

          <p className="mt-2 text-3xl font-semibold">
            {activeCameras}
          </p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
          <p className="text-sm text-slate-400">
            Vehicles Detected
          </p>

          <p className="mt-2 text-3xl font-semibold">
            {totalVehicles}
          </p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
          <p className="text-sm text-slate-400">
            System Status
          </p>

          <p className="mt-2 text-3xl font-semibold text-green-400">
            Operational
          </p>
        </div>
      </div>

      {/* Live Traffic Map */}

      <div className="mt-8">
        <div className="mb-4">
          <h3 className="text-lg font-medium">
            Live Traffic Map
          </h3>

          <p className="mt-1 text-sm text-slate-500">
            Cross-camera vehicle activity and network overview.
          </p>
        </div>

        <MapView />
      </div>

      {/* Camera Network */}

      <div className="mt-8">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-lg font-medium">
            Camera Network
          </h3>

          <span className="text-sm text-slate-500">
            {cameras.length} cameras connected
          </span>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {cameras.map((camera) => (
            <div
              key={camera.camera_id}
              className="rounded-xl border border-slate-800 bg-slate-900 p-5"
            >
              {/* Camera Header */}

              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-xl font-semibold">
                    {camera.camera_id}
                  </h4>

                  <p className="mt-1 text-sm text-green-400">
                    ● {camera.status}
                  </p>
                </div>

                <SourceBadge source={camera.source} />
              </div>

              {/* Camera Stats */}

              <div className="mt-5 rounded-lg bg-slate-800 p-4">
                <p className="text-sm text-slate-400">
                  Vehicles Detected
                </p>

                <p className="mt-1 text-2xl font-semibold">
                  {camera.vehicles_detected}
                </p>
              </div>

              {/* View Button */}

              <button
                className="mt-4 w-full rounded-lg border border-slate-700 px-4 py-2 text-sm font-medium transition hover:bg-slate-800"
              >
                View Camera
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default CommandCenter