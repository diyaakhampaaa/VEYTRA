function TopBar({ activePage }) {
  const pageNames = {
    command: "Command Center",
    vehicles: "Vehicle Search",
    verification: "Smart Verification",
    analytics: "Traffic Analytics",
    alerts: "Alerts",
    simulation: "SUMO",
  }

  const currentPage = pageNames[activePage] || "Command Center"

  return (
    <header className="veytra-topbar">
      <div className="veytra-topbar-inner">
        {/* BRAND */}
        <div className="veytra-topbar-brand">
          <div className="veytra-topbar-logo">
            <div className="relative h-5 w-5 rotate-45 border-2 border-[var(--veytra-cyan)]">
              <div className="absolute inset-1 border border-[var(--veytra-cyan)]/50" />
            </div>
          </div>

          <div>
            <div className="veytra-topbar-eyebrow">
              City Intelligence Network
            </div>

            <div className="veytra-topbar-title">
              VEYTRA
            </div>
          </div>
        </div>

        {/* ACTIVE CITY */}
        <div className="veytra-topbar-city">
          <span className="veytra-topbar-city-label">
            Active City
          </span>

          <span className="veytra-topbar-city-name">
            Bengaluru
          </span>
        </div>

        {/* OPERATOR */}
        <div className="veytra-topbar-operator">
          <button
            type="button"
            className="veytra-topbar-operator-button"
            title="Open operator profile"
          >
            <div className="veytra-topbar-operator-info">
              <span className="veytra-topbar-operator-label">
                Authorized Operator
              </span>

              <span className="veytra-topbar-operator-status">
                <span className="veytra-live-dot" />
                Online
              </span>
            </div>

            <div className="veytra-topbar-operator-avatar">
              OP
            </div>
          </button>
        </div>
      </div>
    </header>
  )
}

export default TopBar