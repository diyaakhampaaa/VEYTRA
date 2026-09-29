import { useState, useEffect } from "react";

/**
 * LiveDetectionShowcase
 *
 * Displays actual evidence frames extracted from VEYTRA's
 * three-camera video network.
 */

const SAMPLES = [
  {
    image: "CAM_01_6195.jpg",
    camera: "CAM_01",
    vehicle: "Vehicle A",
  },
  {
    image: "CAM_02_15708.jpg",
    camera: "CAM_02",
    vehicle: "Vehicle A",
  },
  {
    image: "CAM_03_4522.jpg",
    camera: "CAM_03",
    vehicle: "Vehicle A",
  },
  {
    image: "CAM_01_6608.jpg",
    camera: "CAM_01",
    vehicle: "Vehicle B",
  },
  {
    image: "CAM_02_16422.jpg",
    camera: "CAM_02",
    vehicle: "Vehicle B",
  },
  {
    image: "CAM_03_5355.jpg",
    camera: "CAM_03",
    vehicle: "Vehicle B",
  },
];

const CYCLE_MS = 4000;
const BASE_PATH = "/data/sample_frames/";

export default function LiveDetectionShowcase() {
  const [index, setIndex] = useState(0);
  const [fade, setFade] = useState(true);

  const current = SAMPLES[index];

  useEffect(() => {
    setFade(false);

    const timer = setTimeout(() => {
      setFade(true);
    }, 150);

    return () => clearTimeout(timer);
  }, [index]);

  useEffect(() => {
    const timer = setInterval(() => {
      setIndex((i) => (i + 1) % SAMPLES.length);
    }, CYCLE_MS);

    return () => clearInterval(timer);
  }, []);

  return (
    <section className="relative mt-8">

      <div className="mb-3 flex items-end justify-between">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-[8px] uppercase tracking-[0.25em] text-cyan-300/50">
              Live Camera Evidence
            </span>

            <span className="h-px w-8 bg-cyan-300/20" />
          </div>

          <h2 className="mt-2 text-lg font-medium text-slate-200">
            Camera Evidence Feed
          </h2>

          <p className="mt-1 text-xs text-slate-600">
            Actual frames extracted from VEYTRA's three-camera video network.
          </p>
        </div>

        <div className="hidden items-center gap-4 text-[7px] uppercase tracking-[0.16em] text-slate-600 sm:flex">
          <div className="flex items-center gap-2">
            <span className="veytra-live-dot" />
            Live evidence
          </div>
        </div>
      </div>

      <div className="veytra-panel veytra-hud overflow-hidden rounded-xl p-2">

        <div
          className="relative overflow-hidden rounded-lg"
          style={{
            width: "100%",
            aspectRatio: "16 / 9",
            maxHeight: 430,
            background: "#02080c",
          }}
        >

          <img
            src={BASE_PATH + current.image}
            alt={`${current.camera} evidence frame`}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
              display: "block",
              opacity: fade ? 1 : 0,
              transition: "opacity 400ms ease",
            }}
          />

          <div className="absolute left-3 top-3 rounded-full border border-cyan-300/20 bg-[#02080c]/80 px-3 py-1 text-[8px] uppercase tracking-[0.16em] text-cyan-300/80">
            {current.camera}
          </div>

          <div className="absolute bottom-3 left-3 rounded-md border border-cyan-300/10 bg-[#02080c]/80 px-3 py-2">
            <div className="text-[7px] uppercase tracking-[0.16em] text-slate-500">
              Tracked vehicle
            </div>

            <div className="mt-1 text-xs font-medium text-cyan-300">
              {current.vehicle}
            </div>
          </div>

          <span className="absolute right-3 top-3 rounded-full border border-cyan-300/20 bg-[#02080c]/80 px-3 py-1 text-[7px] uppercase tracking-[0.16em] text-cyan-300/70">
            Evidence Frame
          </span>

          <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(transparent_50%,rgba(34,211,238,0.02)_50%)] bg-[length:100%_4px]" />

        </div>
      </div>

      <div className="mt-3 flex justify-center gap-2">
        {SAMPLES.map((sample, i) => (
          <button
            key={i}
            onClick={() => setIndex(i)}
            aria-label={`Show ${sample.camera} ${sample.vehicle}`}
            className="h-1.5 w-1.5 rounded-full border-none p-0 transition"
            style={{
              background:
                i === index
                  ? "#22d3ee"
                  : "rgba(148,163,184,0.25)",

              boxShadow:
                i === index
                  ? "0 0 6px #22d3ee"
                  : "none",

              cursor: "pointer",
            }}
          />
        ))}
      </div>

    </section>
  );
}