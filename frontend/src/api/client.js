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
  const response = await fetch(
    `${API_BASE_URL}/analytics/overview`
  )

  if (!response.ok) {
    throw new Error("Failed to fetch analytics")
  }

  return response.json()
}
export async function getAlerts() {
  const response = await fetch(
    `${API_BASE_URL}/alerts`
  )

  if (!response.ok) {
    throw new Error("Failed to fetch alerts")
  }

  return response.json()
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