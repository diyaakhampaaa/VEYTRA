import { useState, useEffect, useRef } from "react";

/**
 * LiveDetectionShowcase
 *
 * Cycles through real sample frames (genuine UVH-26 CCTV footage,
 * processed by our actual detect() pipeline) and overlays the real
 * bounding boxes / labels VehicleNet-Y26x and our plate detector
 * produced. Every box, label, and confidence score comes directly
 * from ai/detection/detector.py's real output, precomputed and saved
 * as JSON alongside each image.
 *
 * Styled to match the dark cyan "HUD" theme used across CommandCenter.
 */

const SAMPLES = [
  { image: "real_sample1.png", json: "real_sample1.png.json", width: 1920, height: 1080 },
  { image: "real_sample2.png", json: "real_sample2.png.json", width: 1920, height: 1080 },
  { image: "real_sample3.png", json: "real_sample3.png.json", width: 1920, height: 1080 },
  { image: "demo_clean_plate.jpeg", json: "demo_clean_plate.jpeg.json", width: 665, height: 471 },
];

const CYCLE_MS = 4000;
const BASE_PATH = "/sample_detections/";

const VEHICLE_BOX_COLOR = "#22d3ee";
const PLATE_BOX_COLOR = "#fbbf24";

export default function LiveDetectionShowcase() {
  const [index, setIndex] = useState(0);
  const [detections, setDetections] = useState(null);
  const [fade, setFade] = useState(true);
  const containerRef = useRef(null);
  const [renderedSize, setRenderedSize] = useState({ width: 0, height: 0 });

  const current = SAMPLES[index];

  useEffect(() => {
    let cancelled = false;
    setFade(false);
    fetch(BASE_PATH + current.json)
      .then((res) => res.json())
      .then((data) => {
        if (!cancelled) {
          setDetections(data);
          setFade(true);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setDetections(null);
          setFade(true);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [index]);

  useEffect(() => {
    const timer = setInterval(() => {
      setIndex((i) => (i + 1) % SAMPLES.length);
    }, CYCLE_MS);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    function updateSize() {
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect();
        setRenderedSize({ width: rect.width, height: rect.height });
      }
    }
    updateSize();
    window.addEventListener("resize", updateSize);
    return () => window.removeEventListener("resize", updateSize);
  }, [index]);

  const scaleX = renderedSize.width / current.width;
  const scaleY = renderedSize.height / current.height;

  return (
    <section className="relative mt-8">
      <div className="mb-3 flex items-end justify-between">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-[8px] uppercase tracking-[0.25em] text-cyan-300/50">
              Live Detection Feed
            </span>
            <span className="h-px w-8 bg-cyan-300/20" />
          </div>
          <h2 className="mt-2 text-lg font-medium text-slate-200">
            Pipeline Output
          </h2>
          <p className="mt-1 text-xs text-slate-600">
            Real detections from VehicleNet-Y26x and our fine-tuned plate model.
          </p>
        </div>

        <div className="hidden items-center gap-4 text-[7px] uppercase tracking-[0.16em] text-slate-600 sm:flex">
          <div className="flex items-center gap-2">
            <span className="veytra-live-dot" />
            Vehicle box
          </div>
          <div className="flex items-center gap-2">
            <span className="h-1.5 w-1.5 rounded-full bg-amber-400 shadow-[0_0_8px_#fbbf24]" />
            Plate box
          </div>
        </div>
      </div>

      <div className="veytra-panel veytra-hud overflow-hidden rounded-xl p-2">
        <div
          ref={containerRef}
          style={{
            position: "relative",
            width: "100%",
            aspectRatio: `${current.width} / ${current.height}`,
            maxHeight: 430,
            overflow: "hidden",
            borderRadius: 8,
            background: "#02080c",
          }}
        >
          <img
            src={BASE_PATH + current.image}
            alt="Live VEYTRA detection sample"
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
              display: "block",
              opacity: fade ? 1 : 0,
              transition: "opacity 400ms ease",
            }}
          />

          {fade &&
            detections?.detections?.map((det, i) => {
              const [vx1, vy1, vx2, vy2] = det.vehicle_bbox;
              const plate = det.plate_bbox;

              return (
                <div key={i}>
                  <div
                    style={{
                      position: "absolute",
                      left: vx1 * scaleX,
                      top: vy1 * scaleY,
                      width: (vx2 - vx1) * scaleX,
                      height: (vy2 - vy1) * scaleY,
                      border: `2px solid ${VEHICLE_BOX_COLOR}`,
                      borderRadius: 3,
                      pointerEvents: "none",
                      boxShadow: `0 0 8px ${VEHICLE_BOX_COLOR}40`,
                    }}
                  >
                    <span
                      style={{
                        position: "absolute",
                        top: -20,
                        left: 0,
                        fontSize: 10,
                        fontWeight: 500,
                        color: "#02080c",
                        background: VEHICLE_BOX_COLOR,
                        padding: "2px 6px",
                        borderRadius: 4,
                        whiteSpace: "nowrap",
                        textTransform: "uppercase",
                        letterSpacing: "0.04em",
                      }}
                    >
                      {det.vehicle_type} · {(det.vehicle_confidence * 100).toFixed(0)}%
                    </span>
                  </div>

                  {plate && (
                    <div
                      style={{
                        position: "absolute",
                        left: plate[0] * scaleX,
                        top: plate[1] * scaleY,
                        width: (plate[2] - plate[0]) * scaleX,
                        height: (plate[3] - plate[1]) * scaleY,
                        border: `2px solid ${PLATE_BOX_COLOR}`,
                        borderRadius: 2,
                        pointerEvents: "none",
                        boxShadow: `0 0 8px ${PLATE_BOX_COLOR}40`,
                      }}
                    />
                  )}
                </div>
              );
            })}

          <span
            className="absolute top-3 right-3 rounded-full border border-cyan-300/20 bg-[#02080c]/80 px-3 py-1 text-[7px] uppercase tracking-[0.16em] text-cyan-300/70"
          >
            {detections?.source === "real" ? "Real footage" : "Sample"}
          </span>

          <div className="absolute inset-0 pointer-events-none bg-[linear-gradient(transparent_50%,rgba(34,211,238,0.02)_50%)] bg-[length:100%_4px]" />
        </div>
      </div>

      <div className="mt-3 flex justify-center gap-2">
        {SAMPLES.map((_, i) => (
          <button
            key={i}
            onClick={() => setIndex(i)}
            aria-label={`Show sample ${i + 1}`}
            className="h-1.5 w-1.5 rounded-full border-none p-0 transition"
            style={{
              background: i === index ? "#22d3ee" : "rgba(148,163,184,0.25)",
              boxShadow: i === index ? "0 0 6px #22d3ee" : "none",
              cursor: "pointer",
            }}
          />
        ))}
      </div>
    </section>
  );
}
