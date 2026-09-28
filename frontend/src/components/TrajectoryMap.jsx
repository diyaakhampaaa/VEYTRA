import React, { useEffect, useMemo } from "react";
import {
  MapContainer,
  TileLayer,
  Polyline,
  Marker,
  Popup,
  CircleMarker,
  useMap,
} from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

const INDIA_TIMEZONE = "Asia/Kolkata";

/*
 * DEMO TRAJECTORY
 * These values are hardcoded for the final presentation.
 * They are simulated route metadata, not real GPS observations.
 */
const DEMO_TRAJECTORY = [
  {
    event_id: "demo-c01",
    camera_id: "C01",
    timestamp: "2026-09-27T10:02:15+05:30",
    direction: "South-East",
    road_name: "Kashmere Gate Road",
    speed_kmh: 42,
    location: {
      latitude: 28.666949,
      longitude: 77.229996,
    },
  },
  {
    event_id: "demo-c02",
    camera_id: "C02",
    timestamp: "2026-09-27T10:06:42+05:30",
    direction: "South",
    road_name: "Netaji Subhash Marg",
    speed_kmh: 38,
    location: {
      latitude: 28.667140,
      longitude: 77.231179,
    },
  },
  {
    event_id: "demo-c03",
    camera_id: "C03",
    timestamp: "2026-09-27T10:12:08+05:30",
    direction: "South-East",
    road_name: "Mahatma Gandhi Marg",
    speed_kmh: 45,
    location: {
      latitude: 28.665748,
      longitude: 77.232073,
    },
  },
];

function formatTimestamp(value) {
  if (!value) return "Unavailable";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);

  return new Intl.DateTimeFormat("en-IN", {
    timeZone: INDIA_TIMEZONE,
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: true,
  }).format(date);
}

function formatValue(value, suffix = "") {
  if (value === null || value === undefined || value === "") {
    return "Unavailable";
  }

  return `${value}${suffix}`;
}

function cameraIcon(camera) {
  return L.divIcon({
    className: "veytra-camera-icon",
    html: `<div class="cam-label"><span class="cam-dot"></span>${camera}</div>`,
    iconSize: [100, 32],
    iconAnchor: [8, 16],
  });
}

function midpoint(a, b) {
  return [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
}

function bearing(a, b) {
  const p1 = (a[0] * Math.PI) / 180;
  const p2 = (b[0] * Math.PI) / 180;
  const dl = ((b[1] - a[1]) * Math.PI) / 180;

  const y = Math.sin(dl) * Math.cos(p2);
  const x =
    Math.cos(p1) * Math.sin(p2) -
    Math.sin(p1) * Math.cos(p2) * Math.cos(dl);

  return (Math.atan2(y, x) * 180) / Math.PI;
}

function arrowIcon(rotation) {
  return L.divIcon({
    className: "veytra-arrow-icon",
    html: `<div class="route-arrow" style="transform:rotate(${rotation}deg)">➜</div>`,
    iconSize: [28, 28],
    iconAnchor: [14, 14],
  });
}

function FitRoute({ points }) {
  const map = useMap();

  useEffect(() => {
    if (points.length > 0) {
      map.fitBounds(L.latLngBounds(points), {
        padding: [45, 45],
        maxZoom: 20,
      });
    }
  }, [map, points]);

  return null;
}

function TrajectoryMap({ cameraSequence = [] }) {
  /*
   * The backend sequence is still accepted by the component,
   * but the displayed route is currently the controlled demo route.
   */
  const events = useMemo(() => {
    return DEMO_TRAJECTORY.map((item, index) => ({
      ...item,
      eventKey: item.event_id || `${item.camera_id}-${index}`,
    }));
  }, [cameraSequence]);

  const geoEvents = useMemo(
    () =>
      events.map((item) => ({
        ...item,
        position: [
          Number(item.location.latitude),
          Number(item.location.longitude),
        ],
      })),
    [events]
  );

  const route = useMemo(
    () => geoEvents.map((item) => item.position),
    [geoEvents]
  );

  const arrows = useMemo(
    () =>
      geoEvents.slice(0, -1).map((item, index) => ({
        position: midpoint(
          item.position,
          geoEvents[index + 1].position
        ),
        rotation: bearing(
          item.position,
          geoEvents[index + 1].position
        ),
      })),
    [geoEvents]
  );

  const cameraCount = geoEvents.length;
  const hasRoute = geoEvents.length > 1;
  const mapCenter = geoEvents[0]?.position || [28.64, 77.23];

  return (
    <section className="trajectory-panel">
      <div className="trajectory-title">
        <div>
          <div className="eyebrow">CROSS-CAMERA ANALYSIS</div>
          <h2>Vehicle Trajectory</h2>
          <p className="trajectory-subtitle">
            Reconstructed camera sequence across the monitored network
          </p>
        </div>

        <div className="trajectory-summary">
          <div>
            <strong>{cameraCount}</strong>
            <span>CAMERAS</span>
          </div>

          <div>
            <strong>{events.length}</strong>
            <span>OBSERVATIONS</span>
          </div>
        </div>
      </div>

      <div className="map-heading">
        <span>LOCATION VIEW</span>

        <span>
          Simulated route metadata · C01 → C02 → C03
        </span>
      </div>

      <div className="trajectory-map-shell">
        <MapContainer
          center={mapCenter}
          zoom={14}
          scrollWheelZoom
          className="trajectory-map"
        >
          <TileLayer
            attribution="&copy; OpenStreetMap contributors"
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          <FitRoute points={route} />

          {hasRoute && (
            <Polyline
              positions={route}
              pathOptions={{
                color: "#16e5ff",
                weight: 5,
                opacity: 0.95,
                lineCap: "round",
                lineJoin: "round",
              }}
            />
          )}

          {arrows.map((arrow, index) => (
            <Marker
              key={`arrow-${index}`}
              position={arrow.position}
              icon={arrowIcon(arrow.rotation)}
              interactive={false}
            />
          ))}

          {geoEvents.map((item) => (
            <React.Fragment key={item.eventKey}>
              <CircleMarker
                center={item.position}
                radius={9}
                pathOptions={{
                  color: "#16e5ff",
                  weight: 2,
                  fillColor: "#06131d",
                  fillOpacity: 1,
                }}
              />

              <Marker
                position={item.position}
                icon={cameraIcon(item.camera_id)}
              >
                <Popup>
                  <strong>{item.camera_id}</strong>
                  <br />
                  {formatTimestamp(item.timestamp)}
                  <br />
                  Direction: {formatValue(item.direction)}
                  <br />
                  Road: {formatValue(item.road_name)}
                  <br />
                  Speed: {formatValue(item.speed_kmh, " km/h")}
                  <br />
                  <br />
                  <strong>SIMULATED ROUTE</strong>
                </Popup>
              </Marker>
            </React.Fragment>
          ))}
        </MapContainer>

        <div className="north">
          ▲<small>N</small>
        </div>

        <div className="map-status">
          <span />
          PROJECTED ROUTE <b>C01 → C02 → C03</b>
        </div>
      </div>

      <div className="sequence-heading">
        <div>
          <div className="eyebrow">OBSERVATION RECORD</div>
          <h3>Camera Sequence</h3>
        </div>

        <span className="sequence-count">
          {events.length} EVENTS
        </span>
      </div>

      <div className="trajectory-events">
        {events.map((item, index) => (
          <React.Fragment key={item.eventKey}>
            <article className="event-card">
              <div className="event-number">
                {String(index + 1).padStart(2, "0")}
              </div>

              <div className="event-body">
                <div className="event-topline">
                  <div>
                    <div className="event-camera">
                      {item.camera_id}
                    </div>

                    <div className="event-type">
                      CAMERA OBSERVATION · SIMULATED
                    </div>
                  </div>

                  <span className="event-index">
                    EVENT {String(index + 1).padStart(2, "0")}
                  </span>
                </div>

                <div className="divider" />

                <div className="event-row">
                  <span>TIMESTAMP</span>
                  <strong>
                    {formatTimestamp(item.timestamp)}
                  </strong>
                </div>

                <div className="event-row">
                  <span>DIRECTION</span>
                  <strong>
                    {formatValue(item.direction)}
                  </strong>
                </div>

                <div className="event-row">
                  <span>ROAD</span>
                  <strong>
                    {formatValue(item.road_name)}
                  </strong>
                </div>

                <div className="event-row">
                  <span>SPEED</span>
                  <strong>
                    {formatValue(item.speed_kmh, " km/h")}
                  </strong>
                </div>

                <div className="event-row">
                  <span>LOCATION</span>
                  <strong>
                    {Number(item.location.latitude).toFixed(5)},{" "}
                    {Number(item.location.longitude).toFixed(5)}
                  </strong>
                </div>
              </div>
            </article>

            {index < events.length - 1 && (
              <div className="connector" aria-hidden="true">
                →
              </div>
            )}
          </React.Fragment>
        ))}
      </div>

      <style>{`
        .trajectory-panel {
          width: 100%;
          margin: 28px 0;
          padding: 24px;
          box-sizing: border-box;
          border: 1px solid rgba(22,229,255,.2);
          border-radius: 18px;
          background: #07101a;
          color: #eef7fb;
          overflow: hidden;
          font-family: Inter, system-ui, sans-serif;
        }

        .trajectory-title {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          gap: 20px;
          margin-bottom: 22px;
        }

        .eyebrow {
          color: #16e5ff;
          font-size: 10px;
          font-weight: 700;
          letter-spacing: .18em;
          margin-bottom: 7px;
        }

        .trajectory-title h2,
        .sequence-heading h3 {
          margin: 0;
          font-size: 22px;
          font-weight: 600;
          letter-spacing: -.02em;
        }

        .trajectory-subtitle {
          margin: 7px 0 0;
          color: #8299a5;
          font-size: 12px;
          line-height: 1.6;
        }

        .trajectory-summary {
          display: flex;
          gap: 10px;
        }

        .trajectory-summary > div {
          min-width: 76px;
          padding: 10px 12px;
          border: 1px solid rgba(22,229,255,.13);
          border-radius: 9px;
          background: rgba(22,229,255,.025);
          text-align: center;
        }

        .trajectory-summary strong {
          display: block;
          color: #dffaff;
          font-family: ui-monospace, monospace;
          font-size: 19px;
        }

        .trajectory-summary span {
          display: block;
          margin-top: 4px;
          color: #63808d;
          font-size: 8px;
          font-weight: 700;
          letter-spacing: .12em;
        }

        .map-heading {
          display: flex;
          justify-content: space-between;
          flex-wrap: wrap;
          gap: 8px;
          margin-bottom: 10px;
          color: #718c98;
          font-size: 9px;
          font-weight: 700;
          letter-spacing: .12em;
          text-transform: uppercase;
        }

        .trajectory-map-shell {
          position: relative;
          height: 390px;
          border: 1px solid rgba(22,229,255,.25);
          border-radius: 14px;
          overflow: hidden;
          background: #07151f;
        }

        .trajectory-map {
          width: 100%;
          height: 100%;
          background: #07151f;
        }

        .trajectory-map .leaflet-tile {
          filter: brightness(.42) saturate(.55) hue-rotate(155deg) contrast(1.12);
        }

        .veytra-camera-icon,
        .veytra-arrow-icon {
          background: transparent !important;
          border: 0 !important;
        }

        .cam-label {
          display: flex;
          align-items: center;
          gap: 7px;
          width: max-content;
          padding: 5px 8px;
          border: 1px solid rgba(22,229,255,.55);
          border-radius: 6px;
          background: rgba(4,16,25,.94);
          color: #eafcff;
          font-size: 12px;
          font-weight: 800;
          letter-spacing: .05em;
        }

        .cam-dot {
          width: 7px;
          height: 7px;
          border-radius: 50%;
          background: #16e5ff;
          box-shadow: 0 0 10px #16e5ff;
        }

        .route-arrow {
          color: #16e5ff;
          font-size: 24px;
          font-weight: 900;
          text-shadow: 0 0 10px rgba(22,229,255,.9);
        }

        .north {
          position: absolute;
          top: 16px;
          right: 16px;
          z-index: 500;
          width: 43px;
          height: 49px;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          border: 1px solid rgba(22,229,255,.35);
          border-radius: 8px;
          background: rgba(4,15,24,.88);
          color: #16e5ff;
          pointer-events: none;
        }

        .north small {
          font-size: 9px;
        }

        .map-status {
          position: absolute;
          left: 15px;
          bottom: 15px;
          z-index: 500;
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 9px 12px;
          border: 1px solid rgba(22,229,255,.28);
          border-radius: 7px;
          background: rgba(4,15,24,.9);
          color: #c3d6de;
          font-size: 9px;
          font-weight: 700;
          letter-spacing: .1em;
          pointer-events: none;
        }

        .map-status span {
          width: 7px;
          height: 7px;
          border-radius: 50%;
          background: #16e5ff;
          box-shadow: 0 0 9px #16e5ff;
        }

        .map-status b {
          color: #16e5ff;
        }

        .sequence-heading {
          display: flex;
          align-items: end;
          justify-content: space-between;
          gap: 12px;
          margin-top: 25px;
          margin-bottom: 14px;
        }

        .sequence-heading h3 {
          font-size: 17px;
        }

        .sequence-count {
          color: #78909b;
          font-size: 9px;
          font-weight: 700;
          letter-spacing: .12em;
        }

        .trajectory-events {
          display: flex;
          align-items: stretch;
          gap: 12px;
          overflow-x: auto;
          overflow-y: hidden;
          padding-bottom: 10px;
          scroll-behavior: smooth;
        }

        .trajectory-events::-webkit-scrollbar {
          height: 6px;
        }

        .trajectory-events::-webkit-scrollbar-track {
          background: rgba(255,255,255,.04);
          border-radius: 10px;
        }

        .trajectory-events::-webkit-scrollbar-thumb {
          background: rgba(22,229,255,.35);
          border-radius: 10px;
        }

        .event-card {
          flex: 0 0 330px;
          min-width: 0;
          padding: 17px;
          display: flex;
          gap: 13px;
          box-sizing: border-box;
          border: 1px solid rgba(22,229,255,.18);
          border-radius: 13px;
          background: rgba(2,9,15,.78);
        }

        .event-number {
          width: 36px;
          height: 36px;
          flex: 0 0 36px;
          display: grid;
          place-items: center;
          border: 1px solid rgba(22,229,255,.65);
          border-radius: 50%;
          color: #16e5ff;
          font-size: 11px;
          font-weight: 800;
        }

        .event-body {
          flex: 1;
          min-width: 0;
        }

        .event-topline {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          gap: 8px;
        }

        .event-camera {
          color: #eef7fb;
          font-size: 16px;
          font-weight: 800;
        }

        .event-type {
          margin-top: 4px;
          color: #63808d;
          font-size: 9px;
          font-weight: 700;
          letter-spacing: .12em;
        }

        .event-index {
          flex: 0 0 auto;
          color: #58717d;
          font-size: 8px;
          font-weight: 700;
          letter-spacing: .08em;
        }

        .divider {
          height: 1px;
          margin: 13px 0;
          background: rgba(255,255,255,.08);
        }

        .event-row {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          gap: 12px;
          margin-top: 10px;
        }

        .event-row span {
          flex: 0 0 auto;
          color: #68808b;
          font-size: 8px;
          font-weight: 700;
          letter-spacing: .1em;
        }

        .event-row strong {
          min-width: 0;
          color: #b3c6ce;
          font-size: 10px;
          font-weight: 500;
          text-align: right;
          overflow-wrap: anywhere;
        }

        .connector {
          flex: 0 0 auto;
          align-self: center;
          color: #16e5ff;
          font-size: 21px;
          text-shadow: 0 0 9px rgba(22,229,255,.6);
        }

        @media (max-width: 700px) {
          .trajectory-panel {
            padding: 16px;
          }

          .trajectory-title {
            flex-direction: column;
          }

          .trajectory-summary {
            width: 100%;
          }

          .trajectory-summary > div {
            flex: 1;
          }

          .trajectory-map-shell {
            height: 320px;
          }

          .event-card {
            flex-basis: min(300px, 82vw);
          }

          .map-heading {
            flex-direction: column;
          }
        }
      `}</style>
    </section>
  );
}

export default TrajectoryMap;