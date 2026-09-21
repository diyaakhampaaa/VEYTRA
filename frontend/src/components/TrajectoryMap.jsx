import React, { useEffect, useMemo } from "react";
import { MapContainer, TileLayer, Polyline, Marker, Popup, CircleMarker, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

const TRAJECTORY = [
  { camera: "CAM_A", timestamp: "18:42:10", direction: "NORTH", position: [28.6139, 77.2090] },
  { camera: "CAM_B", timestamp: "18:45:23", direction: "NORTH-EAST", position: [28.6170, 77.2150] },
  { camera: "CAM_C", timestamp: "18:49:32", direction: "EAST", position: [28.6130, 77.2210] },
];

const cameraIcon = (camera) => L.divIcon({
  className: "veytra-camera-icon",
  html: `<div class="cam-label"><span class="cam-dot"></span>${camera}</div>`,
  iconSize: [100, 32],
  iconAnchor: [8, 16],
});

const arrowIcon = (rotation) => L.divIcon({
  className: "veytra-arrow-icon",
  html: `<div class="route-arrow" style="transform:rotate(${rotation}deg)">➜</div>`,
  iconSize: [28, 28],
  iconAnchor: [14, 14],
});

function midpoint(a, b) {
  return [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
}

function bearing(a, b) {
  const p1 = a[0] * Math.PI / 180;
  const p2 = b[0] * Math.PI / 180;
  const dl = (b[1] - a[1]) * Math.PI / 180;
  const y = Math.sin(dl) * Math.cos(p2);
  const x = Math.cos(p1) * Math.sin(p2) - Math.sin(p1) * Math.cos(p2) * Math.cos(dl);
  return Math.atan2(y, x) * 180 / Math.PI;
}

function FitRoute() {
  const map = useMap();
  useEffect(() => {
    map.fitBounds(L.latLngBounds(TRAJECTORY.map(x => x.position)), { padding: [50, 50], maxZoom: 16 });
  }, [map]);
  return null;
}

export default function TrajectoryMap() {
  const route = useMemo(() => TRAJECTORY.map(x => x.position), []);
  const arrows = useMemo(() => TRAJECTORY.slice(0, -1).map((x, i) => ({
    position: midpoint(x.position, TRAJECTORY[i + 1].position),
    rotation: bearing(x.position, TRAJECTORY[i + 1].position),
  })), []);

  return (
    <section className="trajectory-panel">
      <div className="trajectory-title">
        <div>
          <div className="eyebrow">CROSS-CAMERA ANALYSIS</div>
          <h2>Projected Vehicle Trajectory</h2>
        </div>
        <div className="legend">
          <span><i className="legend-line" /> Vehicle trajectory</span>
          <span><i className="legend-dot" /> Camera location</span>
        </div>
      </div>

      <div className="trajectory-map-shell">
        <MapContainer center={[28.615, 77.215]} zoom={15} scrollWheelZoom className="trajectory-map">
          <TileLayer attribution='&copy; OpenStreetMap contributors' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
          <FitRoute />

          <Polyline positions={route} pathOptions={{
            color: "#16e5ff", weight: 5, opacity: 0.95, lineCap: "round", lineJoin: "round"
          }} />

          {arrows.map((a, i) => (
            <Marker key={i} position={a.position} icon={arrowIcon(a.rotation)} interactive={false} />
          ))}

          {TRAJECTORY.map((item, i) => (
            <React.Fragment key={item.camera}>
              <CircleMarker center={item.position} radius={9} pathOptions={{
                color: "#16e5ff", weight: 2, fillColor: "#06131d", fillOpacity: 1
              }} />
              <Marker position={item.position} icon={cameraIcon(item.camera)}>
                <Popup>
                  <strong>{item.camera}</strong><br />
                  {item.timestamp}<br />
                  Direction: {item.direction}
                </Popup>
              </Marker>
            </React.Fragment>
          ))}
        </MapContainer>

        <div className="north">▲<small>N</small></div>
        <div className="map-status"><span /> PROJECTED ROUTE <b>CAM_A → CAM_B → CAM_C</b></div>
      </div>

      <div className="trajectory-events">
        {TRAJECTORY.map((item, i) => (
          <React.Fragment key={item.camera}>
            <article className="event-card">
              <div className="event-number">{String(i + 1).padStart(2, "0")}</div>
              <div className="event-body">
                <div className="event-camera">{item.camera}</div>
                <div className="event-type">CAMERA NODE</div>
                <div className="divider" />
                <div className="event-row"><span>TIMESTAMP</span><strong>{item.timestamp}</strong></div>
                <div className="event-row"><span>DIRECTION</span><strong>{item.direction}</strong></div>
              </div>
            </article>
            {i < TRAJECTORY.length - 1 && <div className="connector">→</div>}
          </React.Fragment>
        ))}
      </div>

      <style>{`
        .trajectory-panel{width:100%;margin:28px 0;padding:24px;box-sizing:border-box;border:1px solid rgba(22,229,255,.2);border-radius:18px;background:#07101a;color:#eef7fb;overflow:hidden;font-family:Inter,system-ui,sans-serif}
        .trajectory-title{display:flex;justify-content:space-between;align-items:end;gap:20px;margin-bottom:18px}
        .eyebrow{color:#16e5ff;font-size:11px;font-weight:700;letter-spacing:.18em;margin-bottom:7px}
        .trajectory-title h2{margin:0;font-size:24px;letter-spacing:-.02em}
        .legend{display:flex;gap:18px;color:#91a9b5;font-size:11px;text-transform:uppercase;letter-spacing:.08em}
        .legend span{display:flex;align-items:center;gap:7px}
        .legend-line{width:23px;height:3px;border-radius:5px;background:#16e5ff;box-shadow:0 0 8px rgba(22,229,255,.7)}
        .legend-dot{width:9px;height:9px;border:2px solid #16e5ff;border-radius:50%}
        .trajectory-map-shell{position:relative;height:430px;border:1px solid rgba(22,229,255,.25);border-radius:14px;overflow:hidden;background:#07151f}
        .trajectory-map{width:100%;height:100%;background:#07151f}
        .trajectory-map .leaflet-tile{filter:brightness(.42) saturate(.55) hue-rotate(155deg) contrast(1.12)}
        .veytra-camera-icon,.veytra-arrow-icon{background:transparent!important;border:0!important}
        .cam-label{display:flex;align-items:center;gap:7px;width:max-content;padding:5px 8px;border:1px solid rgba(22,229,255,.55);border-radius:6px;background:rgba(4,16,25,.94);color:#eafcff;font-size:12px;font-weight:800;letter-spacing:.05em}
        .cam-dot{width:7px;height:7px;border-radius:50%;background:#16e5ff;box-shadow:0 0 10px #16e5ff}
        .route-arrow{color:#16e5ff;font-size:24px;font-weight:900;text-shadow:0 0 10px rgba(22,229,255,.9)}
        .north{position:absolute;top:16px;right:16px;z-index:500;width:43px;height:49px;display:flex;flex-direction:column;align-items:center;justify-content:center;border:1px solid rgba(22,229,255,.35);border-radius:8px;background:rgba(4,15,24,.88);color:#16e5ff;pointer-events:none}
        .north small{font-size:9px}
        .map-status{position:absolute;left:15px;bottom:15px;z-index:500;display:flex;align-items:center;gap:8px;padding:9px 12px;border:1px solid rgba(22,229,255,.28);border-radius:7px;background:rgba(4,15,24,.9);color:#9bb2bd;font-size:10px;font-weight:700;letter-spacing:.1em;pointer-events:none}
        .map-status span{width:7px;height:7px;border-radius:50%;background:#16e5ff;box-shadow:0 0 9px #16e5ff}
        .map-status b{color:#eafcff}
        .trajectory-events{display:grid;grid-template-columns:1fr 32px 1fr 32px 1fr;align-items:center;margin-top:18px}
        .event-card{min-height:160px;padding:20px;display:flex;gap:16px;box-sizing:border-box;border:1px solid rgba(22,229,255,.18);border-radius:13px;background:rgba(2,9,15,.78)}
        .event-number{width:42px;height:42px;flex:0 0 42px;display:grid;place-items:center;border:1px solid rgba(22,229,255,.65);border-radius:50%;color:#16e5ff;font-size:12px;font-weight:800}
        .event-body{flex:1}.event-camera{font-size:17px;font-weight:800}.event-type{margin-top:4px;color:#477384;font-size:10px;font-weight:700;letter-spacing:.14em}
        .divider{height:1px;margin:17px 0;background:rgba(255,255,255,.08)}
        .event-row{display:flex;justify-content:space-between;gap:12px;margin-top:10px}.event-row span{color:#526b78;font-size:9px;font-weight:700;letter-spacing:.13em}.event-row strong{color:#8ca7b3;font-size:11px}.event-row:last-child strong{color:#16e5ff}
        .connector{color:#16e5ff;font-size:24px;text-align:center;text-shadow:0 0 9px rgba(22,229,255,.6)}
        @media(max-width:900px){.trajectory-title{align-items:flex-start;flex-direction:column}.legend{flex-wrap:wrap}.trajectory-events{grid-template-columns:1fr;gap:10px}.connector{display:none}.trajectory-map-shell{height:360px}}
      `}</style>
    </section>
  );
}
