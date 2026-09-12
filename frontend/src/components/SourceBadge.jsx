function SourceBadge({ source }) {
  const isReal = source === "real"

  return (
    <span
      className={`px-2 py-1 rounded-full text-xs font-medium ${
        isReal
          ? "bg-green-500/20 text-green-400"
          : "bg-yellow-500/20 text-yellow-400"
      }`}
    >
      {isReal ? "Real" : "Simulated"}
    </span>
  )
}

export default SourceBadge