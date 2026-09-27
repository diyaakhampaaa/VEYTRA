import { useEffect, useMemo, useState } from "react"
import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Polyline,
  Popup,
  useMap,
} from "react-leaflet"
import "leaflet/dist/leaflet.css"

const DEMO_ROUTES = [
  {
    id: "R01",
    name: "Ring Road Northbound",
    color: "#00ffff",
    positions: [
      [28.5350, 77.2500],
      [28.5480, 77.2450],
      [28.5620, 77.2400],
      [28.5780, 77.2350],
      [28.5940, 77.2320],
      [28.6100, 77.2300],
      [28.6280, 77.2300],
      [28.6460, 77.2290],
      [28.6620, 77.2290],
      [28.6740, 77.2290],
    ],
  },

  {
    id: "R02",
    name: "Ring Road Southbound",
    color: "#ff00ff",
    positions: [
      [28.6740, 77.2290],
      [28.6600, 77.2290],
      [28.6440, 77.2300],
      [28.6250, 77.2310],
      [28.6060, 77.2330],
      [28.5880, 77.2360],
      [28.5700, 77.2410],
      [28.5530, 77.2470],
      [28.5370, 77.2540],
    ],
  },

  {
    id: "R03",
    name: "ITO → Kashmere Gate",
    color: "#39ff14",
    positions: [
      [28.6280, 77.2400],
      [28.6350, 77.2370],
      [28.6430, 77.2340],
      [28.6510, 77.2320],
      [28.6590, 77.2310],
      [28.6670, 77.2300],
      [28.6740, 77.2290],
    ],
  },

  {
    id: "R04",
    name: "Kashmere Gate → Central Delhi",
    color: "#ffb000",
    positions: [
      [28.6740, 77.2290],
      [28.6680, 77.2240],
      [28.6600, 77.2190],
      [28.6510, 77.2150],
      [28.6410, 77.2110],
      [28.6310, 77.2080],
      [28.6210, 77.2070],
      [28.6110, 77.2090],
    ],
  },

  {
    id: "R05",
    name: "Raj Ghat → ITO → East Delhi",
    color: "#ff3030",
    positions: [
      [28.6400, 77.2470],
      [28.6350, 77.2430],
      [28.6310, 77.2390],
      [28.6280, 77.2350],
      [28.6260, 77.2300],
      [28.6250, 77.2240],
      [28.6250, 77.2180],
      [28.6270, 77.2110],
      [28.6320, 77.2050],
    ],
  },

  {
    id: "R06",
    name: "North Delhi Corridor",
    color: "#ff1493",
    positions: [
      [28.7180, 77.2080],
      [28.7090, 77.2140],
      [28.7000, 77.2190],
      [28.6910, 77.2230],
      [28.6830, 77.2260],
      [28.6740, 77.2290],
      [28.6660, 77.2320],
    ],
  },

  {
    id: "R07",
    name: "Central → South Delhi",
    color: "#9d00ff",
    positions: [
      [28.6110, 77.2090],
      [28.6020, 77.2080],
      [28.5920, 77.2090],
      [28.5810, 77.2110],
      [28.5700, 77.2140],
      [28.5580, 77.2170],
      [28.5460, 77.2200],
      [28.5330, 77.2240],
    ],
  },

  {
    id: "R08",
    name: "Kashmere Gate → Red Fort",
    color: "#00ff99",
    positions: [
      [28.6740, 77.2290],
      [28.6690, 77.2350],
      [28.6630, 77.2400],
      [28.6570, 77.2420],
      [28.6510, 77.2410],
      [28.6460, 77.2390],
    ],
  },

  {
    id: "R09",
    name: "Red Fort → Delhi Gate",
    color: "#ffff00",
    positions: [
      [28.6460, 77.2390],
      [28.6400, 77.2380],
      [28.6340, 77.2370],
      [28.6280, 77.2350],
      [28.6210, 77.2330],
      [28.6150, 77.2310],
    ],
  },

  {
    id: "R10",
    name: "Lothian Road Corridor",
    color: "#00bfff",
    positions: [
      [28.6740, 77.2290],
      [28.6710, 77.2240],
      [28.6680, 77.2190],
      [28.6640, 77.2140],
      [28.6600, 77.2100],
      [28.6550, 77.2070],
    ],
  },

  {
    id: "R11",
    name: "East-West Central Corridor",
    color: "#ff6600",
    positions: [
      [28.6250, 77.2180],
      [28.6250, 77.2240],
      [28.6260, 77.2300],
      [28.6280, 77.2360],
      [28.6310, 77.2420],
      [28.6350, 77.2480],
    ],
  },

  {
    id: "R12",
    name: "North Ring Connector",
    color: "#7fff00",
    positions: [
      [28.7180, 77.2080],
      [28.7100, 77.2150],
      [28.7020, 77.2210],
      [28.6940, 77.2260],
      [28.6860, 77.2290],
      [28.6780, 77.2310],
    ],
  },

  {
    id: "R13",
    name: "Central Delhi Eastbound",
    color: "#ff00aa",
    positions: [
      [28.6110, 77.2090],
      [28.6160, 77.2160],
      [28.6200, 77.2230],
      [28.6240, 77.2300],
      [28.6280, 77.2370],
      [28.6320, 77.2440],
      [28.6360, 77.2510],
    ],
  },

  {
    id: "R14",
    name: "South Ring Connector",
    color: "#00ffea",
    positions: [
      [28.5330, 77.2240],
      [28.5440, 77.2230],
      [28.5550, 77.2200],
      [28.5660, 77.2170],
      [28.5780, 77.2140],
      [28.5900, 77.2110],
    ],
  },

  {
    id: "R15",
    name: "Ring Road Inner Lane",
    color: "#ff3366",
    positions: [
      [28.5450, 77.2580],
      [28.5580, 77.2520],
      [28.5730, 77.2470],
      [28.5880, 77.2430],
      [28.6030, 77.2400],
      [28.6190, 77.2380],
      [28.6350, 77.2370],
      [28.6510, 77.2360],
      [28.6680, 77.2350],
    ],
  },

  {
    id: "R16",
    name: "Ring Road Inner Southbound",
    color: "#8a2be2",
    positions: [
      [28.6680, 77.2350],
      [28.6510, 77.2360],
      [28.6350, 77.2370],
      [28.6190, 77.2380],
      [28.6030, 77.2400],
      [28.5880, 77.2430],
      [28.5730, 77.2470],
      [28.5580, 77.2520],
      [28.5450, 77.2580],
    ],
  },

  {
    id: "R17",
    name: "Kashmere Gate → Majnu Ka Tila",
    color: "#00ff44",
    positions: [
      [28.6740, 77.2290],
      [28.6800, 77.2240],
      [28.6870, 77.2200],
      [28.6950, 77.2160],
      [28.7030, 77.2120],
      [28.7110, 77.2080],
      [28.7200, 77.2040],
    ],
  },

  {
    id: "R18",
    name: "Majnu Ka Tila → Kashmere Gate",
    color: "#ff8800",
    positions: [
      [28.7200, 77.2040],
      [28.7110, 77.2080],
      [28.7030, 77.2120],
      [28.6950, 77.2160],
      [28.6870, 77.2200],
      [28.6800, 77.2240],
      [28.6740, 77.2290],
    ],
  },

  {
    id: "R19",
    name: "Civil Lines → Central Delhi",
    color: "#00d9ff",
    positions: [
      [28.7040, 77.2250],
      [28.6960, 77.2240],
      [28.6880, 77.2230],
      [28.6800, 77.2210],
      [28.6710, 77.2180],
      [28.6620, 77.2150],
      [28.6530, 77.2120],
      [28.6440, 77.2100],
      [28.6350, 77.2080],
    ],
  },

  {
    id: "R20",
    name: "Central Delhi → Civil Lines",
    color: "#ff1493",
    positions: [
      [28.6350, 77.2080],
      [28.6440, 77.2100],
      [28.6530, 77.2120],
      [28.6620, 77.2150],
      [28.6710, 77.2180],
      [28.6800, 77.2210],
      [28.6880, 77.2230],
      [28.6960, 77.2240],
      [28.7040, 77.2250],
    ],
  },

  {
    id: "R21",
    name: "ITO → Raj Ghat",
    color: "#ffea00",
    positions: [
      [28.6280, 77.2400],
      [28.6320, 77.2450],
      [28.6360, 77.2500],
      [28.6400, 77.2550],
      [28.6440, 77.2600],
    ],
  },

  {
    id: "R22",
    name: "Raj Ghat → ITO",
    color: "#00ffcc",
    positions: [
      [28.6440, 77.2600],
      [28.6400, 77.2550],
      [28.6360, 77.2500],
      [28.6320, 77.2450],
      [28.6280, 77.2400],
    ],
  },

  {
    id: "R23",
    name: "Delhi Gate → ITO",
    color: "#ff0055",
    positions: [
      [28.6350, 77.2370],
      [28.6320, 77.2400],
      [28.6290, 77.2430],
      [28.6260, 77.2460],
      [28.6230, 77.2490],
      [28.6200, 77.2520],
    ],
  },

  {
    id: "R24",
    name: "ITO → Delhi Gate",
    color: "#6600ff",
    positions: [
      [28.6200, 77.2520],
      [28.6230, 77.2490],
      [28.6260, 77.2460],
      [28.6290, 77.2430],
      [28.6320, 77.2400],
      [28.6350, 77.2370],
    ],
  },

  {
    id: "R25",
    name: "Kashmere Gate → Yamuna Link",
    color: "#00ff80",
    positions: [
      [28.6740, 77.2290],
      [28.6720, 77.2360],
      [28.6700, 77.2430],
      [28.6670, 77.2500],
      [28.6630, 77.2570],
      [28.6580, 77.2640],
    ],
  },

  {
    id: "R26",
    name: "Yamuna Link → Kashmere Gate",
    color: "#ff4500",
    positions: [
      [28.6580, 77.2640],
      [28.6630, 77.2570],
      [28.6670, 77.2500],
      [28.6700, 77.2430],
      [28.6720, 77.2360],
      [28.6740, 77.2290],
    ],
  },

  {
    id: "R27",
    name: "North-South Central",
    color: "#bf00ff",
    positions: [
      [28.7100, 77.2400],
      [28.7000, 77.2390],
      [28.6900, 77.2380],
      [28.6800, 77.2370],
      [28.6700, 77.2360],
      [28.6600, 77.2350],
      [28.6500, 77.2340],
      [28.6400, 77.2330],
      [28.6300, 77.2320],
      [28.6200, 77.2310],
      [28.6100, 77.2300],
    ],
  },

  {
    id: "R28",
    name: "South-North Central",
    color: "#00ffff",
    positions: [
      [28.6100, 77.2300],
      [28.6200, 77.2310],
      [28.6300, 77.2320],
      [28.6400, 77.2330],
      [28.6500, 77.2340],
      [28.6600, 77.2350],
      [28.6700, 77.2360],
      [28.6800, 77.2370],
      [28.6900, 77.2380],
      [28.7000, 77.2390],
      [28.7100, 77.2400],
    ],
  },

  {
    id: "R29",
    name: "Central East Connector",
    color: "#ff0099",
    positions: [
      [28.6500, 77.2100],
      [28.6480, 77.2170],
      [28.6460, 77.2240],
      [28.6440, 77.2310],
      [28.6420, 77.2380],
      [28.6400, 77.2450],
      [28.6380, 77.2520],
    ],
  },

  {
    id: "R30",
    name: "Central West Connector",
    color: "#80ff00",
    positions: [
      [28.6380, 77.2020],
      [28.6400, 77.2090],
      [28.6420, 77.2160],
      [28.6440, 77.2230],
      [28.6460, 77.2300],
      [28.6480, 77.2370],
      [28.6500, 77.2440],
    ],
  },
]

function FitNetwork({ cameras, routes }) {
  const map = useMap()

  useEffect(() => {
    const points = [
      ...cameras.map((camera) => camera.position),
      ...routes.flatMap((route) => route.positions),
    ]

    if (points.length > 0) {
      map.fitBounds(points, {
        padding: [40, 40],
      })
    }
  }, [map, cameras, routes])

  return null
}

function CameraMarker({ camera, selected, onSelect }) {
  return (
    <CircleMarker
      center={camera.position}
      radius={selected ? 10 : 7}
      pathOptions={{
        color: "#ffffff",
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
          Status: {camera.status || "Unknown"}
          <br />
          Vehicles: {camera.vehicles}
          <br />
          Source: {camera.source || "Unknown"}
          <br />
          Location:{" "}
          {camera.position
            ? `${camera.position[0].toFixed(5)}, ${camera.position[1].toFixed(5)}`
            : "Unavailable"}
        </div>
      </Popup>
    </CircleMarker>
  )
}

function RoutePopup({ route }) {
  return (
    <Popup>
      <div style={{ minWidth: "170px" }}>
        <strong>{route.name}</strong>
        <br />
        Demo traffic route
        <br />
        <span style={{ color: route.color }}>
          ● Background traffic
        </span>
      </div>
    </Popup>
  )
}

export default function GISMapView({
  cameras: backendCameras = [],
  selectedCameraId = null,
  onCameraSelect,
}) {
  const [running, setRunning] = useState(true)

  const cameras = useMemo(() => {
    return backendCameras
      .map((camera) => {
        const latitude = Number(camera?.location?.latitude)
        const longitude = Number(camera?.location?.longitude)

        if (
          !Number.isFinite(latitude) ||
          !Number.isFinite(longitude)
        ) {
          return null
        }

        return {
          id: camera.camera_id,
          position: [latitude, longitude],
          vehicles: Number(camera.vehicles_detected || 0),
          status: camera.status || "Unknown",
          source: camera.source || "Unknown",
        }
      })
      .filter(Boolean)
  }, [backendCameras])

  const selectedCamera = cameras.find(
    (camera) => camera.id === selectedCameraId
  )

  return (
    <div
      className="relative h-[520px] w-full overflow-hidden rounded-lg"
      style={{
        background: "#071018",
      }}
    >
      <MapContainer
        center={[28.63, 77.225]}
        zoom={14}
        style={{
          height: "100%",
          width: "100%",
        }}
        zoomControl={true}
      >
        <TileLayer
          attribution="&copy; OpenStreetMap contributors"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {DEMO_ROUTES.map((route) => (
          <Polyline
            key={route.id}
            positions={route.positions}
            pathOptions={{
              color: route.color,
              weight: 7,
              opacity: running ? 0.95 : 0.45,
            }}
          >
            <RoutePopup route={route} />
          </Polyline>
        ))}

        {cameras.map((camera) => (
          <CameraMarker
            key={camera.id}
            camera={camera}
            selected={selectedCameraId === camera.id}
            onSelect={onCameraSelect}
          />
        ))}
      </MapContainer>

      <div
        className="absolute left-4 top-4 z-[1000] rounded-lg border px-4 py-3"
        style={{
          background: "rgba(5, 15, 25, 0.92)",
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
          DELHI
        </div>

        <div className="mt-1 flex items-center gap-2 text-[10px] tracking-wider text-slate-300">
          <span
            className="rounded px-2 py-1"
            style={{
              background: "rgba(34, 197, 94, 0.18)",
              color: "#4ade80",
            }}
          >
            LIVE VIEW
          </span>

          <span>
            {String(cameras.length).padStart(2, "0")} CAMERA NODES
          </span>
        </div>
      </div>

      <div
        className="absolute right-4 top-4 z-[1000] rounded-lg border px-4 py-3"
        style={{
          background: "rgba(5, 15, 25, 0.92)",
          borderColor: "rgba(0, 229, 255, 0.25)",
          color: "white",
          backdropFilter: "blur(8px)",
        }}
      >
        <div className="text-[10px] tracking-[0.15em] text-slate-400">
          BACKGROUND TRAFFIC
        </div>

        <div className="mt-2 text-xs font-medium">
          {DEMO_ROUTES.length} ACTIVE ROUTES
        </div>

        <div className="mt-1 text-[9px] text-slate-400">
          Dense demo traffic network
        </div>
      </div>

      <div
        className="absolute left-4 bottom-4 z-[1000] rounded-lg border px-4 py-3"
        style={{
          background: "rgba(5, 15, 25, 0.94)",
          borderColor: "rgba(0, 229, 255, 0.30)",
          color: "white",
          backdropFilter: "blur(8px)",
        }}
      >
        <div
          className="text-[9px] tracking-[0.18em]"
          style={{ color: "#94a3b8" }}
        >
          TRAFFIC CORRIDORS
        </div>

        <div className="mt-2 space-y-1">
          {DEMO_ROUTES.slice(0, 4).map((route) => (
            <div
              key={route.id}
              className="flex items-center gap-2 text-[9px] text-slate-300"
            >
              <span
                className="h-2 w-2 rounded-full"
                style={{
                  background: route.color,
                }}
              />

              {route.name}
            </div>
          ))}

          {DEMO_ROUTES.length > 4 && (
            <div className="text-[8px] text-slate-500">
              + {DEMO_ROUTES.length - 4} additional corridors
            </div>
          )}
        </div>
      </div>

      {selectedCamera && (
        <div
          className="absolute left-1/2 top-4 z-[1000] -translate-x-1/2 rounded-lg border px-4 py-3"
          style={{
            background: "rgba(5, 15, 25, 0.94)",
            borderColor: "rgba(0, 229, 255, 0.35)",
            color: "white",
            backdropFilter: "blur(8px)",
          }}
        >
          <div
            className="text-[9px] tracking-[0.18em]"
            style={{ color: "#00e5ff" }}
          >
            CAMERA INTELLIGENCE
          </div>

          <div className="mt-2 text-sm font-semibold">
            {selectedCamera.id}
          </div>

          <div className="mt-1 text-[9px] text-slate-400">
            {selectedCamera.vehicles} vehicles detected
          </div>
        </div>
      )}

      <button
        type="button"
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
        {running ? "PAUSE NETWORK" : "RESUME NETWORK"}
      </button>

      <div
        className="absolute bottom-1 left-1/2 z-[1000] -translate-x-1/2 text-[9px] tracking-wider"
        style={{
          color: "rgba(255,255,255,0.55)",
        }}
      >
        DEMO TRAFFIC CORRIDORS • VEYTRA
      </div>
    </div>
  )
}