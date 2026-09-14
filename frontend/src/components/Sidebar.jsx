function Sidebar({ activePage, setActivePage }) {
  const pages = [
    {
      id: "command",
      label: "Overview",
      icon: (
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.7"
          width="22"
          height="22"
        >
          <path d="M4 10.5 12 4l8 6.5" />
          <path d="M6.5 9.5V20h11V9.5" />
          <path d="M9.5 20v-5.5h5V20" />
        </svg>
      ),
    },

    {
      id: "vehicles",
      label: "Trajectory",
      icon: (
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.7"
          width="22"
          height="22"
        >
          <path d="M5 18.5c4-1 5.5-6.5 8.5-8.5 1.7-1.2 3.2-1.2 5.5-2" />
          <path d="M15.5 7.5H19v3.5" />
        </svg>
      ),
    },

    {
      id: "analytics",
      label: "Traffic",
      icon: (
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.7"
          width="22"
          height="22"
        >
          <path d="M5 9c2-2 4-2 6 0s4 2 6 0 3-2 3-2" />
          <path d="M5 14c2-2 4-2 6 0s4 2 6 0 3-2 3-2" />
        </svg>
      ),
    },

    {
      id: "alerts",
      label: "Alerts",
      icon: (
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.7"
          width="22"
          height="22"
        >
          <path d="M12 5v7" />
          <circle cx="12" cy="17.5" r=".8" fill="currentColor" />
        </svg>
      ),
    },

    {
      id: "verification",
      label: "Automation",
      icon: (
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.7"
          width="22"
          height="22"
        >
          <circle cx="12" cy="12" r="7" />
          <circle cx="12" cy="12" r="3" />
          <path d="M12 2v2M12 20v2M2 12h2M20 12h2" />
        </svg>
      ),
    },

    {
      id: "simulation",
      label: "SUMO",
      icon: (
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.7"
          width="22"
          height="22"
        >
          <circle cx="12" cy="12" r="7" />
          <path d="M12 5v14M5 12h14" />
          <circle cx="12" cy="12" r="2" />
        </svg>
      ),
    },
  ]

  return (
    <aside className="veytra-sidebar flex min-h-screen shrink-0 flex-col">

      {/* =====================================================
          LOGO
          ===================================================== */}

      <div className="flex justify-center pt-4 pb-7">

        <div className="veytra-sidebar-logo">

          <div
            className="h-3.5 w-3.5 rotate-45 border"
            style={{
              borderColor: "rgba(66, 232, 223, 0.9)",
            }}
          >
            <div
              className="m-[3px] h-full w-full border"
              style={{
                borderColor: "rgba(66, 232, 223, 0.35)",
              }}
            />
          </div>

        </div>

      </div>


      {/* =====================================================
          NAVIGATION
          ===================================================== */}

      <nav className="flex flex-1 flex-col items-center gap-3">

        {pages.map((page) => {
          const active = activePage === page.id

          return (
            <button
              key={page.id}
              type="button"
              onClick={() => setActivePage(page.id)}
              aria-label={page.label}
              title={page.label}
              className={`veytra-nav-item ${
                active ? "veytra-nav-item-active" : ""
              }`}
            >

              <span className="veytra-nav-icon">
                {page.icon}
              </span>

              <span className="veytra-nav-label">
                {page.label}
              </span>

            </button>
          )
        })}

      </nav>


      {/* =====================================================
          BOTTOM SYSTEM INDICATOR
          ===================================================== */}

      <div className="flex flex-col items-center gap-2 pb-6">

        <span className="veytra-live-dot veytra-pulse" />

        <span
          className="text-center uppercase"
          style={{
            color: "var(--veytra-dim)",
            fontSize: "8px",
            letterSpacing: "0.12em",
          }}
        >
          Online
        </span>

      </div>

    </aside>
  )
}

export default Sidebar