const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8001"
export async function checkBackend() {
  const response = await fetch(`${API_BASE_URL}/health`)

  if (!response.ok) {
    throw new Error("Backend request failed")
  }

  return response.json()
}

export async function getCameras() {
  const response = await fetch(`${API_BASE_URL}/cameras`)

  if (!response.ok) {
    throw new Error("Failed to fetch cameras")
  }

  return response.json()
}

export async function searchVehicle(plate) {
  const normalizedPlate = plate
    .replace(/\s+/g, "")
    .toUpperCase()

  const response = await fetch(
    `${API_BASE_URL}/vehicles/search?plate=${encodeURIComponent(
      normalizedPlate
    )}`
  )

  if (!response.ok) {
    throw new Error("Vehicle search failed")
  }

  return response.json()
}
export async function getVerificationEvents() {
  const response = await fetch(
    `${API_BASE_URL}/verification/events`
  )

  if (!response.ok) {
    throw new Error("Failed to fetch verification events")
  }

  return response.json()
}
export async function getAnalytics() {
  const response = await fetch(`${API_BASE_URL}/analytics/congestion`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify([
      // ==========================================
      // SEGMENT 01 — NORTH AVENUE
      // LOW CONGESTION
      // ==========================================
      {
        camera_id: "CAM_01",
        vehicle_id: "VEH_001",
        road_segment_id: "SEG_01",
        road_name: "North Avenue",
        timestamp: "2026-09-09T18:00:00",
        speed_kmh: 48,
      },
      {
        camera_id: "CAM_02",
        vehicle_id: "VEH_002",
        road_segment_id: "SEG_01",
        road_name: "North Avenue",
        timestamp: "2026-09-09T18:02:00",
        speed_kmh: 45,
      },
      {
        camera_id: "CAM_03",
        vehicle_id: "VEH_003",
        road_segment_id: "SEG_01",
        road_name: "North Avenue",
        timestamp: "2026-09-09T18:04:00",
        speed_kmh: 43,
      },

      // ==========================================
      // SEGMENT 02 — CENTRAL CORRIDOR
      // MODERATE CONGESTION
      // ==========================================
      {
        camera_id: "CAM_01",
        vehicle_id: "VEH_004",
        road_segment_id: "SEG_02",
        road_name: "Central Corridor",
        timestamp: "2026-09-09T18:00:00",
        speed_kmh: 30,
      },
      {
        camera_id: "CAM_02",
        vehicle_id: "VEH_005",
        road_segment_id: "SEG_02",
        road_name: "Central Corridor",
        timestamp: "2026-09-09T18:02:00",
        speed_kmh: 27,
      },
      {
        camera_id: "CAM_03",
        vehicle_id: "VEH_006",
        road_segment_id: "SEG_02",
        road_name: "Central Corridor",
        timestamp: "2026-09-09T18:04:00",
        speed_kmh: 24,
      },
      {
        camera_id: "CAM_01",
        vehicle_id: "VEH_007",
        road_segment_id: "SEG_02",
        road_name: "Central Corridor",
        timestamp: "2026-09-09T18:06:00",
        speed_kmh: 22,
      },

      // ==========================================
      // SEGMENT 03 — EASTERN BYPASS
      // HIGH CONGESTION
      // ==========================================
      {
        camera_id: "CAM_02",
        vehicle_id: "VEH_008",
        road_segment_id: "SEG_03",
        road_name: "Eastern Bypass",
        timestamp: "2026-09-09T18:00:00",
        speed_kmh: 18,
      },
      {
        camera_id: "CAM_03",
        vehicle_id: "VEH_009",
        road_segment_id: "SEG_03",
        road_name: "Eastern Bypass",
        timestamp: "2026-09-09T18:02:00",
        speed_kmh: 16,
      },
      {
        camera_id: "CAM_01",
        vehicle_id: "VEH_010",
        road_segment_id: "SEG_03",
        road_name: "Eastern Bypass",
        timestamp: "2026-09-09T18:04:00",
        speed_kmh: 14,
      },
      {
        camera_id: "CAM_02",
        vehicle_id: "VEH_011",
        road_segment_id: "SEG_03",
        road_name: "Eastern Bypass",
        timestamp: "2026-09-09T18:06:00",
        speed_kmh: 12,
      },
      {
        camera_id: "CAM_03",
        vehicle_id: "VEH_012",
        road_segment_id: "SEG_03",
        road_name: "Eastern Bypass",
        timestamp: "2026-09-09T18:08:00",
        speed_kmh: 11,
      },

      // ==========================================
      // SEGMENT 04 — SOUTH INDUSTRIAL ROAD
      // SEVERE CONGESTION
      // ==========================================
      {
        camera_id: "CAM_01",
        vehicle_id: "VEH_013",
        road_segment_id: "SEG_04",
        road_name: "South Industrial Road",
        timestamp: "2026-09-09T18:00:00",
        speed_kmh: 9,
      },
      {
        camera_id: "CAM_02",
        vehicle_id: "VEH_014",
        road_segment_id: "SEG_04",
        road_name: "South Industrial Road",
        timestamp: "2026-09-09T18:02:00",
        speed_kmh: 7,
      },
      {
        camera_id: "CAM_03",
        vehicle_id: "VEH_015",
        road_segment_id: "SEG_04",
        road_name: "South Industrial Road",
        timestamp: "2026-09-09T18:04:00",
        speed_kmh: 6,
      },
      {
        camera_id: "CAM_01",
        vehicle_id: "VEH_016",
        road_segment_id: "SEG_04",
        road_name: "South Industrial Road",
        timestamp: "2026-09-09T18:06:00",
        speed_kmh: 5,
      },
      {
        camera_id: "CAM_02",
        vehicle_id: "VEH_017",
        road_segment_id: "SEG_04",
        road_name: "South Industrial Road",
        timestamp: "2026-09-09T18:08:00",
        speed_kmh: 4,
      },
      {
        camera_id: "CAM_03",
        vehicle_id: "VEH_018",
        road_segment_id: "SEG_04",
        road_name: "South Industrial Road",
        timestamp: "2026-09-09T18:10:00",
        speed_kmh: 3,
      },
    ]),
  })

  if (!response.ok) {
    const errorText = await response.text()

    throw new Error(
      `Analytics request failed: ${response.status} ${errorText}`
    )
  }

  const result = await response.json()

  const rows = result?.data?.by_segment_time || []

  return {
    segments: rows.map((row) => ({
      segment_id: row.road_segment_id,
      road_name: row.road_name,
      timestamp: row.interval_start,
      vehicle_count: row.vehicle_count,
      average_speed: row.average_speed_kmh,
      congestion_score: row.congestion_score,
      congestion_level: row.congestion_level,
    })),
  }
}
export async function getSimulationComparison() {
  const response = await fetch(
    `${API_BASE_URL}/simulation/comparison`
  )

  if (!response.ok) {
    throw new Error(
      "Failed to fetch simulation comparison"
    )
  }

  return response.json()
}

export async function getAlerts() {
  const response = await fetch(`${API_BASE_URL}/alerts`)

  if (!response.ok) {
    throw new Error("Failed to fetch alerts")
  }

  return response.json()
}