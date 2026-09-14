function SourceBadge({ source }) {
  const isReal = source === "real"

  return (
    <span
      className={`px-2.5 py-1 rounded-full text-[10px] font-semibold uppercase tracking-wide ${
        isReal ? "veytra-pill-real" : "veytra-pill-sim"
      }`}
    >
      {isReal ? "Real" : "Simulated"}
    </span>
  )
}

export default SourceBadge
