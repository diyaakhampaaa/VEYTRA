import { useEffect, useState } from "react"
import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Polyline,
  Popup,
  useMap,
} from "react-leaflet"
import "leaflet/dist/leaflet.css"

// ============================================================
// VEYTRA — BENGALURU GIS DEMO NETWORK
// NOTE: Camera locations are simulated demo coordinates.
// ============================================================

const cameraLocations = [
  {
    id: "CAM_01",
    name: "Koramangala",
    position: [12.9352, 77.6245],
    road: "Hosur Road Corridor",
  },
  {
    id: "CAM_02",
    name: "Silk Board",
    position: [12.9173, 77.6229],
    road: "Silk Board Junction",
  },
  {
    id: "CAM_03",
    name: "HSR Layout",
    position: [12.9116, 77.6389],
    road: "27th Main Road",
  },
  {
    id: "CAM_04",
    name: "Indiranagar",
    position: [12.9784, 77.6408],
    road: "100 Feet Road",
  },
  {
    id: "CAM_05",
    name: "MG Road",
    position: [12.9756, 77.6065],
    road: "Mahatma Gandhi Road",
  },
]

// Simulated reconstructed vehicle trajectory
const trajectory = [
  [12.9173, 77.6229],
  [12.9215, 77.6235],
  [12.9280, 77.6240],
  [12.9352, 77.6245],
  [12.9440, 77.6270],
  [12.9550, 77.6310],
  [12.9660, 77.6360],
  [12.9784, 77.6408],
]

// ------------------------------------------------------------
// Animated vehicle marker
// ------------------------------------------------------------

function MovingVehicle({ position }) {
  return (
    <CircleMarker
      center={position}
      radius={8}
      pathOptions={{
        color: "#ffffff",
        fillColor: "#00e5ff",
        fillOpacity: 1,
        weight: 2,
      }}
    >
      <Popup>
        <div style={{ minWidth: "150px" }}>
          <strong>VEHICLE V18</strong>
          <br />
          Plate: KA01AB1234
          <br />
          Status: Tracking
        </div>
      </Popup>
    </CircleMarker>
  )
}

// ------------------------------------------------------------
// Camera marker
// ------------------------------------------------------------

function CameraMarker({
  camera,
  selected,
  onSelect,
}) {
  return (
    <CircleMarker
      center={camera.position}
      radius={selected ? 11 : 7}
      pathOptions={{
        color: selected ? "#ffffff" : "#ffffff",
        fillColor: selected ? "#ffffff" : "#00d9ff",
        fillOpacity: 0.95,
        weight: selected ? 3 : 2,
      }}
      eventHandlers={{
        click: () => onSelect?.(camera.id),
      }}
    >
      <Popup>
        <div style={{ minWidth: "180px" }}>
          <strong>{camera.id}</strong>
          <br />
          {camera.name}
          <br />
          Road: {camera.road}
          <br />
          Vehicles: {camera.vehicles}
          <br />
          Source: {camera.source}
          <br />
          <span style={{ color: "#16a34a" }}>
            ● {camera.status?.toUpperCase() || "ONLINE"}
          </span>
        </div>
      </Popup>
    </CircleMarker>
  )
}

// ------------------------------------------------------------
// Automatically fit map around the Bengaluru network
// ------------------------------------------------------------

function FitNetwork({ cameras }) {
  const map = useMap()

  useEffect(() => {
    const points = [
      ...cameras.map((camera) => camera.position),
      ...trajectory,
    ]

    if (points.length > 0) {
      map.fitBounds(points, {
        padding: [50, 50],
      })
    }
  }, [map, cameras])

  return null
}

// ------------------------------------------------------------
// Main GIS Map
// ------------------------------------------------------------

export default function GISMapView({
  cameras: backendCameras = [],
  selectedCameraId = null,
  onCameraSelect,
}) {
  const [vehicleIndex, setVehicleIndex] = useState(0)
  const [running, setRunning] = useState(true)

  // Combine backend camera data with simulated geographic positions
  const cameras = cameraLocations
    .filter((location) =>
      backendCameras.some(
        (camera) => camera.camera_id === location.id
      )
    )
    .map((location) => {
      const backendCamera = backendCameras.find(
        (camera) => camera.camera_id === location.id
      )

      return {
        ...location,
        vehicles: backendCamera?.vehicles_detected || 0,
        status: backendCamera?.status || "Active",
        source: backendCamera?.source || "simulated",
      }
    })

  // Animate vehicle along reconstructed trajectory
  useEffect(() => {
    if (!running) return

    const interval = setInterval(() => {
      setVehicleIndex((current) => {
        if (current >= trajectory.length - 1) {
          return 0
        }

        return current + 1
      })
    }, 900)

    return () => clearInterval(interval)
  }, [running])

  return (
    <div
      className="relative h-[520px] w-full overflow-hidden rounded-lg"
      style={{
        background: "#071018",
      }}
    >

      <MapContainer
        center={[12.9352, 77.6245]}
        zoom={12}
        style={{
          height: "100%",
          width: "100%",
        }}
        zoomControl={true}
      >

        {/* OpenStreetMap base layer */}

        <TileLayer
          attribution="&copy; OpenStreetMap contributors"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <FitNetwork cameras={cameras} />

        {/* Reconstructed vehicle trajectory */}

        <Polyline
          positions={trajectory}
          pathOptions={{
            color: "#00e5ff",
            weight: 5,
            opacity: 0.85,
          }}
        />

        {/* Camera network */}

        {cameras.map((camera) => (
          <CameraMarker
            key={camera.id}
            camera={camera}
            selected={selectedCameraId === camera.id}
            onSelect={onCameraSelect}
          />
        ))}

        {/* Moving vehicle */}

        <MovingVehicle
          position={trajectory[vehicleIndex]}
        />

      </MapContainer>

      {/* ======================================================
          TOP LEFT — MAP STATUS
          ====================================================== */}

      <div
        className="absolute left-4 top-4 z-[1000] rounded-lg border px-4 py-3"
        style={{
          background: "rgba(5, 15, 25, 0.90)",
          borderColor: "rgba(0, 229, 255, 0.35)",
          color: "white",
          backdropFilter: "blur(8px)",
        }}
      >

        <div
          className="text-xs font-semibold tracking-[0.18em]"
          style={{ color: "#00e5ff" }}
        >
          GIS TRAFFIC NETWORK
        </div>

        <div className="mt-1 text-lg font-semibold">
          BENGALURU
        </div>

        <div className="mt-1 flex items-center gap-2 text-[10px] tracking-wider text-slate-300">

          <span
            className="rounded px-2 py-1"
            style={{
              background: "rgba(245, 158, 11, 0.18)",
              color: "#fbbf24",
            }}
          >
            SIMULATED
          </span>

          <span>
            {String(cameras.length).padStart(2, "0")} CAMERA NODES
          </span>

        </div>

      </div>

      {/* ======================================================
          TOP RIGHT — PIPELINE STATUS
          ====================================================== */}

      <div
        className="absolute right-4 top-4 z-[1000] rounded-lg border px-4 py-3"
        style={{
          background: "rgba(5, 15, 25, 0.90)",
          borderColor: "rgba(0, 229, 255, 0.25)",
          color: "white",
          backdropFilter: "blur(8px)",
        }}
      >

        <div className="text-[10px] tracking-[0.15em] text-slate-400">
          INTELLIGENCE PIPELINE
        </div>

        <div className="mt-2 flex items-center gap-2">

          <span
            className="h-2 w-2 rounded-full"
            style={{
              background: "#22c55e",
              boxShadow: "0 0 8px #22c55e",
            }}
          />

          <span className="text-xs font-medium">
            ACTIVE
          </span>

        </div>

      </div>

      {/* ======================================================
          SELECTED CAMERA
          ====================================================== */}

      {selectedCameraId && (
        <div
          className="absolute left-4 top-1/2 z-[1000] -translate-y-1/2 rounded-lg border px-4 py-3"
          style={{
            background: "rgba(5, 15, 25, 0.94)",
            borderColor: "rgba(0, 229, 255, 0.35)",
            color: "white",
            backdropFilter: "blur(8px)",
          }}
        >

          {(() => {
            const selectedCamera = cameras.find(
              (camera) => camera.id === selectedCameraId
            )

            if (!selectedCamera) return null

            return (
              <>
                <div
                  className="text-[9px] tracking-[0.18em]"
                  style={{ color: "#00e5ff" }}
                >
                  CAMERA INTELLIGENCE
                </div>

                <div className="mt-2 text-sm font-semibold">
                  {selectedCamera.id}
                </div>

                <div className="mt-1 text-[10px] text-slate-400">
                  {selectedCamera.name}
                </div>

                <div className="mt-3 grid grid-cols-2 gap-2">

                  <div>
                    <div className="text-[8px] uppercase tracking-wider text-slate-600">
                      Vehicles
                    </div>

                    <div className="mt-1 text-sm font-semibold text-cyan-200">
                      {selectedCamera.vehicles}
                    </div>
                  </div>

                  <div>
                    <div className="text-[8px] uppercase tracking-wider text-slate-600">
                      Status
                    </div>

                    <div className="mt-1 text-[10px] font-semibold uppercase text-green-400">
                      {selectedCamera.status}
                    </div>
                  </div>

                </div>

                <div className="mt-3 text-[8px] uppercase tracking-wider text-slate-600">
                  {selectedCamera.road}
                </div>
              </>
            )
          })()}

        </div>
      )}

      {/* ======================================================
          BOTTOM LEFT — ACTIVE TRAJECTORY
          ====================================================== */}

      <div
        className="absolute bottom-4 left-4 z-[1000] rounded-lg border px-4 py-3"
        style={{
          background: "rgba(5, 15, 25, 0.92)",
          borderColor: "rgba(0, 229, 255, 0.30)",
          color: "white",
          backdropFilter: "blur(8px)",
        }}
      >

        <div
          className="text-[10px] tracking-[0.15em]"
          style={{ color: "#94a3b8" }}
        >
          ACTIVE TRAJECTORY
        </div>

        <div
          className="mt-1 text-sm font-semibold"
          style={{ color: "#00e5ff" }}
        >
          VEHICLE V18
        </div>

        <div className="mt-1 text-[11px] text-slate-300">
          SILK BOARD → KORAMANGALA → INDIRANAGAR
        </div>

      </div>

      {/* ======================================================
          BOTTOM RIGHT — SIMULATION CONTROL
          ====================================================== */}

      <button
        onClick={() => setRunning((value) => !value)}
        className="absolute bottom-4 right-4 z-[1000] rounded-lg border px-4 py-2 text-xs font-semibold tracking-wider transition"
        style={{
          background: running
            ? "rgba(15, 23, 42, 0.92)"
            : "rgba(0, 229, 255, 0.15)",
          borderColor: "rgba(0, 229, 255, 0.40)",
          color: "#00e5ff",
          backdropFilter: "blur(8px)",
        }}
      >
        {running ? "PAUSE SIMULATION" : "RESUME SIMULATION"}
      </button>

      {/* ======================================================
          DEMO DISCLAIMER
          ====================================================== */}

      <div
        className="absolute bottom-1 left-1/2 z-[1000] -translate-x-1/2 text-[9px] tracking-wider"
        style={{
          color: "rgba(255,255,255,0.55)",
        }}
      >
        SIMULATED CAMERA INFRASTRUCTURE • DEMONSTRATION NETWORK
      </div>

    </div>
  )
}