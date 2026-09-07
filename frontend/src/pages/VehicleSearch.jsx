import { useState } from "react"
import SourceBadge from "../components/SourceBadge"
import { searchVehicle } from "../api/client"

function VehicleSearch() {
  const [plate, setPlate] = useState("")
  const [vehicle, setVehicle] = useState(null)
  const [searched, setSearched] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleSearch = async () => {
    if (!plate.trim()) return

    setLoading(true)
    setSearched(false)

    try {
      const data = await searchVehicle(plate.trim())

      if (data.found) {
        setVehicle(data.vehicle)
      } else {
        setVehicle(null)
      }

      setSearched(true)
    } catch (error) {
      console.error("Vehicle search error:", error)
      setVehicle(null)
      setSearched(true)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      {/* Header */}
      <h2 className="text-2xl font-semibold">
        Vehicle Search
      </h2>

      <p className="mt-2 text-slate-400">
        Search and track vehicles across the camera network.
      </p>

      {/* Search */}
      <div className="mt-8 flex gap-3">
        <input
          type="text"
          value={plate}
          onChange={(e) => setPlate(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              handleSearch()
            }
          }}
          placeholder="Enter vehicle plate..."
          className="flex-1 rounded-lg border border-slate-700 bg-slate-900 px-4 py-3 text-white outline-none placeholder:text-slate-500 focus:border-slate-500"
        />

        <button
          onClick={handleSearch}
          disabled={loading}
          className="rounded-lg bg-white px-6 py-3 font-medium text-slate-950 transition hover:bg-slate-200 disabled:opacity-50"
        >
          {loading ? "Searching..." : "Search"}
        </button>
      </div>

      {/* Results */}
      {searched && !vehicle && (
        <div className="mt-6 rounded-xl border border-slate-800 bg-slate-900 p-6">
          <p className="text-slate-400">
            No vehicle found for{" "}
            <span className="text-white">
              {plate.toUpperCase()}
            </span>
          </p>
        </div>
      )}

      {vehicle && (
        <div className="mt-6 rounded-xl border border-slate-800 bg-slate-900 p-6">
          {/* Vehicle Header */}
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-500">
                Vehicle ID
              </p>

              <h3 className="mt-1 text-xl font-semibold">
                {vehicle.vehicle_id}
              </h3>
            </div>

            <SourceBadge source={vehicle.source} />
          </div>

          {/* Plate */}
          <div className="mt-6 rounded-lg bg-slate-800 p-4">
            <p className="text-sm text-slate-400">
              License Plate
            </p>

            <p className="mt-1 text-2xl font-semibold tracking-wider">
              {vehicle.plate}
            </p>
          </div>

          {/* Camera Journey */}
          <div className="mt-6">
            <p className="mb-3 text-sm text-slate-400">
              Camera Journey
            </p>

            <div className="flex items-center gap-3">
              {vehicle.camera_sequence.map((camera, index) => (
                <div
                  key={camera}
                  className="flex items-center gap-3"
                >
                  <div className="rounded-lg border border-slate-700 bg-slate-800 px-4 py-3">
                    <p className="font-medium">
                      {camera}
                    </p>
                  </div>

                  {index < vehicle.camera_sequence.length - 1 && (
                    <span className="text-slate-600">
                      →
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Match Scores */}
          <div className="mt-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
            <div className="rounded-lg bg-slate-800 p-4">
              <p className="text-xs text-slate-400">
                Re-ID Similarity
              </p>

              <p className="mt-1 text-xl font-semibold">
                {Math.round(
                  vehicle.match_score.reid_similarity * 100
                )}%
              </p>
            </div>

            <div className="rounded-lg bg-slate-800 p-4">
              <p className="text-xs text-slate-400">
                Plate Similarity
              </p>

              <p className="mt-1 text-xl font-semibold">
                {Math.round(
                  vehicle.match_score.plate_similarity * 100
                )}%
              </p>
            </div>

            <div className="rounded-lg bg-slate-800 p-4">
              <p className="text-xs text-slate-400">
                Temporal Score
              </p>

              <p className="mt-1 text-xl font-semibold">
                {Math.round(
                  vehicle.match_score.temporal_score * 100
                )}%
              </p>
            </div>

            <div className="rounded-lg bg-slate-800 p-4">
              <p className="text-xs text-slate-400">
                Route Score
              </p>

              <p className="mt-1 text-xl font-semibold">
                {Math.round(
                  vehicle.match_score.route_score * 100
                )}%
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default VehicleSearch