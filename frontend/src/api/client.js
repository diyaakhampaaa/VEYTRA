const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000"


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
  const normalizedPlate = plate.replace(/\s+/g, "").toUpperCase()

  const response = await fetch(
    `${API_BASE_URL}/vehicles/search?plate=${encodeURIComponent(normalizedPlate)}`
  )

  if (!response.ok) {
    throw new Error("Vehicle search failed")
  }

  return response.json()
}


export async function getVerificationEvents() {
  const response = await fetch(`${API_BASE_URL}/verification/events`)

  if (!response.ok) {
    throw new Error("Failed to fetch verification events")
  }

  return response.json()
}


export async function runVerification(payloads) {
  const response = await fetch(`${API_BASE_URL}/verification/run`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payloads),
  })

  if (!response.ok) {
    const errorText = await response.text()

    throw new Error(
      `Verification request failed: ${response.status} ${errorText}`
    )
  }

  return response.json()
}


export async function getAnalytics() {
  try {
    const response = await fetch(`${API_BASE_URL}/analytics`)

    if (!response.ok) {
      throw new Error(`Analytics request failed: ${response.status}`)
    }

    return response.json()
  } catch (error) {
    console.warn(
      "Analytics backend unavailable. Using demo analytics.",
      error
    )

    return {
      status: "success",
      source: {
        type: "controlled_vehicle_observations",
        file: "demo",
        note: "Demo traffic analytics for presentation",
      },

      summary: {
        total_vehicles: 247,
        average_speed_kmh: 34.7,
        average_congestion: 0.61,
        bottleneck_count: 3,
      },

      segments: [
        {
          segment_id: "SEG_A1",
          road_name: "Indiranagar Corridor",
          vehicle_count: 82,
          average_speed: 28.4,
          congestion_score: 0.78,
          timestamp: "18:50:00",
        },
        {
          segment_id: "SEG_B2",
          road_name: "MG Road Corridor",
          vehicle_count: 67,
          average_speed: 31.2,
          congestion_score: 0.64,
          timestamp: "18:50:00",
        },
        {
          segment_id: "SEG_C3",
          road_name: "Marathahalli Corridor",
          vehicle_count: 54,
          average_speed: 36.8,
          congestion_score: 0.43,
          timestamp: "18:50:00",
        },
        {
          segment_id: "SEG_D4",
          road_name: "Electronic City Corridor",
          vehicle_count: 44,
          average_speed: 42.5,
          congestion_score: 0.21,
          timestamp: "18:50:00",
        },
      ],

      bottlenecks: [
        {
          segment_id: "SEG_A1",
          road_name: "Indiranagar Corridor",
          congestion_score: 0.78,
          is_bottleneck: true,
        },
        {
          segment_id: "SEG_B2",
          road_name: "MG Road Corridor",
          congestion_score: 0.64,
          is_bottleneck: true,
        },
        {
          segment_id: "SEG_C3",
          road_name: "Marathahalli Corridor",
          congestion_score: 0.43,
          is_bottleneck: true,
        },
      ],

      movement_flows: [
        {
          origin: "SEG_A1",
          destination: "SEG_B2",
          vehicles: 82,
          origin_segment_id: "SEG_A1",
          destination_segment_id: "SEG_B2",
        },
        {
          origin: "SEG_B2",
          destination: "SEG_C3",
          vehicles: 67,
          origin_segment_id: "SEG_B2",
          destination_segment_id: "SEG_C3",
        },
        {
          origin: "SEG_C3",
          destination: "SEG_D4",
          vehicles: 54,
          origin_segment_id: "SEG_C3",
          destination_segment_id: "SEG_D4",
        },
      ],
    }
  }
}

export async function getSimulationComparison() {
  const response = await fetch(
    `${API_BASE_URL}/simulation/comparison`
  )

  if (!response.ok) {
    const errorText = await response.text()
    throw new Error(
      `Simulation comparison failed: ${response.status} ${errorText}`
    )
  }

  return response.json()
}


export async function runSimulation() {
  const response = await fetch(
    `${API_BASE_URL}/simulation/run`,
    {
      method: "POST",
    }
  )

  if (!response.ok) {
    const errorText = await response.text()
    throw new Error(
      `Simulation run failed: ${response.status} ${errorText}`
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
