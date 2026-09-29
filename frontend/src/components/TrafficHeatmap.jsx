import { useMemo } from "react"
import {
  MapContainer,
  TileLayer,
  Circle,
  Popup,
} from "react-leaflet"
import "leaflet/dist/leaflet.css"

const DELHI_HEAT_POINTS = [
  { name: "Connaught Place", position: [28.6315, 77.2167], score: 0.86 },
  { name: "Kashmere Gate", position: [28.6675, 77.2282], score: 0.58 },
  { name: "Karol Bagh", position: [28.6514, 77.1907], score: 0.42 },
  { name: "India Gate", position: [28.6129, 77.2295], score: 0.72 },
  { name: "Lajpat Nagar", position: [28.5677, 77.2433], score: 0.64 },
  { name: "Hauz Khas", position: [28.5494, 77.2001], score: 0.35 },
  { name: "Saket", position: [28.5244, 77.2066], score: 0.78 },
  { name: "Dwarka", position: [28.5921, 77.0460], score: 0.48 },
  { name: "Rohini", position: [28.7041, 77.1025], score: 0.55 },
  { name: "Mayur Vihar", position: [28.6090, 77.2940], score: 0.69 },
]

function getHeatColor(score) {
  if (score >= 0.75) return "#ef4444"
  if (score >= 0.55) return "#f97316"
  return "#facc15"
}

function TrafficHeatmap() {
  const points = useMemo(
    () => DELHI_HEAT_POINTS,
    []
  )

  return (
    <div
      className="relative h-[520px] w-full overflow-hidden rounded-lg"
      style={{ background: "#071018" }}
    >
      <MapContainer
        center={[28.6139, 77.2090]}
        zoom={11}
        style={{
          height: "100%",
          width: "100%",
        }}
      >
        <TileLayer
          attribution="&copy; OpenStreetMap contributors"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {points.map((point) => (
          <Circle
            key={point.name}
            center={point.position}
            radius={900}
            pathOptions={{
              color: getHeatColor(point.score),
              fillColor: getHeatColor(point.score),
              fillOpacity: 0.28,
              opacity: 0.15,
              weight: 1,
            }}
          >
            <Popup>
              <strong>{point.name}</strong>
              <br />
              Congestion: {Math.round(point.score * 100)}%
            </Popup>
          </Circle>
        ))}
      </MapContainer>

      <div className="absolute left-4 top-4 z-[1000] rounded-lg border border-cyan-400/20 bg-[#050f19]/90 px-4 py-3 text-white backdrop-blur-md">
        <div className="text-[10px] font-semibold tracking-[0.18em] text-cyan-400">
          SPATIAL INTELLIGENCE
        </div>

        <div className="mt-1 text-lg font-semibold">
          DELHI TRAFFIC HEATMAP
        </div>

        <div className="mt-2 flex gap-3 text-[9px] uppercase tracking-wider text-slate-400">
          <span className="text-yellow-400">LOW</span>
          <span className="text-orange-400">MEDIUM</span>
          <span className="text-red-400">HIGH</span>
        </div>
      </div>
    </div>
  )
}

export default TrafficHeatmap
