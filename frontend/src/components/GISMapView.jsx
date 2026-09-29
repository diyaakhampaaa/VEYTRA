import { useEffect, useMemo, useRef, useState } from "react"
import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Polyline,
  Popup,
  useMap,
} from "react-leaflet"
import "leaflet/dist/leaflet.css"

import { getAnalytics } from "../api/client"


/*
 * VEYTRA traffic visualization
 *
 * Only two traffic states are shown:
 *
 * GREEN = lower traffic / freer movement
 * RED   = higher traffic / heavier movement
 *
 * The actual traffic score comes from backend analytics.
 */
function getTrafficColor(congestion, baseline) {
  const value = Number(congestion || 0)
  const average = Number(baseline || 0.5)

  return value > average
    ? "#ef4444"
    : "#22c55e"
}


function getTrafficLabel(congestion, baseline) {
  const value = Number(congestion || 0)
  const average = Number(baseline || 0.5)

  return value > average
    ? "HIGH TRAFFIC"
    : "LOW TRAFFIC"
}

/*
 * These are the current analytics segment coordinates.
 *
 * They are used as a fallback when a movement flow does not
 * contain usable camera coordinates.
 */
const SEGMENT_POINTS = {
  SEG_A1: [28.63207, 77.219562],
  SEG_B2: [28.628433, 77.230193],
  SEG_C3: [28.590162, 77.250062],
}


/*
 * Fit the map around the actual camera nodes and
 * the road-following traffic paths.
 *
 * The map is fitted only when the network geometry
 * changes rather than continuously during refreshes.
 */
function FitNetwork({ cameras, paths }) {
  const map = useMap()
  const hasFitted = useRef(false)

  useEffect(() => {
    if (hasFitted.current) return

    const points = [
      ...cameras.map((camera) => camera.position),
      ...paths.flatMap((path) => path.geometry || []),
    ]

    if (points.length > 1) {
      map.fitBounds(points, {
        padding: [70, 70],
        maxZoom: 16,
      })

      hasFitted.current = true
    }
  }, [map, cameras, paths])

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
        <div style={{ minWidth: "190px" }}>
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


function TrafficPopup({ path }) {
  return (
    <Popup>
      <div style={{ minWidth: "210px" }}>
        <strong>{path.roadName || "Traffic corridor"}</strong>

        <br />

        Traffic:{" "}
        <span
          style={{
            color: path.color,
            fontWeight: 700,
          }}
        >
          {path.trafficLabel}
        </span>

        <br />

        Congestion:{" "}
        {(path.congestion * 100).toFixed(0)}%

        <br />

        Vehicles: {path.vehicleCount}

        <br />

        Average speed:{" "}
        {path.averageSpeed.toFixed(1)} km/h

        <br />

        <span style={{ color: "#64748b" }}>
          {path.fromCamera} → {path.toCamera}
        </span>
      </div>
    </Popup>
  )
}


/*
 * Ask OSRM for an actual road-following route.
 *
 * IMPORTANT:
 * We do NOT draw a straight line if routing fails.
 *
 * OSRM returns GeoJSON coordinates in:
 *
 * [longitude, latitude]
 *
 * Leaflet expects:
 *
 * [latitude, longitude]
 */
async function getRoadGeometry(from, to) {
  const [fromLat, fromLon] = from
  const [toLat, toLon] = to

  const url =
    `https://router.project-osrm.org/route/v1/driving/` +
    `${fromLon},${fromLat};${toLon},${toLat}` +
    `?overview=full&geometries=geojson`

  const response = await fetch(url)

  if (!response.ok) {
    throw new Error("Road routing request failed")
  }

  const data = await response.json()

  const coordinates =
    data?.routes?.[0]?.geometry?.coordinates

  if (!coordinates || coordinates.length < 2) {
    throw new Error("No road geometry returned")
  }

  return coordinates.map(([longitude, latitude]) => [
    latitude,
    longitude,
  ])
}


export default function GISMapView({
  cameras: backendCameras = [],
  selectedCameraId = null,
  onCameraSelect,
}) {
  const [analytics, setAnalytics] = useState(null)
  const [roadGeometry, setRoadGeometry] = useState({})
  const [loadingRoads, setLoadingRoads] = useState(true)
  const [routingError, setRoutingError] = useState(false)

  /*
   * Prevent repeated OSRM requests for the same
   * camera-to-camera corridor.
   */
  const routeCache = useRef({})


  /*
   * Load backend traffic intelligence.
   *
   * The analytics refreshes every 30 seconds.
   */
  useEffect(() => {
    let cancelled = false

    async function loadAnalytics() {
      try {
        const data = await getAnalytics()

        if (!cancelled) {
          setAnalytics(data)
        }
      } catch (error) {
        console.error(
          "GIS analytics unavailable:",
          error
        )

        if (!cancelled) {
          setAnalytics(null)
        }
      }
    }

    loadAnalytics()

    const interval = setInterval(
      loadAnalytics,
      30000
    )

    return () => {
      cancelled = true
      clearInterval(interval)
    }
  }, [])


  /*
   * Convert backend camera data into Leaflet cameras.
   */
  const cameras = useMemo(() => {
    return backendCameras
      .map((camera) => {
        const latitude = Number(
          camera?.location?.latitude
        )

        const longitude = Number(
          camera?.location?.longitude
        )

        if (
          !Number.isFinite(latitude) ||
          !Number.isFinite(longitude)
        ) {
          return null
        }

        return {
          id: camera.camera_id,
          position: [latitude, longitude],
          vehicles: Number(
            camera.vehicles_detected || 0
          ),
          status: camera.status || "Unknown",
          source: camera.source || "Unknown",
        }
      })
      .filter(Boolean)
  }, [backendCameras])


  /*
   * Quickly find a camera by its ID.
   */
  const cameraLookup = useMemo(() => {
    const lookup = {}

    for (const camera of cameras) {
      lookup[camera.id] = camera
    }

    return lookup
  }, [cameras])


  /*
   * Keep only the latest analytics record
   * for every segment.
   */
  const latestSegments = useMemo(() => {
    const segments = analytics?.segments || []

    const latest = {}

    for (const segment of segments) {
      const existing =
        latest[segment.segment_id]

      if (
        !existing ||
        new Date(segment.timestamp) >
          new Date(existing.timestamp)
      ) {
        latest[segment.segment_id] = segment
      }
    }

    return latest
  }, [analytics])


  /*
   * Convert backend movement flows into
   * actual GIS traffic corridors.
   *
   * Expected backend structure:
   *
   * CAM_02 / SEG_B2 -> CAM_03 / SEG_C3
   * CAM_03 / SEG_C3 -> CAM_01 / SEG_A1
   *
   * The important difference is that we are now
   * reading these dynamically from analytics.
   */
  const movementConnections = useMemo(() => {
    const flows = analytics?.movement_flows || []

    return flows
      .map((flow, index) => {
        const fromCamera =
        flow.origin_camera_id ||
        flow.from_camera_id ||
        flow.source_camera_id ||
        flow.origin_camera ||
        flow.from_camera_id ||
        flow.from_camera

        const toCamera =
          flow.destination_camera_id ||
          flow.to_camera_id ||
          flow.target_camera_id ||
          flow.destination_camera ||
          flow.to_camera_id ||
          flow.to_camera

        const fromSegment =
          flow.origin_segment_id ||
          flow.from_segment_id ||
          flow.source_segment_id ||
          flow.origin_segment ||
          flow.from_segment

        const toSegment =
          flow.destination_segment_id ||
          flow.to_segment_id ||
          flow.target_segment_id ||
          flow.destination_segment ||
          flow.to_segment
        if (
          !fromCamera &&
          !fromSegment
        ) {
          return null
        }

        if (
          !toCamera &&
          !toSegment
        ) {
          return null
        }

        return {
          id:
            `${fromCamera || fromSegment}` +
            `-${toCamera || toSegment}-${index}`,

          fromCamera,
          toCamera,

          fromSegment,
          toSegment,

          vehicleCount: Number(
            flow.vehicle_count || 0
          ),
        }
      })
      .filter(Boolean)
  }, [analytics])


  /*
   * Build traffic paths.
   *
   * Camera coordinates are preferred because the
   * actual observed movement is camera-to-camera.
   *
   * Segment coordinates are used only when a camera
   * coordinate is unavailable.
   */
  const trafficPaths = useMemo(() => {
    return movementConnections
      .map((connection) => {
        const fromPosition =
          cameraLookup[
            connection.fromCamera
          ]?.position ||
          SEGMENT_POINTS[
            connection.fromSegment
          ]

        const toPosition =
          cameraLookup[
            connection.toCamera
          ]?.position ||
          SEGMENT_POINTS[
            connection.toSegment
          ]

        if (!fromPosition || !toPosition) {
          return null
        }

        /*
         * Traffic state comes from the destination
         * segment first, then the source segment.
         */
        const segment =
          latestSegments[
            connection.toSegment
          ] ||
          latestSegments[
            connection.fromSegment
          ]

        if (!segment) {
          return null
        }

        const congestion = Number(
          segment.congestion_score || 0
        )

        const key =
          `${connection.fromCamera || connection.fromSegment}` +
          `-${connection.toCamera || connection.toSegment}`

        const networkAverage =
          Number(
            analytics?.summary?.average_congestion || 0.5
          )
        return {
          id: connection.id,

          key,

          fromCamera:
            connection.fromCamera ||
            connection.fromSegment,

          toCamera:
            connection.toCamera ||
            connection.toSegment,

          segmentId:
            segment.segment_id,

          roadName:
            segment.road_name ||
            "Traffic corridor",

          geometry:
            roadGeometry[key] || [],

          color:
            getTrafficColor(
              congestion,
              networkAverage
            ),

          trafficLabel:
            getTrafficLabel(
              congestion,
              networkAverage
            ),
          congestion,

          vehicleCount:
            Number(
              segment.vehicle_count ||
              connection.vehicleCount ||
              0
            ),

          averageSpeed:
            Number(
              segment.average_speed || 0
            ) * 3.6,
        }
      })
      .filter(Boolean)
  }, [
    movementConnections,
    cameraLookup,
    latestSegments,
    roadGeometry,
  ])


  /*
   * Request road geometry for every new
   * camera-to-camera movement.
   *
   * Existing routes are taken from cache.
   */
  useEffect(() => {
    let cancelled = false

    async function loadRoads() {
      if (!trafficPaths.length) {
        setLoadingRoads(false)
        return
      }

      setLoadingRoads(true)
      setRoutingError(false)

      const nextGeometry = {
        ...routeCache.current,
      }

      let successfulRoutes = 0

      for (const path of trafficPaths) {
        if (cancelled) return

        const fromPosition =
          cameraLookup[path.fromCamera]
            ?.position ||
          SEGMENT_POINTS[
            movementConnections.find(
              (connection) =>
                connection.id === path.id
            )?.fromSegment
          ]

        const toPosition =
          cameraLookup[path.toCamera]
            ?.position ||
          SEGMENT_POINTS[
            movementConnections.find(
              (connection) =>
                connection.id === path.id
            )?.toSegment
          ]

        if (!fromPosition || !toPosition) {
          continue
        }

        /*
         * Already routed.
         */
        if (
          routeCache.current[path.key]
        ) {
          successfulRoutes += 1
          continue
        }

        try {
          const geometry =
            await getRoadGeometry(
              fromPosition,
              toPosition
            )

          nextGeometry[path.key] = geometry
          successfulRoutes += 1
        } catch (error) {
          console.warn(
            `Could not route ${path.fromCamera} -> ${path.toCamera}`,
            error
          )
        }
      }

      if (!cancelled) {
        routeCache.current =
          nextGeometry

        setRoadGeometry(
          nextGeometry
        )

        if (
          successfulRoutes === 0
        ) {
          setRoutingError(true)
        }

        setLoadingRoads(false)
      }
    }

    loadRoads()

    return () => {
      cancelled = true
    }
  }, [
    trafficPaths,
    cameraLookup,
    movementConnections,
  ])


  const selectedCamera =
    cameras.find(
      (camera) =>
        camera.id === selectedCameraId
    )


  const activeSegmentCount =
    Object.keys(latestSegments).length


  const activeRouteCount =
    trafficPaths.filter(
      (path) =>
        path.geometry.length > 1
    ).length


  return (
    <div
      className="relative h-[520px] w-full overflow-hidden rounded-lg"
      style={{
        background: "#071018",
      }}
    >
      <MapContainer
          center={[28.62, 77.23]}
          zoom={13}
          style={{
            height: "100%",
            width: "100%",
          }}
          zoomControl={true}
          zoomControlPosition="bottomright"
        >
        <TileLayer
          attribution="&copy; OpenStreetMap contributors"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <FitNetwork
          cameras={cameras}
          paths={trafficPaths}
        />

        {trafficPaths.map((path) => {
        if (!path.geometry || path.geometry.length < 2) {
          return null
        }

        return (
          <div key={path.id}>
            {/* subtle dark road casing */}
            <Polyline
              positions={path.geometry}
              pathOptions={{
                color: "#17212b",
                weight: 11,
                opacity: 0.55,
                lineCap: "round",
                lineJoin: "round",
              }}
            />

            {/* main traffic intelligence layer */}
            <Polyline
              positions={path.geometry}
              pathOptions={{
                color: path.color,
                weight: 7,
                opacity: 0.48,
                lineCap: "round",
                lineJoin: "round",
              }}
            >
              <TrafficPopup path={path} />
            </Polyline>

            {/* very subtle center highlight */}
            <Polyline
              positions={path.geometry}
              pathOptions={{
                color: path.color,
                weight: 2,
                opacity: 0.30,
                lineCap: "round",
                lineJoin: "round",
              }}
            />
          </div>
        )
      })}

        {cameras.map((camera) => (
          <CameraMarker
            key={camera.id}
            camera={camera}
            selected={
              selectedCameraId === camera.id
            }
            onSelect={onCameraSelect}
          />
        ))}
      </MapContainer>


      {/* top-left information panel */}
      <div
        className="absolute left-4 top-4 z-[1000] rounded-lg border px-4 py-3"
        style={{
          background:
            "rgba(5, 15, 25, 0.92)",
          borderColor:
            "rgba(0, 229, 255, 0.28)",
          color: "white",
          backdropFilter: "blur(8px)",
        }}
      >
        <div
          className="text-xs font-semibold tracking-[0.18em]"
          style={{
            color: "#00e5ff",
          }}
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
              background:
                "rgba(34, 197, 94, 0.14)",
              color: "#4ade80",
            }}
          >
            LIVE INTELLIGENCE
          </span>

          <span>
            {String(
              cameras.length
            ).padStart(2, "0")}{" "}
            CAMERA NODES
          </span>
        </div>
      </div>


      {/* top-right traffic intelligence */}
      <div
        className="absolute right-4 top-4 z-[1000] rounded-lg border px-4 py-3"
        style={{
          background:
            "rgba(5, 15, 25, 0.92)",
          borderColor:
            "rgba(0, 229, 255, 0.22)",
          color: "white",
          backdropFilter: "blur(8px)",
        }}
      >
        <div className="text-[10px] tracking-[0.15em] text-slate-400">
          TRAFFIC INTELLIGENCE
        </div>

        <div className="mt-2 text-xs font-medium">
          {activeRouteCount} ACTIVE CORRIDORS
        </div>

        <div className="mt-2 space-y-1 text-[9px]">
          <div className="flex items-center gap-2">
            <span
              className="h-2 w-2 rounded-full"
              style={{
                background: "#22c55e",
              }}
            />

            LOW TRAFFIC
          </div>

          <div className="flex items-center gap-2">
            <span
              className="h-2 w-2 rounded-full"
              style={{
                background: "#ef4444",
              }}
            />

            HIGH TRAFFIC
          </div>
        </div>
      </div>


      {/* bottom-left data source */}
      <div
        className="absolute left-4 bottom-4 z-[1000] rounded-lg border px-4 py-3"
        style={{
          background:
            "rgba(5, 15, 25, 0.92)",
          borderColor:
            "rgba(0, 229, 255, 0.25)",
          color: "white",
          backdropFilter: "blur(8px)",
        }}
      >
        <div
          className="text-[9px] tracking-[0.18em]"
          style={{
            color: "#94a3b8",
          }}
        >
          DATA SOURCE
        </div>

        <div className="mt-2 text-xs font-semibold">
          VEYTRA TRAFFIC INTELLIGENCE
        </div>

        <div className="mt-1 text-[9px] text-slate-400">
          Vehicle observations · movement flows · GIS routing
        </div>

        {analytics?.summary && (
          <div className="mt-2 text-[9px] text-slate-400">
            {analytics.summary.total_vehicles}{" "}
            vehicles ·{" "}
            {Number(
              analytics.summary.average_speed_kmh ||
              0
            ).toFixed(1)}{" "}
            km/h avg
          </div>
        )}
      </div>


      {/* selected camera */}
      {selectedCamera && (
        <div
          className="absolute left-1/2 top-4 z-[1000] -translate-x-1/2 rounded-lg border px-4 py-3"
          style={{
            background:
              "rgba(5, 15, 25, 0.92)",
            borderColor:
              "rgba(0, 229, 255, 0.28)",
            color: "white",
            backdropFilter: "blur(8px)",
          }}
        >
          <div
            className="text-[9px] tracking-[0.18em]"
            style={{
              color: "#00e5ff",
            }}
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


      {/* routing status */}
      {(loadingRoads ||
        routingError) && (
        <div
          className="absolute bottom-4 left-1/2 z-[1000] -translate-x-1/2 rounded-lg border px-3 py-2 text-[9px]"
          style={{
            background:
              "rgba(5, 15, 25, 0.92)",
            borderColor:
              "rgba(0, 229, 255, 0.20)",
            color: "#94a3b8",
          }}
        >
          {loadingRoads
            ? "BUILDING ROAD-ALIGNED TRAFFIC NETWORK..."
            : "ROAD ROUTING TEMPORARILY UNAVAILABLE"}
        </div>
      )}


      <div
        className="absolute bottom-1 right-4 z-[1000] text-[9px] tracking-wider"
        style={{
          color:
            "rgba(255,255,255,0.45)",
        }}
      >
        OSM ROAD NETWORK • VEYTRA
      </div>
    </div>
  )
}
