import { useEffect, useState } from "react"
import {
  getVerificationEvents,
  runVerification,
} from "../api/client"
import SourceBadge from "../components/SourceBadge"

const DEMO_EVENT = {
  event_id: "DEMO-EVT-2048",
  camera_id: "CAM_02",
  plate: "KA01A8134",
  original_plate: "KA01A8134",
  corrected_plate: "KA01AB1234",
  ocr_confidence: 0.61,
  reid_similarity: 0.91,
  verification_confidence: 0.91,
  supporting_cameras: ["CAM_01", "CAM_03"],
  reason:
    "Neighbouring camera agreement (CAM_01, CAM_03) + high Re-ID similarity",
  source: "simulated",
}

const DEMO_PAYLOAD = [
  {
    event_id: "DEMO-EVT-2048",
    camera_id: "CAM_02",
    plate: "KA01A8134",
    ocr_confidence: 0.61,
    timestamp: "2026-09-06T14:32:18",
    reid_similarity: 0.91,
    nearby_events: [
      {
        event_id: "DEMO-EVT-2047",
        camera_id: "CAM_01",
        plate: "KA01AB1234",
      },
      {
        event_id: "DEMO-EVT-2049",
        camera_id: "CAM_03",
        plate: "KA01AB1234",
      },
    ],
  },
]

const CAMERA_OBSERVATIONS = [
  {
    camera: "CAM_01",
    time: "14:31:52",
    plate: "KA01AB1234",
    confidence: 94,
    status: "consistent",
  },
  {
    camera: "CAM_02",
    time: "14:32:18",
    plate: "KA01A8134",
    confidence: 61,
    status: "suspicious",
  },
  {
    camera: "CAM_03",
    time: "14:32:44",
    plate: "KA01AB1234",
    confidence: 96,
    status: "consistent",
  },
]

const STEPS = [
  "Detecting contradiction",
  "Checking OCR confidence",
  "Comparing neighbouring plates",
  "Checking vehicle appearance",
  "Checking temporal feasibility",
  "Selecting supporting evidence",
  "Applying verified correction",
  "Updating trajectory",
]

function SmartVerification() {
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [demoRunning, setDemoRunning] = useState(false)
  const [demoStep, setDemoStep] = useState(-1)

  useEffect(() => {
    loadEvents()
  }, [])

  const loadEvents = async () => {
    try {
      setLoading(true)
      setError("")

      const data = await getVerificationEvents()

      setEvents(
        Array.isArray(data)
          ? data
          : data?.events || data?.results || []
      )
    } catch (err) {
      setError("Unable to load verification events.")
    } finally {
      setLoading(false)
    }
  }

  const sleep = (ms) =>
    new Promise((resolve) => setTimeout(resolve, ms))

  const runDemo = () => {
    if (demoRunning) return

    setError("")
    setEvents([])
    setDemoStep(0)
    setDemoRunning(true)
  }

  useEffect(() => {
    if (!demoRunning) return

    let cancelled = false

    const runVerificationCycle = async () => {
      while (!cancelled) {
        setDemoStep(0)

        for (let step = 1; step < STEPS.length; step++) {
          await sleep(850)

          if (cancelled) return

          setDemoStep(step)

          /*
           * At the evidence stage we call the REAL
           * backend verification pipeline.
           *
           * The UI animation continues while the request
           * is being processed.
           */
          if (step === 5) {
            try {
              const result = await runVerification(DEMO_PAYLOAD)

              if (!cancelled && result?.results?.length) {
                setEvents(result.results)
              }
            } catch (err) {
              if (!cancelled) {
                setError(
                  err.message ||
                    "Verification request failed."
                )
              }
            }
          }
        }

        /*
         * Keep the completed correction visible
         * before beginning the next observation cycle.
         */
        await sleep(3500)

        if (!cancelled) {
          setEvents([])
        }
      }
    }

    runVerificationCycle()

    return () => {
      cancelled = true
    }
  }, [demoRunning])

  const displayEvents =
    events.length > 0
      ? events
      : demoRunning
        ? [DEMO_EVENT]
        : []

  const suspiciousCount = displayEvents.filter(
    (event) =>
      event.original_plate &&
      event.corrected_plate &&
      event.original_plate !== event.corrected_plate
  ).length

  return (
    <div className="min-h-screen bg-[#02070b] text-white">

      {/* =========================================================
          HEADER
      ========================================================= */}

      <div className="mb-7 flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">

        <div>

          <div className="mb-2 flex items-center gap-2 text-xs uppercase tracking-[0.28em] text-cyan-400">
            <span className="veytra-live-dot" />
            Verification Intelligence
          </div>

          <h1 className="text-3xl font-semibold tracking-tight">
            Parallel Intelligence Assurance
          </h1>

          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
            VEYTRA continuously checks uncertain vehicle observations in
            parallel while the main city intelligence pipeline keeps running.
          </p>

        </div>

        <div className="flex flex-wrap gap-3">

          <div className="veytra-panel px-4 py-3">

            <div className="text-[9px] uppercase tracking-[0.2em] text-slate-600">
              Live Pipeline
            </div>

            <div className="mt-1 flex items-center gap-2 text-sm text-cyan-300">
              <span className="veytra-live-dot" />
              ACTIVE
            </div>

          </div>

          <div className="veytra-panel px-4 py-3">

            <div className="text-[9px] uppercase tracking-[0.2em] text-slate-600">
              Verification
            </div>

            <div className="mt-1 flex items-center gap-2 text-sm text-amber-300">

              <span
                className={`h-2 w-2 rounded-full ${
                  demoRunning
                    ? "animate-pulse bg-amber-300"
                    : "bg-cyan-400"
                }`}
              />

              {demoRunning
                ? "INVESTIGATING"
                : "STANDBY"}

            </div>

          </div>

        </div>

      </div>


      {/* =========================================================
          USP FLOW
      ========================================================= */}

      <div className="veytra-panel mb-7 overflow-hidden">

        <div className="border-b border-cyan-400/10 px-5 py-4">

          <div className="text-[10px] uppercase tracking-[0.22em] text-slate-500">
            Parallel Verification Flow
          </div>

        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8">

          {[
            ["01", "Observe"],
            ["02", "Detect"],
            ["03", "Investigate"],
            ["04", "Evidence"],
            ["05", "Verify"],
            ["06", "Correct"],
            ["07", "Propagate"],
            ["08", "Continue"],
          ].map(([number, label], index) => {

            const active = demoStep >= index
            const current = demoStep === index

            return (
              <div
                key={number}
                className={`relative border-r border-b border-cyan-400/10 px-4 py-4 transition-all ${
                  active ? "bg-cyan-400/[0.04]" : ""
                }`}
              >

                <div
                  className={`font-mono text-[10px] ${
                    active
                      ? "text-cyan-400"
                      : "text-slate-700"
                  }`}
                >
                  {number}
                </div>

                <div
                  className={`mt-1 text-xs ${
                    current
                      ? "text-white"
                      : active
                        ? "text-slate-300"
                        : "text-slate-600"
                  }`}
                >
                  {label}
                </div>

                {current && (
                  <div className="absolute bottom-0 left-0 h-[2px] w-full animate-pulse bg-cyan-400" />
                )}

              </div>
            )
          })}

        </div>

      </div>


      {/* =========================================================
          CONTROLLED DEMO
      ========================================================= */}

      <div className="mb-7 flex flex-col gap-4 border border-amber-400/10 bg-amber-400/[0.025] p-5 lg:flex-row lg:items-center lg:justify-between">

        <div>

          <div className="flex items-center gap-2">

            <span className="text-amber-300">
              ◆
            </span>

            <span className="text-xs font-medium uppercase tracking-[0.18em] text-amber-300">
              Controlled Verification Scenario
            </span>

          </div>

          <p className="mt-2 max-w-2xl text-xs leading-5 text-slate-500">
            Demonstrates a low-confidence OCR contradiction across three
            cameras. This is a controlled prototype scenario, not live CCTV.
          </p>

        </div>

        <button
          onClick={() => {
            if (demoRunning) {
              setDemoRunning(false)
              setDemoStep(-1)
            } else {
              runDemo()
            }
          }}
          className="border border-cyan-400/30 bg-cyan-400/10 px-5 py-3 text-xs font-medium uppercase tracking-[0.15em] text-cyan-300 transition hover:bg-cyan-400/20"
        >
          {demoRunning
            ? "■ Stop Parallel Monitoring"
            : "▶ Start Parallel Monitoring"}
        </button>

      </div>


      {/* =========================================================
          CAMERA OBSERVATIONS
      ========================================================= */}

      <section className="mb-7">

        <div className="mb-3 flex items-end justify-between">

          <div>

            <div className="text-[10px] uppercase tracking-[0.22em] text-slate-600">
              Camera Evidence
            </div>

            <h2 className="mt-1 text-lg font-medium">
              Same Vehicle / Distributed Observations
            </h2>

          </div>

          <div className="font-mono text-[10px] text-slate-600">
            VEHICLE V18
          </div>

        </div>


        <div className="grid gap-4 md:grid-cols-3">

          {CAMERA_OBSERVATIONS.map((camera) => {

            const suspicious =
              camera.status === "suspicious"

            return (
              <div
                key={camera.camera}
                className={`veytra-panel overflow-hidden transition-all ${
                  suspicious
                    ? "border-amber-400/30 shadow-[0_0_30px_rgba(245,158,11,0.05)]"
                    : ""
                }`}
              >

                {/* Camera header */}

                <div className="flex items-center justify-between border-b border-white/5 px-4 py-3">

                  <div className="flex items-center gap-2">

                    <div
                      className={`h-2 w-2 rounded-full ${
                        suspicious
                          ? "animate-pulse bg-amber-400"
                          : "bg-cyan-400"
                      }`}
                    />

                    <span className="font-mono text-xs text-slate-300">
                      {camera.camera}
                    </span>

                  </div>

                  <span
                    className={`text-[9px] uppercase tracking-[0.15em] ${
                      suspicious
                        ? "text-amber-300"
                        : "text-cyan-300"
                    }`}
                  >
                    {suspicious
                      ? "Contradiction"
                      : "Consistent"}
                  </span>

                </div>


                {/* Evidence visual */}

                <div
                  className={`relative flex h-28 items-center justify-center ${
                    suspicious
                      ? "bg-amber-400/[0.035]"
                      : "bg-cyan-400/[0.018]"
                  }`}
                >

                  <div className="absolute inset-4 border border-dashed border-white/5" />

                  <div className="text-center">

                    <div className="font-mono text-xl tracking-widest text-slate-200">
                      {camera.plate}
                    </div>

                    <div className="mt-2 text-[9px] uppercase tracking-[0.18em] text-slate-600">
                      OCR observation
                    </div>

                  </div>

                  {suspicious && (
                    <div className="absolute right-3 top-3 border border-amber-400/20 bg-amber-400/5 px-2 py-1 text-[8px] uppercase tracking-wider text-amber-300">
                      LOW CONFIDENCE
                    </div>
                  )}

                </div>


                {/* Metadata */}

                <div className="grid grid-cols-2 border-t border-white/5">

                  <div className="border-r border-white/5 px-4 py-3">

                    <div className="text-[8px] uppercase tracking-wider text-slate-600">
                      Timestamp
                    </div>

                    <div className="mt-1 font-mono text-xs text-slate-400">
                      {camera.time}
                    </div>

                  </div>

                  <div className="px-4 py-3">

                    <div className="text-[8px] uppercase tracking-wider text-slate-600">
                      OCR Confidence
                    </div>

                    <div
                      className={`mt-1 font-mono text-xs ${
                        suspicious
                          ? "text-amber-300"
                          : "text-cyan-300"
                      }`}
                    >
                      {camera.confidence}%
                    </div>

                  </div>

                </div>

              </div>
            )
          })}

        </div>

      </section>


      {/* =========================================================
          MAIN INVESTIGATION AREA
      ========================================================= */}

      <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">


        {/* =======================================================
            VERIFICATION ENGINE
        ======================================================= */}

        <div className="veytra-panel overflow-hidden">

          <div className="flex items-center justify-between border-b border-cyan-400/10 px-5 py-4">

            <div>

              <div className="text-[10px] uppercase tracking-[0.2em] text-slate-600">
                Parallel Engine
              </div>

              <div className="mt-1 text-sm font-medium">
                Verification Investigation
              </div>

            </div>

            <div className="flex items-center gap-2 text-[9px] uppercase tracking-wider text-amber-300">

              <span className="h-2 w-2 animate-pulse rounded-full bg-amber-300" />

              {demoRunning
                ? "Investigating"
                : "Ready"}

            </div>

          </div>


          <div className="p-5">

            <div className="border border-amber-400/15 bg-amber-400/[0.025] p-4">

              <div className="flex gap-3">

                <div className="flex h-8 w-8 shrink-0 items-center justify-center border border-amber-400/20 text-amber-300">
                  !
                </div>

                <div>

                  <div className="text-[10px] uppercase tracking-[0.18em] text-amber-300">
                    Contradiction Detected
                  </div>

                  <div className="mt-1 font-mono text-sm text-slate-300">
                    CAM_02 → KA01A8134
                  </div>

                  <div className="mt-1 text-xs text-slate-600">
                    Expected plate based on trajectory evidence:
                    KA01AB1234
                  </div>

                </div>

              </div>

            </div>


            {/* Checks */}

            <div className="mt-5 space-y-3">

              {[
                ["OCR confidence", "61% < 75%", true],
                ["Plate disagreement", "CAM_01 / CAM_03", true],
                ["Vehicle appearance", "Re-ID 91%", true],
                ["Temporal feasibility", "Consistent", true],
                ["Evidence agreement", "2 cameras", true],
              ].map(([label, value, passed], index) => {

                const visible = demoRunning
                  ? demoStep >= index + 1
                  : events.length > 0

                return (
                  <div
                    key={label}
                    className={`flex items-center justify-between border-b border-white/5 pb-3 transition-opacity ${
                      visible
                        ? "opacity-100"
                        : "opacity-35"
                    }`}
                  >

                    <div className="flex items-center gap-3">

                      <span
                        className={`flex h-5 w-5 items-center justify-center border text-[9px] ${
                          visible
                            ? "border-cyan-400/20 bg-cyan-400/5 text-cyan-300"
                            : "border-white/5 text-slate-700"
                        }`}
                      >
                        {visible ? "✓" : "·"}
                      </span>

                      <span className="text-xs text-slate-400">
                        {label}
                      </span>

                    </div>

                    <span
                      className={`font-mono text-[10px] ${
                        visible
                          ? "text-cyan-300"
                          : "text-slate-700"
                      }`}
                    >
                      {visible
                        ? value
                        : "WAITING"}
                    </span>

                  </div>
                )
              })}

            </div>


            {/* Evidence search */}

            <div className="mt-6">

              <div className="mb-3 text-[9px] uppercase tracking-[0.2em] text-slate-600">
                Evidence Search
              </div>

              <div className="space-y-2">

                <EvidenceRow
                  camera="CAM_01"
                  time="14:31:52"
                  plate="KA01AB1234"
                  status="SUPPORT"
                  visible={
                    !demoRunning ||
                    demoStep >= 5
                  }
                />

                <EvidenceRow
                  camera="CAM_03"
                  time="14:32:44"
                  plate="KA01AB1234"
                  status="SUPPORT"
                  visible={
                    !demoRunning ||
                    demoStep >= 5
                  }
                />

                <div className="flex items-center justify-between border border-dashed border-white/5 px-3 py-3">

                  <div className="text-xs text-slate-600">
                    Temporal search window
                  </div>

                  <div className="font-mono text-[10px] text-slate-500">
                    ±10 SEC
                  </div>

                </div>

              </div>

            </div>

          </div>

        </div>


        {/* =======================================================
            CORRECTION / PROPAGATION
        ======================================================= */}

        <div className="space-y-6">


          {/* Correction */}

          <div className="veytra-panel overflow-hidden">

            <div className="border-b border-cyan-400/10 px-5 py-4">

              <div className="text-[10px] uppercase tracking-[0.2em] text-slate-600">
                Verified Correction
              </div>

              <div className="mt-1 text-sm font-medium">
                Evidence-backed decision
              </div>

            </div>


            <div className="p-5">

              <div className="flex items-center justify-between gap-4">

                <div>

                  <div className="text-[9px] uppercase tracking-wider text-slate-600">
                    Original OCR
                  </div>

                  <div className="mt-2 font-mono text-xl text-slate-400">
                    KA01A8134
                  </div>

                </div>

                <div className="text-xl text-cyan-500/50">
                  →
                </div>

                <div>

                  <div className="text-[9px] uppercase tracking-wider text-slate-600">
                    Verified
                  </div>

                  <div className="mt-2 font-mono text-xl text-cyan-300">
                    KA01AB1234
                  </div>

                </div>

              </div>


              <div className="mt-6 grid grid-cols-2 gap-3">

                <Metric
                  label="Confidence"
                  value="91%"
                />

                <Metric
                  label="Re-ID"
                  value="91%"
                />

                <Metric
                  label="Evidence"
                  value="2 CAMS"
                />

                <Metric
                  label="Status"
                  value={
                    demoRunning
                      ? "RESOLVED"
                      : "STANDBY"
                  }
                />

              </div>


              <div className="mt-5 border border-cyan-400/10 bg-cyan-400/[0.025] p-4">

                <div className="text-[9px] uppercase tracking-[0.18em] text-cyan-400">
                  Decision
                </div>

                <p className="mt-2 text-xs leading-5 text-slate-400">
                  Supporting camera observations agree on the corrected
                  plate and vehicle appearance is consistent.
                </p>

              </div>

            </div>

          </div>


          {/* Trajectory propagation */}

          <div className="veytra-panel overflow-hidden">

            <div className="border-b border-cyan-400/10 px-5 py-4">

              <div className="text-[10px] uppercase tracking-[0.2em] text-slate-600">
                Intelligence Propagation
              </div>

              <div className="mt-1 text-sm font-medium">
                Trajectory updated
              </div>

            </div>


            <div className="p-5">

              <div className="relative pl-7">

                <div className="absolute bottom-3 left-[7px] top-3 w-px bg-cyan-400/15" />

                {[
                  [
                    "CAM_01",
                    "KA01AB1234",
                    "14:31:52",
                    "verified",
                  ],
                  [
                    "CAM_02",
                    "KA01AB1234",
                    "14:32:18",
                    "corrected",
                  ],
                  [
                    "CAM_03",
                    "KA01AB1234",
                    "14:32:44",
                    "verified",
                  ],
                ].map(
                  ([camera, plate, time, status]) => (

                    <div
                      key={camera}
                      className="relative mb-5 last:mb-0"
                    >

                      <div
                        className={`absolute -left-7 top-1 h-[15px] w-[15px] rounded-full border-2 bg-[#02070b] ${
                          status === "corrected"
                            ? "border-amber-400"
                            : "border-cyan-400"
                        }`}
                      />

                      <div className="flex items-center justify-between">

                        <div>

                          <div className="font-mono text-xs text-slate-300">
                            {camera}
                          </div>

                          <div className="mt-1 font-mono text-[10px] text-cyan-300">
                            {plate}
                          </div>

                        </div>

                        <div className="text-right">

                          <div className="font-mono text-[10px] text-slate-600">
                            {time}
                          </div>

                          <div
                            className={`mt-1 text-[8px] uppercase tracking-wider ${
                              status === "corrected"
                                ? "text-amber-300"
                                : "text-cyan-300"
                            }`}
                          >
                            {status}
                          </div>

                        </div>

                      </div>

                    </div>

                  )
                )}

              </div>


              <div className="mt-6 flex items-center gap-2 border-t border-white/5 pt-4 text-[9px] uppercase tracking-[0.16em] text-cyan-300">

                <span>✓</span>

                Main intelligence updated without pipeline interruption

              </div>

            </div>

          </div>

        </div>

      </div>


      {/* =========================================================
          REAL BACKEND EVENTS
      ========================================================= */}

      {!demoRunning && events.length > 0 && (

        <section className="mt-8">

          <div className="mb-3 flex items-center justify-between">

            <div>

              <div className="text-[10px] uppercase tracking-[0.22em] text-slate-600">
                Backend Results
              </div>

              <h2 className="mt-1 text-lg font-medium">
                Verification Events
              </h2>

            </div>

            <button
              onClick={loadEvents}
              className="text-[10px] uppercase tracking-wider text-cyan-400 hover:text-cyan-300"
            >
              Refresh
            </button>

          </div>


          <div className="space-y-3">

            {events.map((event, index) => {

              const original =
                event.original_plate ||
                event.plate ||
                "UNKNOWN"

              const corrected =
                event.corrected_plate ||
                original

              const confidence =
                event.verification_confidence ??
                event.confidence

              const cameras =
                event.supporting_cameras || []

              const changed =
                original !== corrected

              return (

                <div
                  key={
                    event.event_id ||
                    index
                  }
                  className="veytra-panel p-5"
                >

                  <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">

                    <div>

                      <div className="text-[9px] uppercase tracking-wider text-slate-600">
                        {event.event_id ||
                          `EVENT-${index + 1}`}
                      </div>

                      <div className="mt-2 flex items-center gap-3 font-mono">

                        <span className="text-slate-400">
                          {original}
                        </span>

                        {changed && (
                          <>
                            <span className="text-cyan-500/50">
                              →
                            </span>

                            <span className="text-cyan-300">
                              {corrected}
                            </span>
                          </>
                        )}

                      </div>

                    </div>


                    <div className="flex flex-wrap items-center gap-3">

                      <span className="border border-cyan-400/10 bg-cyan-400/5 px-3 py-2 text-[9px] uppercase tracking-wider text-cyan-300">
                        {confidence !==
                        undefined
                          ? `${(
                              Number(confidence) *
                              100
                            ).toFixed(1)}% confidence`
                          : "Verified"}
                      </span>

                      {cameras.map(
                        (camera) => (

                          <span
                            key={camera}
                            className="font-mono text-[9px] text-slate-500"
                          >
                            {camera}
                          </span>

                        )
                      )}

                      {event.source && (
                        <SourceBadge
                          source={event.source}
                        />
                      )}

                    </div>

                  </div>


                  {event.reason && (

                    <div className="mt-4 border-t border-white/5 pt-3 text-xs text-slate-500">
                      {event.reason}
                    </div>

                  )}

                </div>

              )
            })}

          </div>

        </section>
      )}


      {/* =========================================================
          EMPTY BACKEND STATE
      ========================================================= */}

      {!loading &&
        !demoRunning &&
        events.length === 0 && (

          <div className="mt-8 border border-white/5 bg-white/[0.01] p-5">

            <div className="flex items-center justify-between">

              <div>

                <div className="text-[9px] uppercase tracking-[0.2em] text-slate-600">
                  Backend Verification Store
                </div>

                <div className="mt-1 text-xs text-slate-500">
                  No live verification events returned.
                </div>

              </div>

              <div className="font-mono text-[9px] text-slate-700">
                0 EVENTS
              </div>

            </div>

          </div>
        )}


      {/* =========================================================
          ERROR
      ========================================================= */}

      {error && (

        <div className="mt-6 border border-red-400/20 bg-red-400/5 px-5 py-4 text-xs text-red-300">
          {error}
        </div>

      )}


      {/* =========================================================
          FOOTER
      ========================================================= */}

      <div className="mt-10 flex flex-col gap-2 border-t border-cyan-400/10 pt-4 text-[9px] uppercase tracking-[0.18em] text-slate-700 md:flex-row md:items-center md:justify-between">

        <span>
          VEYTRA / Parallel Intelligence Assurance
        </span>

        <span>
          OCR • Re-ID • Temporal Evidence • Provenance
        </span>

      </div>

    </div>
  )
}


/* ===============================================================
   SMALL COMPONENTS
   =============================================================== */

function EvidenceRow({
  camera,
  time,
  plate,
  status,
  visible,
}) {
  return (
    <div
      className={`flex items-center justify-between border border-cyan-400/10 bg-cyan-400/[0.02] px-3 py-3 transition-all ${
        visible
          ? "opacity-100"
          : "opacity-30"
      }`}
    >

      <div className="flex items-center gap-3">

        <span className="flex h-6 w-6 items-center justify-center border border-cyan-400/10 text-[9px] text-cyan-300">
          ✓
        </span>

        <div>

          <div className="font-mono text-[10px] text-slate-400">
            {camera}
          </div>

          <div className="mt-1 text-[9px] text-slate-600">
            {time}
          </div>

        </div>

      </div>

      <div className="text-right">

        <div className="font-mono text-xs text-cyan-300">
          {plate}
        </div>

        <div className="mt-1 text-[8px] uppercase tracking-wider text-cyan-500/70">
          {status}
        </div>

      </div>

    </div>
  )
}


function Metric({ label, value }) {
  return (
    <div className="border border-white/5 bg-white/[0.01] px-3 py-3">

      <div className="text-[8px] uppercase tracking-wider text-slate-600">
        {label}
      </div>

      <div className="mt-1 font-mono text-xs text-cyan-300">
        {value}
      </div>

    </div>
  )
}


export default SmartVerification