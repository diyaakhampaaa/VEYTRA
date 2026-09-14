import { useEffect, useMemo, useState } from "react"
import SourceBadge from "../components/SourceBadge"
import { getAnalytics } from "../api/client"


/* =========================================================
   BENGALURU HEATMAP AREAS
========================================================= */

const BENGALURU_AREAS = [
  {
    id: "yelahanka",
    name: "Yelahanka",
    x: 390,
    y: 105,
    shape:
      "M320 70 L405 58 L465 82 L470 135 L425 165 L350 155 L310 120 Z",
  },

  {
    id: "hebbal",
    name: "Hebbal",
    x: 445,
    y: 175,
    shape:
      "M380 150 L455 140 L505 170 L500 220 L455 235 L395 215 Z",
  },

  {
    id: "malleshwaram",
    name: "Malleshwaram",
    x: 345,
    y: 245,
    shape:
      "M275 205 L350 210 L385 245 L365 290 L300 290 L265 255 Z",
  },

  {
    id: "rajajinagar",
    name: "Rajajinagar",
    x: 315,
    y: 325,
    shape:
      "M235 285 L315 285 L355 315 L340 370 L265 375 L220 335 Z",
  },

  {
    id: "mg-road",
    name: "MG Road",
    x: 475,
    y: 305,
    shape:
      "M405 255 L480 245 L535 275 L525 325 L475 350 L415 330 Z",
  },

  {
    id: "indiranagar",
    name: "Indiranagar",
    x: 585,
    y: 315,
    shape:
      "M525 255 L605 245 L655 280 L650 335 L595 360 L535 340 Z",
  },

  {
    id: "koramangala",
    name: "Koramangala",
    x: 515,
    y: 410,
    shape:
      "M435 350 L520 345 L570 390 L555 445 L475 455 L425 410 Z",
  },

  {
    id: "jayanagar",
    name: "Jayanagar",
    x: 365,
    y: 440,
    shape:
      "M285 380 L370 375 L420 420 L405 480 L325 495 L275 450 Z",
  },

  {
    id: "hsr",
    name: "HSR Layout",
    x: 535,
    y: 495,
    shape:
      "M460 450 L545 450 L590 490 L575 540 L500 555 L450 520 Z",
  },

  {
    id: "marathahalli",
    name: "Marathahalli",
    x: 700,
    y: 370,
    shape:
      "M630 315 L720 300 L775 345 L765 400 L710 425 L645 395 Z",
  },

  {
    id: "whitefield",
    name: "Whitefield",
    x: 790,
    y: 285,
    shape:
      "M735 215 L820 195 L875 235 L865 300 L810 330 L750 300 Z",
  },

  {
    id: "electronic-city",
    name: "Electronic City",
    x: 610,
    y: 615,
    shape:
      "M525 550 L620 540 L690 575 L680 640 L605 665 L535 635 Z",
  },

  {
    id: "banashankari",
    name: "Banashankari",
    x: 290,
    y: 525,
    shape:
      "M205 455 L300 460 L350 510 L330 570 L250 580 L200 525 Z",
  },

  {
    id: "jp-nagar",
    name: "JP Nagar",
    x: 385,
    y: 560,
    shape:
      "M320 495 L400 500 L450 545 L430 600 L355 615 L305 565 Z",
  },

  {
    id: "kr-puram",
    name: "KR Puram",
    x: 690,
    y: 245,
    shape:
      "M625 190 L705 180 L750 215 L740 270 L690 295 L635 260 Z",
  },
]


/*
 * Existing backend segment IDs are projected onto the
 * Bengaluru visual traffic model.
 *
 * This keeps the backend analytics untouched while allowing
 * the dashboard to visualize congestion over Bengaluru areas.
 */
const AREA_SEGMENT_MAP = {
  "mg-road": "SEG_B2",
  indiranagar: "SEG_A1",
  marathahalli: "SEG_C3",
}


/* =========================================================
   COMPONENT
========================================================= */

function TrafficAnalytics() {

  const [segments, setSegments] = useState([])
  const [summary, setSummary] = useState({})
  const [bottleneckData, setBottleneckData] = useState([])
  const [movementFlows, setMovementFlows] = useState([])
  const [source, setSource] = useState(null)

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)

  const [selectedSegment, setSelectedSegment] =
    useState(null)

  const [hoveredArea, setHoveredArea] =
    useState(null)


  /* =========================================================
     LOAD ANALYTICS
  ========================================================= */

  useEffect(() => {

    getAnalytics()

      .then((data) => {

        setSegments(
          Array.isArray(data?.segments)
            ? data.segments
            : []
        )

        setSummary(
          data?.summary || {}
        )

        setBottleneckData(
          Array.isArray(data?.bottlenecks)
            ? data.bottlenecks
            : []
        )


        const normalizedFlows =
          Array.isArray(
            data?.movement_flows
          )
            ? data.movement_flows.map(
                (flow) => ({
                  origin:
                    flow?.origin ||
                    flow?.origin_camera_id ||
                    flow?.origin_segment_id ||
                    "Unknown",

                  destination:
                    flow?.destination ||
                    flow?.destination_camera_id ||
                    flow?.destination_segment_id ||
                    "Unknown",

                  vehicles: Number(
                    flow?.vehicles ??
                    flow?.vehicle_count ??
                    flow?.count ??
                    0
                  ),

                  originSegment:
                    flow?.origin_segment_id ||
                    null,

                  destinationSegment:
                    flow?.destination_segment_id ||
                    null,
                })
              )
            : []


        setMovementFlows(
          normalizedFlows.sort(
            (a, b) =>
              b.vehicles - a.vehicles
          )
        )

        setSource(
          data?.source || null
        )
      })

      .catch((error) => {

        console.error(
          "🔥 VEYTRA ANALYTICS ERROR:",
          error
        )

        setError(true)
      })

      .finally(() => {

        setLoading(false)

      })

  }, [])


  /* =========================================================
     NETWORK METRICS
  ========================================================= */

  const totalVehicles = useMemo(() => {

    return Number(
      summary?.total_vehicles ?? 0
    )

  }, [summary])


  const averageSpeed = useMemo(() => {

    if (
      summary?.average_speed_kmh !==
        undefined &&
      summary?.average_speed_kmh !==
        null
    ) {

      return Number(
        summary.average_speed_kmh
      )

    }

    if (!segments.length)
      return 0

    const validSegments =
      segments.filter(
        (segment) =>
          segment.average_speed !==
            null &&
          segment.average_speed !==
            undefined &&
          Number.isFinite(
            Number(
              segment.average_speed
            )
          )
      )

    if (!validSegments.length)
      return 0

    return (
      validSegments.reduce(
        (total, segment) =>
          total +
          Number(
            segment.average_speed
          ),
        0
      ) /
      validSegments.length
    )

  }, [summary, segments])


  const averageCongestion =
    useMemo(() => {

      if (
        summary?.average_congestion !==
          undefined &&
        summary?.average_congestion !==
          null
      ) {

        return Number(
          summary.average_congestion
        )

      }

      if (!segments.length)
        return 0

      return (
        segments.reduce(
          (total, segment) =>
            total +
            Number(
              segment.congestion_score ||
                0
            ),
          0
        ) /
        segments.length
      )

    }, [summary, segments])


  const severeSegments = useMemo(
    () =>
      segments.filter(
        (segment) =>
          Number(
            segment.congestion_score ||
              0
          ) >= 0.7
      ),
    [segments]
  )


  const highCongestionSegments =
    useMemo(
      () =>
        segments.filter(
          (segment) =>
            Number(
              segment.congestion_score ||
                0
            ) >= 0.4
        ),
      [segments]
    )


  const activeBottleneckCount =
    useMemo(() => {

      if (
        summary?.bottleneck_count !==
          undefined &&
        summary?.bottleneck_count !==
          null
      ) {

        return Number(
          summary.bottleneck_count
        )

      }

      return bottleneckData.filter(
        (bottleneck) =>
          bottleneck?.is_bottleneck ===
          true
      ).length

    }, [
      summary,
      bottleneckData,
    ])


  /* =========================================================
     HELPERS
  ========================================================= */

  const getCongestionLabel = (
    score
  ) => {

    if (score >= 0.7)
      return "SEVERE"

    if (score >= 0.4)
      return "HIGH"

    if (score >= 0.2)
      return "MODERATE"

    return "LOW"
  }


  const getCongestionStyle = (
    score
  ) => {

    if (score >= 0.7) {

      return "border-red-400/20 bg-red-400/5 text-red-300"

    }

    if (score >= 0.4) {

      return "border-amber-400/20 bg-amber-400/5 text-amber-300"

    }

    if (score >= 0.2) {

      return "border-cyan-400/20 bg-cyan-400/5 text-cyan-300"

    }

    return "border-slate-500/20 bg-slate-500/5 text-slate-400"

  }


  /*
   * NOAA-style heat colors.
   *
   * Dark red -> red -> orange -> yellow -> white.
   */
  const getHeatColor = (
    score
  ) => {

    if (score >= 0.85)
      return "#ffffff"

    if (score >= 0.7)
      return "#ff2020"

    if (score >= 0.55)
      return "#ff4d00"

    if (score >= 0.4)
      return "#ff9900"

    if (score >= 0.2)
      return "#ffd900"

    return "#8f0000"
  }


  /* =========================================================
     BENGALURU HEAT DATA
  ========================================================= */

  const heatmapSegments =
    useMemo(() => {

      const validSegments =
        segments.filter(
          (segment) =>
            Number.isFinite(
              Number(
                segment.congestion_score
              )
            )
        )

      return validSegments.map(
        (segment) => ({

          ...segment,

          heatScore: Math.max(
            0,
            Math.min(
              1,
              Number(
                segment.congestion_score ||
                  0
              )
            )
          ),

        })
      )

    }, [segments])


  /*
   * Convert backend segment scores into
   * Bengaluru area intensity.
   */
  const areaHeat = useMemo(() => {

    const scores = {}

    BENGALURU_AREAS.forEach(
      (area) => {
        scores[area.id] = 0
      }
    )


    heatmapSegments.forEach(
      (segment, index) => {

        const mappedArea =
          Object.keys(
            AREA_SEGMENT_MAP
          ).find(
            (areaId) =>
              AREA_SEGMENT_MAP[
                areaId
              ] ===
              segment.segment_id
          )


        if (mappedArea) {

          scores[mappedArea] =
            Math.max(
              scores[mappedArea] ||
                0,
              Number(
                segment.heatScore ||
                  0
              )
            )

        } else {

          /*
           * If a new segment appears,
           * distribute it deterministically
           * rather than breaking the map.
           */
          const fallbackArea =
            BENGALURU_AREAS[
              index %
                BENGALURU_AREAS.length
            ]

          scores[
            fallbackArea.id
          ] =
            Math.max(
              scores[
                fallbackArea.id
              ] || 0,
              Number(
                segment.heatScore ||
                  0
              )
            )

        }

      }
    )

    return scores

  }, [heatmapSegments])


  /* =========================================================
     BOTTLENECK INTELLIGENCE
  ========================================================= */

  const bottlenecks = useMemo(() => {

    return bottleneckData

      .map((bottleneck) => {

        const score =
          Number(
            bottleneck?.congestion_score ??
            bottleneck?.mean_congestion_score ??
            bottleneck?.average_congestion_score ??
            0
          )

        return {

          ...bottleneck,

          segment_id:
            bottleneck?.segment_id ||
            bottleneck?.road_segment_id ||
            "Unknown",

          road_name:
            bottleneck?.road_name ||
            "",

          congestion_score:
            score,

          is_bottleneck:
            bottleneck?.is_bottleneck ===
            true,

        }

      })

      .sort(
        (a, b) =>
          Number(
            b.congestion_score ||
              0
          ) -
          Number(
            a.congestion_score ||
              0
          )
      )

      .slice(0, 5)

  }, [bottleneckData])


  /* =========================================================
     FLOW DISTRIBUTION
  ========================================================= */

  const maxVehicles =
    useMemo(() => {

      if (!segments.length)
        return 1

      return Math.max(
        ...segments.map(
          (segment) =>
            Number(
              segment.vehicle_count ||
                0
            )
        ),
        1
      )

    }, [segments])


  const topFlowSegments =
    useMemo(() => {

      return [...segments]
        .sort(
          (a, b) =>
            Number(
              b.vehicle_count ||
                0
            ) -
            Number(
              a.vehicle_count ||
                0
            )
        )
        .slice(0, 5)

    }, [segments])


  /* =========================================================
     LOADING
  ========================================================= */

  if (loading) {

    return (

      <div className="min-h-screen bg-[#02070b] text-white">

        <div className="mb-8">

          <div className="mb-2 flex items-center gap-2 text-xs uppercase tracking-[0.28em] text-cyan-400">

            <span className="veytra-live-dot" />

            Traffic Intelligence

          </div>


          <h1 className="text-3xl font-semibold tracking-tight">

            Traffic Analytics

          </h1>


          <p className="mt-2 text-sm text-slate-400">

            Converting vehicle observations into city-wide movement intelligence.

          </p>

        </div>


        <div className="veytra-panel veytra-hud flex min-h-[300px] items-center justify-center">

          <div className="text-sm text-slate-500">

            Loading traffic intelligence...

          </div>

        </div>

      </div>

    )

  }


  /* =========================================================
     ERROR
  ========================================================= */

  if (error) {

    return (

      <div className="min-h-screen bg-[#02070b] text-white">

        <div className="flex items-end justify-between">

          <div>

            <div className="mb-2 flex items-center gap-2 text-xs uppercase tracking-[0.28em] text-cyan-400">

              <span className="veytra-warning-dot" />

              Traffic Intelligence

            </div>


            <h1 className="text-3xl font-semibold tracking-tight">

              Traffic Analytics

            </h1>


            <p className="mt-2 text-sm text-slate-400">

              City-wide traffic flow and congestion analysis.

            </p>

          </div>


          <SourceBadge source="simulated" />

        </div>


        <div className="veytra-panel veytra-hud mt-8 p-8">

          <div className="flex items-start gap-4">

            <div className="flex h-10 w-10 items-center justify-center border border-amber-400/20 bg-amber-400/5 text-amber-300">

              !

            </div>


            <div>

              <h2 className="text-lg font-medium">

                Analytics service unavailable

              </h2>


              <p className="mt-2 text-sm text-slate-500">

                Traffic analytics could not be retrieved.
                Make sure the backend is running and the
                analytics endpoint is available.

              </p>

            </div>

          </div>

        </div>

      </div>

    )

  }


  /* =========================================================
     MAIN
  ========================================================= */

  return (

    <div className="min-h-screen bg-[#02070b] text-white">


      {/* =====================================================
          HEADER
      ===================================================== */}

      <div className="flex flex-col gap-5 border-b border-cyan-400/10 pb-6 lg:flex-row lg:items-end lg:justify-between">

        <div>

          <div className="mb-2 flex items-center gap-2 text-xs uppercase tracking-[0.28em] text-cyan-400">

            <span className="veytra-live-dot" />

            Traffic Intelligence

          </div>


          <h1 className="text-3xl font-semibold tracking-tight">

            Traffic Analytics

          </h1>


          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">

            City-wide analysis of vehicle flow, movement density,
            average speed, congestion, and network bottlenecks.

          </p>

        </div>


        <div className="flex items-center gap-3">

          <div className="veytra-panel px-4 py-3">

            <div className="mb-1 text-[9px] uppercase tracking-[0.22em] text-slate-600">

              Intelligence State

            </div>


            <div className="flex items-center gap-2 text-xs text-cyan-300">

              <span className="veytra-live-dot" />

              OPERATIONAL

            </div>

          </div>


          <div className="veytra-panel px-4 py-3">

            <div className="mb-1 text-[9px] uppercase tracking-[0.22em] text-slate-600">

              Data Source

            </div>

            <SourceBadge source="simulated" />

          </div>

        </div>

      </div>


      {/* =====================================================
          NETWORK OVERVIEW
      ===================================================== */}

      <div className="mt-8">

        <div className="mb-4">

          <div className="mb-1 text-[10px] uppercase tracking-[0.22em] text-cyan-500/60">

            Network State

          </div>


          <h2 className="text-lg font-medium">

            City Traffic Overview

          </h2>


          <p className="mt-1 text-sm text-slate-500">

            Current traffic conditions reconstructed from monitored vehicle observations.

          </p>

        </div>


        <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-4">


          {/* VEHICLES */}

          <div className="veytra-panel veytra-panel-hover veytra-hud p-5">

            <div className="flex items-start justify-between">

              <div className="text-[10px] uppercase tracking-[0.2em] text-slate-500">

                Vehicles Observed

              </div>

              <span className="h-2 w-2 rounded-full bg-cyan-400 shadow-[0_0_10px_rgba(34,211,238,0.6)]" />

            </div>


            <div className="mt-4 font-mono text-3xl font-semibold">

              {totalVehicles.toLocaleString()}

            </div>


            <div className="mt-2 text-xs text-slate-600">

              Unique vehicles observed

            </div>

          </div>


          {/* SPEED */}

          <div className="veytra-panel veytra-panel-hover veytra-hud p-5">

            <div className="flex items-start justify-between">

              <div className="text-[10px] uppercase tracking-[0.2em] text-slate-500">

                Average Speed

              </div>

              <span className="h-2 w-2 rounded-full bg-cyan-400 shadow-[0_0_10px_rgba(34,211,238,0.6)]" />

            </div>


            <div className="mt-4 font-mono text-3xl font-semibold">

              {averageSpeed.toFixed(1)}

              <span className="ml-2 text-sm font-normal text-slate-500">

                km/h

              </span>

            </div>


            <div className="mt-2 text-xs text-slate-600">

              Network-wide mean speed

            </div>

          </div>


          {/* CONGESTION */}

          <div className="veytra-panel veytra-panel-hover veytra-hud p-5">

            <div className="flex items-start justify-between">

              <div className="text-[10px] uppercase tracking-[0.2em] text-slate-500">

                Network Congestion

              </div>


              <span
                className="h-2 w-2 rounded-full"
                style={{
                  background:
                    getHeatColor(
                      averageCongestion
                    ),
                  boxShadow:
                    `0 0 10px ${getHeatColor(
                      averageCongestion
                    )}`,
                }}
              />

            </div>


            <div className="mt-4 font-mono text-3xl font-semibold">

              {Math.round(
                averageCongestion * 100
              )}

              <span className="ml-1 text-sm font-normal text-slate-500">

                %

              </span>

            </div>


            <div className="mt-2 text-xs text-slate-600">

              {getCongestionLabel(
                averageCongestion
              )}

              {" "}network condition

            </div>

          </div>


          {/* BOTTLENECKS */}

          <div className="veytra-panel veytra-panel-hover veytra-hud p-5">

            <div className="flex items-start justify-between">

              <div className="text-[10px] uppercase tracking-[0.2em] text-slate-500">

                Bottlenecks

              </div>


              <span
                className={`h-2 w-2 rounded-full ${
                  activeBottleneckCount > 0
                    ? "bg-red-400 shadow-[0_0_10px_rgba(248,113,113,0.6)]"
                    : "bg-cyan-400"
                }`}
              />

            </div>


            <div className="mt-4 font-mono text-3xl font-semibold">

              {activeBottleneckCount
                .toString()
                .padStart(2, "0")}

            </div>


            <div className="mt-2 text-xs text-slate-600">

              Active bottlenecks detected

            </div>

          </div>

        </div>

      </div>


      {/* =====================================================
          BENGALURU TRAFFIC HEATMAP
      ===================================================== */}

      <div className="mt-10">


        <div className="mb-4 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">

          <div>

            <div className="mb-1 text-[10px] uppercase tracking-[0.22em] text-red-400/70">

              Spatial Intelligence

            </div>


            <h2 className="text-lg font-medium">

              Bengaluru Traffic Heatmap

            </h2>


            <p className="mt-1 max-w-2xl text-sm text-slate-500">

              City-wide congestion intensity visualized across major Bengaluru traffic corridors.

            </p>

          </div>


          {/* NOAA STYLE LEGEND */}

          <div className="flex flex-wrap items-center gap-4 text-[9px] uppercase tracking-[0.15em] text-slate-500">

            <div className="flex items-center gap-2">

              <span className="h-2 w-2 rounded-sm bg-[#8f0000]" />

              Low

            </div>


            <div className="flex items-center gap-2">

              <span className="h-2 w-2 rounded-sm bg-[#ffd900]" />

              Moderate

            </div>


            <div className="flex items-center gap-2">

              <span className="h-2 w-2 rounded-sm bg-[#ff9900]" />

              High

            </div>


            <div className="flex items-center gap-2">

              <span className="h-2 w-2 rounded-sm bg-[#ff2020]" />

              Severe

            </div>


            <div className="flex items-center gap-2">

              <span className="h-2 w-2 rounded-sm bg-white" />

              Critical

            </div>

          </div>

        </div>


        {/* =====================================================
            MAP
        ===================================================== */}

        <div
          className="relative min-h-[620px] overflow-hidden rounded-2xl border border-white/10"
          style={{
            background:
              "#020202",
          }}
        >


          {/* SUBTLE ATMOSPHERIC BACKGROUND */}

          <div
            className="pointer-events-none absolute inset-0"
            style={{
              background:
                "radial-gradient(circle at 50% 45%, rgba(255,30,0,0.06), transparent 58%)",
            }}
          />


          {/* HEADER */}

          <div className="absolute left-6 top-5 z-30 font-mono text-[9px] uppercase tracking-[0.2em] text-white/45">

            VEYTRA / BENGALURU TRAFFIC FIELD

          </div>


          <div className="absolute right-6 top-5 z-30 font-mono text-[9px] uppercase tracking-[0.18em] text-white/35">

            LIVE SPATIAL MODEL

          </div>


          {/* =================================================
              ACTUAL MAP CANVAS
          ================================================= */}

          <div className="absolute inset-x-4 bottom-14 top-14">

            <svg
              viewBox="0 0 900 700"
              className="h-full w-full"
              preserveAspectRatio="xMidYMid meet"
            >


              <defs>


                {/* =================================================
                    PIXEL HEAT GRADIENTS
                ================================================= */}

                <linearGradient
                  id="heatRed"
                  x1="0"
                  y1="0"
                  x2="1"
                  y2="1"
                >
                  <stop
                    offset="0%"
                    stopColor="#ff0000"
                    stopOpacity="0.9"
                  />

                  <stop
                    offset="100%"
                    stopColor="#660000"
                    stopOpacity="0"
                  />
                </linearGradient>


                <radialGradient
                  id="heatYellow"
                >

                  <stop
                    offset="0%"
                    stopColor="#ffffff"
                    stopOpacity="0.95"
                  />

                  <stop
                    offset="25%"
                    stopColor="#ffff00"
                    stopOpacity="0.95"
                  />

                  <stop
                    offset="55%"
                    stopColor="#ff9900"
                    stopOpacity="0.75"
                  />

                  <stop
                    offset="100%"
                    stopColor="#ff0000"
                    stopOpacity="0"
                  />

                </radialGradient>


                <radialGradient
                  id="heatOrange"
                >

                  <stop
                    offset="0%"
                    stopColor="#ffff00"
                    stopOpacity="0.85"
                  />

                  <stop
                    offset="45%"
                    stopColor="#ff6600"
                    stopOpacity="0.75"
                  />

                  <stop
                    offset="100%"
                    stopColor="#ff0000"
                    stopOpacity="0"
                  />

                </radialGradient>


                <filter
                  id="heatBlur"
                  x="-100%"
                  y="-100%"
                  width="300%"
                  height="300%"
                >

                  <feGaussianBlur
                    stdDeviation="18"
                  />

                </filter>


                <filter
                  id="heatBlurLarge"
                  x="-100%"
                  y="-100%"
                  width="300%"
                  height="300%"
                >

                  <feGaussianBlur
                    stdDeviation="35"
                  />

                </filter>


              </defs>


              {/* =================================================
                  BENGALURU OUTER CITY BOUNDARY
              ================================================= */}

              <path
                d="
                  M 245 95
                  L 330 55
                  L 430 45
                  L 535 65
                  L 625 105
                  L 720 125
                  L 805 185
                  L 850 270
                  L 855 365
                  L 825 450
                  L 780 520
                  L 700 590
                  L 610 645
                  L 505 665
                  L 400 650
                  L 310 625
                  L 230 580
                  L 165 515
                  L 125 440
                  L 110 350
                  L 125 260
                  L 165 180
                  Z
                "
                fill="#030303"
                stroke="#eeeeee"
                strokeWidth="2"
                strokeOpacity="0.85"
              />


              {/* =================================================
                  MAJOR CITY ROADS
              ================================================= */}

              <g
                fill="none"
                stroke="#ffffff"
                strokeOpacity="0.28"
                strokeWidth="3"
              >

                {/* North → South */}

                <path d="M440 65 C430 170 425 270 415 370 C405 480 410 570 430 650" />

                {/* West → East */}

                <path d="M140 360 C280 345 410 330 540 325 C660 320 760 340 840 365" />

                {/* Northwest → Southeast */}

                <path d="M185 170 C300 245 410 315 515 405 C625 500 720 565 795 610" />

                {/* Northeast → Southwest */}

                <path d="M700 135 C625 220 560 305 490 395 C410 500 315 565 215 610" />

                {/* Outer Ring Road */}

                <path d="M245 180 C360 115 550 105 690 175 C785 225 805 390 745 500 C675 600 500 620 350 560 C220 510 190 330 245 180 Z" />

                {/* Inner ring */}

                <path d="M330 235 C410 180 535 180 625 235 C690 275 705 390 650 455 C580 525 435 520 350 455 C285 405 285 290 330 235 Z" />

              </g>


              {/* =================================================
                  ROAD CENTER LINES
              ================================================= */}

              <g
                fill="none"
                stroke="#ffffff"
                strokeOpacity="0.18"
                strokeWidth="1"
                strokeDasharray="6 8"
              >

                <path d="M440 65 C430 170 425 270 415 370 C405 480 410 570 430 650" />

                <path d="M140 360 C280 345 410 330 540 325 C660 320 760 340 840 365" />

                <path d="M185 170 C300 245 410 315 515 405 C625 500 720 565 795 610" />

                <path d="M700 135 C625 220 560 305 490 395 C410 500 315 565 215 610" />

              </g>


              {/* =================================================
                  PIXELATED HEAT FIELD
              ================================================= */}

              {BENGALURU_AREAS.map(
                (area) => {

                  const score =
                    Number(
                      areaHeat[
                        area.id
                      ] || 0
                    )

                  if (score <= 0)
                    return null

                  const size =
                    80 +
                    score * 100

                  const intensity =
                    0.28 +
                    score * 0.55

                  let gradient =
                    "url(#heatRed)"

                  if (
                    score >= 0.7
                  ) {

                    gradient =
                      "url(#heatYellow)"

                  } else if (
                    score >= 0.4
                  ) {

                    gradient =
                      "url(#heatOrange)"

                  }

                  return (

                    <g
                      key={`heat-${area.id}`}
                      pointerEvents="none"
                    >

                      <circle
                        cx={area.x}
                        cy={area.y}
                        r={size}
                        fill={gradient}
                        opacity={
                          intensity *
                          0.38
                        }
                        filter="url(#heatBlurLarge)"
                      />

                      <circle
                        cx={area.x}
                        cy={area.y}
                        r={size * 0.65}
                        fill={gradient}
                        opacity={
                          intensity
                        }
                        filter="url(#heatBlur)"
                      />

                      <circle
                        cx={area.x}
                        cy={area.y}
                        r={size * 0.28}
                        fill={gradient}
                        opacity="0.75"
                      />

                    </g>

                  )

                }
              )}


              {/* =================================================
                  PIXEL GRID HEAT CELLS
              ================================================= */}

              {Array.from(
                { length: 23 },
                (_, row) =>
                  Array.from(
                    { length: 29 },
                    (_, column) => {

                      const cellX =
                        130 +
                        column * 25

                      const cellY =
                        65 +
                        row * 25

                      let intensity =
                        0

                      BENGALURU_AREAS.forEach(
                        (area) => {

                          const score =
                            Number(
                              areaHeat[
                                area.id
                              ] || 0
                            )

                          if (
                            score <= 0
                          )
                            return

                          const dx =
                            cellX -
                            area.x

                          const dy =
                            cellY -
                            area.y

                          const distance =
                            Math.sqrt(
                              dx * dx +
                              dy * dy
                            )

                          const influence =
                            Math.max(
                              0,
                              1 -
                                distance /
                                  130
                            )

                          intensity =
                            Math.max(
                              intensity,
                              score *
                                influence
                            )

                        }
                      )


                      /*
                       * Small background
                       * thermal noise so the
                       * map resembles the
                       * reference image.
                       */

                      if (
                        intensity <
                        0.055
                      ) {

                        return null

                      }


                      let cellColor =
                        "#7f0000"


                      if (
                        intensity >=
                        0.82
                      ) {

                        cellColor =
                          "#ffffff"

                      } else if (
                        intensity >=
                        0.65
                      ) {

                        cellColor =
                          "#ff1a1a"

                      } else if (
                        intensity >=
                        0.48
                      ) {

                        cellColor =
                          "#ff5a00"

                      } else if (
                        intensity >=
                        0.30
                      ) {

                        cellColor =
                          "#ffb300"

                      } else if (
                        intensity >=
                        0.15
                      ) {

                        cellColor =
                          "#ffd900"

                      }


                      return (

                        <rect
                          key={`cell-${row}-${column}`}
                          x={cellX}
                          y={cellY}
                          width="23"
                          height="23"
                          fill={
                            cellColor
                          }
                          opacity={
                            0.15 +
                            intensity *
                              0.75
                          }
                        />

                      )

                    }
                  )
              )}


              {/* =================================================
                  AREA BOUNDARIES
              ================================================= */}

              {BENGALURU_AREAS.map(
                (area) => {

                  const score =
                    Number(
                      areaHeat[
                        area.id
                      ] || 0
                    )

                  const isHot =
                    score >= 0.4

                  return (

                    <path
                      key={`area-${area.id}`}
                      d={area.shape}
                      fill="transparent"
                      stroke={
                        isHot
                          ? "#ffffff"
                          : "#d7d7d7"
                      }
                      strokeWidth={
                        isHot
                          ? 2
                          : 1
                      }
                      strokeOpacity={
                        isHot
                          ? 0.7
                          : 0.32
                      }
                      className="cursor-pointer transition-all duration-200 hover:stroke-white hover:stroke-[2.5]"
                      onMouseEnter={() =>
                        setHoveredArea(
                          area.id
                        )
                      }
                      onMouseLeave={() =>
                        setHoveredArea(
                          null
                        )
                      }
                    />

                  )

                }
              )}


              {/* =================================================
                  AREA LABELS
              ================================================= */}

              {BENGALURU_AREAS.map(
                (area) => {

                  const score =
                    Number(
                      areaHeat[
                        area.id
                      ] || 0
                    )

                  const active =
                    hoveredArea ===
                    area.id

                  return (

                    <g
                      key={`label-${area.id}`}
                      pointerEvents="none"
                    >

                      <text
                        x={area.x}
                        y={area.y}
                        textAnchor="middle"
                        fill={
                          active
                            ? "#ffffff"
                            : "#ffffff"
                        }
                        fillOpacity={
                          active
                            ? 1
                            : 0.62
                        }
                        fontSize={
                          active
                            ? 13
                            : 10
                        }
                        fontFamily="monospace"
                        fontWeight={
                          active
                            ? "700"
                            : "500"
                        }
                      >

                        {area.name}

                      </text>


                      {score > 0 && (

                        <circle
                          cx={area.x}
                          cy={
                            area.y +
                            10
                          }
                          r="3"
                          fill={
                            getHeatColor(
                              score
                            )
                          }
                        />

                      )}

                    </g>

                  )

                }
              )}


              {/* =================================================
                  CITY TITLE
              ================================================= */}

              <text
                x="450"
                y="40"
                textAnchor="middle"
                fill="#ffffff"
                fillOpacity="0.8"
                fontSize="15"
                fontFamily="monospace"
                letterSpacing="5"
              >

                BENGALURU

              </text>

            </svg>


            {/* =================================================
                HOVER INFORMATION
            ================================================= */}

            {hoveredArea && (() => {

              const area =
                BENGALURU_AREAS.find(
                  (item) =>
                    item.id ===
                    hoveredArea
                )

              if (!area)
                return null

              const score =
                Number(
                  areaHeat[
                    area.id
                  ] || 0
                )

              return (

                <div
                  className="pointer-events-none absolute z-50 w-[210px] rounded-lg border border-white/20 bg-black/90 p-4 shadow-2xl backdrop-blur-xl"
                  style={{
                    left: `${Math.min(
                      Math.max(
                        (area.x /
                          900) *
                          100,
                        12
                      ),
                      76
                    )}%`,
                    top: `${Math.min(
                      Math.max(
                        (area.y /
                          700) *
                          100,
                        12
                      ),
                      70
                    )}%`,
                    transform:
                      "translate(-50%, -115%)",
                  }}
                >

                  <div className="text-[8px] uppercase tracking-[0.2em] text-white/40">

                    Bengaluru Area

                  </div>


                  <div className="mt-1 font-mono text-sm font-semibold text-white">

                    {area.name}

                  </div>


                  <div className="mt-3 flex items-end justify-between">

                    <div>

                      <div className="text-[8px] uppercase tracking-widest text-white/35">

                        Congestion

                      </div>

                      <div
                        className="mt-1 font-mono text-xl"
                        style={{
                          color:
                            getHeatColor(
                              score
                            ),
                        }}
                      >

                        {Math.round(
                          score *
                            100
                        )}

                        %

                      </div>

                    </div>


                    <div
                      className="text-[9px] uppercase tracking-widest"
                      style={{
                        color:
                          getHeatColor(
                            score
                          ),
                      }}
                    >

                      {getCongestionLabel(
                        score
                      )}

                    </div>

                  </div>


                  <div className="mt-3 h-1 overflow-hidden bg-white/10">

                    <div
                      className="h-full"
                      style={{
                        width: `${Math.min(
                          score *
                            100,
                          100
                        )}%`,
                        background:
                          getHeatColor(
                            score
                          ),
                      }}
                    />

                  </div>


                  <div className="mt-3 text-[8px] uppercase tracking-[0.15em] text-white/25">

                    Hover area for spatial intelligence

                  </div>

                </div>

              )

            })()}

          </div>


          {/* =================================================
              MAP FOOTER
          ================================================= */}

          <div className="absolute bottom-5 left-6 z-20 flex flex-wrap gap-x-6 gap-y-2 font-mono text-[8px] uppercase tracking-[0.16em] text-white/30">

            <span>
              BENGALURU SPATIAL MODEL
            </span>

            <span>
              HEAT INTENSITY 0.00 — 1.00
            </span>

            <span>
              HOVER AREA FOR DETAILS
            </span>

          </div>


          {/* NORTH */}

          <div className="absolute bottom-5 right-7 z-20 flex flex-col items-center">

            <span className="font-mono text-[9px] text-white/50">
              N
            </span>

            <span className="mt-1 h-7 w-px bg-white/20" />

            <span className="text-[8px] text-white/30">
              ↑
            </span>

          </div>

        </div>

      </div>


      {/* =====================================================
          BOTTLENECK INTELLIGENCE
      ===================================================== */}

      <div className="mt-10">

        <div className="mb-4">

          <div className="mb-1 text-[10px] uppercase tracking-[0.22em] text-cyan-500/60">

            Network Intelligence

          </div>


          <h2 className="text-lg font-medium">

            Bottleneck Intelligence

          </h2>


          <p className="mt-1 text-sm text-slate-500">

            Bottlenecks identified by the traffic analytics engine from repeated congestion conditions.

          </p>

        </div>


        <div className="veytra-panel veytra-hud overflow-hidden">

          {bottlenecks.length === 0 ? (

            <div className="p-8">

              <div className="text-sm text-slate-500">

                No active bottlenecks detected.

              </div>


              <div className="mt-2 text-xs text-slate-700">

                Current monitored conditions do not satisfy the bottleneck detection threshold.

              </div>

            </div>

          ) : (

            <div>

              {bottlenecks.map(
                (segment, index) => {

                  const congestion =
                    Math.round(
                      Number(
                        segment.congestion_score ||
                          0
                      ) * 100
                    )

                  const color =
                    getHeatColor(
                      Number(
                        segment.congestion_score ||
                          0
                      )
                    )

                  return (

                    <button
                      key={
                        segment.segment_id ||
                        index
                      }
                      type="button"
                      onClick={() =>
                        setSelectedSegment(
                          segment
                        )
                      }
                      className="group flex w-full items-center gap-5 border-b border-cyan-400/5 p-5 text-left transition hover:bg-cyan-400/[0.025] last:border-b-0"
                    >

                      <div className="font-mono text-xs text-slate-700">

                        {String(
                          index + 1
                        ).padStart(
                          2,
                          "0"
                        )}

                      </div>


                      <div className="min-w-0 flex-1">

                        <div className="flex items-center justify-between gap-4">

                          <div>

                            <div className="font-mono text-sm text-slate-300">

                              {segment.segment_id}

                            </div>


                            {segment.road_name && (

                              <div className="mt-1 text-xs text-slate-600">

                                {segment.road_name}

                              </div>

                            )}

                          </div>


                          <div
                            className="font-mono text-sm"
                            style={{
                              color,
                            }}
                          >

                            {congestion}%

                          </div>

                        </div>


                        <div className="mt-3 h-1 overflow-hidden bg-slate-900">

                          <div
                            className="h-full transition-all"
                            style={{
                              width: `${Math.min(
                                congestion,
                                100
                              )}%`,
                              background:
                                color,
                              boxShadow:
                                `0 0 10px ${color}`,
                            }}
                          />

                        </div>

                      </div>


                      <div
                        className={`border px-3 py-1.5 text-[8px] uppercase tracking-[0.16em] ${getCongestionStyle(
                          Number(
                            segment.congestion_score ||
                              0
                          )
                        )}`}
                      >

                        {segment.is_bottleneck
                          ? "BOTTLENECK"
                          : getCongestionLabel(
                              Number(
                                segment.congestion_score ||
                                  0
                              )
                            )}

                      </div>

                    </button>

                  )

                }
              )}

            </div>

          )}

        </div>

      </div>


      {/* =====================================================
          TRAFFIC FLOW DISTRIBUTION
      ===================================================== */}

      <div className="mt-10">

        <div className="mb-4">

          <div className="mb-1 text-[10px] uppercase tracking-[0.22em] text-cyan-500/60">

            Flow Analysis

          </div>


          <h2 className="text-lg font-medium">

            Traffic Distribution

          </h2>


          <p className="mt-1 text-sm text-slate-500">

            Relative vehicle activity across monitored corridors.

          </p>

        </div>


        <div className="veytra-panel veytra-hud p-6">

          <div className="space-y-5">

            {topFlowSegments.length ===
            0 ? (

              <div className="text-sm text-slate-500">

                No traffic distribution data available.

              </div>

            ) : (

              topFlowSegments.map(
                (segment, index) => {

                  const vehicles =
                    Number(
                      segment.vehicle_count ||
                        0
                    )

                  const percentage =
                    (vehicles /
                      maxVehicles) *
                    100

                  return (

                    <div
                      key={`${segment.segment_id}-${segment.timestamp}-${index}`}
                    >

                      <div className="mb-2 flex items-center justify-between">

                        <div>

                          <span className="font-mono text-xs text-slate-300">

                            {segment.segment_id}

                          </span>


                          {segment.road_name && (

                            <span className="ml-3 text-[10px] text-slate-600">

                              {segment.road_name}

                            </span>

                          )}

                        </div>


                        <span className="font-mono text-xs text-slate-500">

                          {vehicles.toLocaleString()}
                          {" "}vehicles

                        </span>

                      </div>


                      <div className="h-1.5 bg-slate-900">

                        <div
                          className="h-full bg-cyan-400/60 shadow-[0_0_10px_rgba(34,211,238,0.25)]"
                          style={{
                            width: `${percentage}%`,
                          }}
                        />

                      </div>

                    </div>

                  )

                }
              )

            )}

          </div>

        </div>

      </div>


      {/* =====================================================
          ORIGIN → DESTINATION
      ===================================================== */}

      {movementFlows.length > 0 && (

        <div className="mt-10">

          <div className="mb-4">

            <div className="mb-1 text-[10px] uppercase tracking-[0.22em] text-cyan-500/60">

              Movement Intelligence

            </div>


            <h2 className="text-lg font-medium">

              Origin → Destination Flow

            </h2>


            <p className="mt-1 text-sm text-slate-500">

              Reconstructed vehicle movement between monitored areas.

            </p>

          </div>


          <div className="veytra-panel veytra-hud overflow-hidden">

            {movementFlows
              .slice(0, 6)
              .map(
                (flow, index) => (

                  <div
                    key={`${flow.origin}-${flow.destination}-${index}`}
                    className="flex flex-col gap-3 border-b border-cyan-400/5 p-5 last:border-b-0 md:flex-row md:items-center"
                  >

                    <div className="font-mono text-[9px] text-slate-700">

                      {String(
                        index + 1
                      ).padStart(
                        2,
                        "0"
                      )}

                    </div>


                    <div className="flex flex-1 items-center gap-4">

                      <div className="border border-cyan-400/10 bg-cyan-400/5 px-3 py-2 font-mono text-xs text-slate-300">

                        {flow.origin}

                      </div>


                      <div className="flex flex-1 items-center gap-2">

                        <div className="h-px flex-1 bg-cyan-400/20" />

                        <span className="font-mono text-cyan-400/60">

                          →

                        </span>

                        <div className="h-px flex-1 bg-cyan-400/20" />

                      </div>


                      <div className="border border-cyan-400/10 bg-cyan-400/5 px-3 py-2 font-mono text-xs text-slate-300">

                        {flow.destination}

                      </div>

                    </div>


                    <div className="font-mono text-sm text-cyan-300">

                      {flow.vehicles.toLocaleString()}

                      <span className="ml-2 text-[9px] text-slate-600">

                        VEHICLES

                      </span>

                    </div>

                  </div>

                )
              )}

          </div>

        </div>

      )}


      {/* =====================================================
          SEGMENT DETAIL
      ===================================================== */}

      <div className="mt-10">

        <div className="mb-4 flex items-end justify-between">

          <div>

            <div className="mb-1 text-[10px] uppercase tracking-[0.22em] text-cyan-500/60">

              Network Analysis

            </div>


            <h2 className="text-lg font-medium">

              Road Segments

            </h2>


            <p className="mt-1 text-sm text-slate-500">

              Detailed traffic conditions reconstructed for each monitored corridor.

            </p>

          </div>


          <div className="font-mono text-xs text-slate-600">

            {segments.length
              .toString()
              .padStart(2, "0")}

            {" "}SEGMENTS

          </div>

        </div>


        {segments.length === 0 ? (

          <div className="veytra-panel veytra-hud p-8">

            <p className="text-sm text-slate-500">

              No traffic segment data available.

            </p>

          </div>

        ) : (

          <div className="space-y-4">

            {segments.map(
              (segment, index) => {

                const congestion =
                  Math.round(
                    Number(
                      segment.congestion_score ||
                        0
                    ) * 100
                  )

                const score =
                  Number(
                    segment.congestion_score ||
                      0
                  )

                return (

                  <div
                    key={`${segment.segment_id}-${segment.timestamp}-${index}`}
                    className="veytra-panel veytra-panel-hover veytra-hud overflow-hidden"
                  >

                    {/* HEADER */}

                    <div className="flex flex-col gap-4 border-b border-cyan-400/10 p-5 md:flex-row md:items-center md:justify-between">

                      <div className="flex items-center gap-4">

                        <div className="flex h-10 w-10 items-center justify-center border border-cyan-400/10 bg-cyan-400/5 font-mono text-xs text-cyan-400">

                          {String(
                            index + 1
                          ).padStart(
                            2,
                            "0"
                          )}

                        </div>


                        <div>

                          <div className="text-[9px] uppercase tracking-[0.2em] text-slate-600">

                            Road Segment

                          </div>


                          <h3 className="mt-1 font-mono text-base text-slate-200">

                            {segment.segment_id}

                          </h3>


                          {segment.road_name && (

                            <p className="mt-1 text-xs text-slate-500">

                              {segment.road_name}

                            </p>

                          )}


                          {segment.timestamp && (

                            <p className="mt-1 font-mono text-[10px] text-slate-700">

                              {segment.timestamp}

                            </p>

                          )}

                        </div>

                      </div>


                      <div
                        className={`w-fit border px-3 py-1.5 text-[9px] uppercase tracking-[0.18em] ${getCongestionStyle(
                          score
                        )}`}
                      >

                        {getCongestionLabel(
                          score
                        )}

                      </div>

                    </div>


                    {/* METRICS */}

                    <div className="grid grid-cols-1 gap-px bg-cyan-400/5 md:grid-cols-3">

                      <div className="bg-[#061016] p-5">

                        <div className="text-[9px] uppercase tracking-[0.2em] text-slate-600">

                          Vehicles

                        </div>


                        <div className="mt-3 font-mono text-2xl text-slate-200">

                          {Number(
                            segment.vehicle_count ||
                              0
                          ).toLocaleString()}

                        </div>


                        <div className="mt-1 text-[10px] text-slate-600">

                          Observed vehicles

                        </div>

                      </div>


                      <div className="bg-[#061016] p-5">

                        <div className="text-[9px] uppercase tracking-[0.2em] text-slate-600">

                          Average Speed

                        </div>


                        <div className="mt-3 font-mono text-2xl text-slate-200">

                          {Number(
                            segment.average_speed ||
                              0
                          ).toFixed(1)}

                          <span className="ml-2 text-xs text-slate-600">

                            km/h

                          </span>

                        </div>


                        <div className="mt-1 text-[10px] text-slate-600">

                          Segment movement speed

                        </div>

                      </div>


                      <div className="bg-[#061016] p-5">

                        <div className="text-[9px] uppercase tracking-[0.2em] text-slate-600">

                          Congestion

                        </div>


                        <div
                          className="mt-3 font-mono text-2xl"
                          style={{
                            color:
                              getHeatColor(
                                score
                              ),
                          }}
                        >

                          {congestion}

                          <span className="ml-1 text-xs opacity-50">

                            %

                          </span>

                        </div>


                        <div className="mt-1 text-[10px] text-slate-600">

                          Network condition

                        </div>

                      </div>

                    </div>


                    {/* BAR */}

                    <div className="p-5">

                      <div className="mb-2 flex items-center justify-between">

                        <span className="text-[9px] uppercase tracking-[0.2em] text-slate-600">

                          Congestion Index

                        </span>


                        <span className="font-mono text-[10px] text-slate-500">

                          {congestion}%

                        </span>

                      </div>


                      <div className="relative h-1.5 overflow-hidden bg-slate-800/80">

                        <div
                          className="h-full"
                          style={{
                            width: `${Math.min(
                              Math.max(
                                congestion,
                                0
                              ),
                              100
                            )}%`,
                            background:
                              getHeatColor(
                                score
                              ),
                            boxShadow:
                              `0 0 12px ${getHeatColor(
                                score
                              )}`,
                          }}
                        />

                      </div>

                    </div>

                  </div>

                )

              }
            )}

          </div>

        )}

      </div>


      {/* =====================================================
          FOOTER
      ===================================================== */}

      <div className="mt-10 flex flex-col gap-2 border-t border-cyan-400/10 pt-4 text-[9px] uppercase tracking-[0.18em] text-slate-700 md:flex-row md:items-center md:justify-between">

        <span>

          VEYTRA / CITY-WIDE TRAFFIC INTELLIGENCE

        </span>


        <span>

          Flow • Speed • Density • Congestion • Bottlenecks

        </span>

      </div>

    </div>

  )

}


export default TrafficAnalytics