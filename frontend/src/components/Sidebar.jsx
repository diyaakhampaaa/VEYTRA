function Sidebar({ activePage, setActivePage }) {
  const pages = [
    {
      id: "command",
      name: "Command Center",
      short: "Overview",
      icon: "◉",
    },
    {
      id: "vehicles",
      name: "Vehicle Search",
      short: "Trajectory",
      icon: "⌕",
    },
    {
      id: "verification",
      name: "Smart Verification",
      short: "Verification",
      icon: "✓",
    },
    {
      id: "analytics",
      name: "Traffic Analytics",
      short: "Traffic",
      icon: "▥",
    },
    {
      id: "alerts",
      name: "Alerts",
      short: "Alerts",
      icon: "!",
    },
    {
      id: "simulation",
      name: "Simulation",
      short: "Simulation",
      icon: "◇",
    },
  ]

  return (
    <aside className="relative z-40 flex min-h-screen w-[250px] shrink-0 flex-col border-r border-cyan-300/[0.08] bg-[#02070b]/95">

      {/* Subtle grid */}
      <div className="pointer-events-none absolute inset-0 opacity-[0.025]">
        <div className="veytra-grid h-full w-full" />
      </div>

      {/* =====================================================
          BRAND
          ===================================================== */}

      <div className="relative border-b border-cyan-300/[0.08] px-6 py-6">

        <div className="flex items-center gap-3">

          <div className="flex h-10 w-10 items-center justify-center rounded-lg border border-cyan-300/25 bg-cyan-300/[0.04]">

            <div className="relative h-4 w-4 rotate-45 border border-cyan-300/80">

              <div className="absolute inset-1 border border-cyan-300/30" />

            </div>

          </div>

          <div>

            <div className="text-base font-bold tracking-[0.28em] text-white">
              VEYTRA
            </div>

            <div className="mt-1 text-[7px] uppercase tracking-[0.22em] text-slate-500">
              City Intelligence Network
            </div>

          </div>

        </div>

      </div>


      {/* =====================================================
          NETWORK STATUS
          ===================================================== */}

      <div className="relative px-5 pt-5">

        <div className="flex items-center justify-between rounded-lg border border-cyan-300/[0.10] bg-cyan-300/[0.025] px-3 py-2.5">

          <div className="flex items-center gap-2">

            <span className="veytra-live-dot" />

            <span className="text-[8px] uppercase tracking-[0.18em] text-cyan-200/70">
              Network Active
            </span>

          </div>

          <span className="text-[8px] text-slate-600">
            03 NODES
          </span>

        </div>

      </div>


      {/* =====================================================
          NAVIGATION
          ===================================================== */}

      <nav className="relative flex-1 px-4 py-7">

        <div className="mb-3 px-3 text-[8px] font-semibold uppercase tracking-[0.28em] text-slate-600">
          Operations
        </div>

        <div className="space-y-1">

          {pages.map((page) => {

            const active = activePage === page.id

            return (
              <button
                key={page.id}
                onClick={() => setActivePage(page.id)}
                className={`group relative flex w-full items-center gap-3 overflow-hidden rounded-lg px-3 py-3 text-left transition ${
                  active
                    ? "border border-cyan-300/[0.14] bg-cyan-300/[0.06] text-cyan-100"
                    : "border border-transparent text-slate-500 hover:bg-white/[0.025] hover:text-slate-200"
                }`}
              >

                {/* Active glow */}
                {active && (
                  <span className="absolute left-0 top-1/2 h-6 w-[2px] -translate-y-1/2 bg-cyan-300 shadow-[0_0_10px_#22d3ee]" />
                )}

                {/* Icon */}
                <span
                  className={`flex h-7 w-7 items-center justify-center rounded-md border text-[12px] transition ${
                    active
                      ? "border-cyan-300/25 bg-cyan-300/[0.08] text-cyan-300"
                      : "border-white/[0.06] bg-white/[0.015] text-slate-600 group-hover:text-slate-300"
                  }`}
                >
                  {page.icon}
                </span>

                <div className="min-w-0">

                  <div className="text-[10px] font-medium tracking-wide">
                    {page.name}
                  </div>

                  <div
                    className={`mt-0.5 text-[7px] uppercase tracking-[0.15em] ${
                      active
                        ? "text-cyan-300/45"
                        : "text-slate-700"
                    }`}
                  >
                    {page.short}
                  </div>

                </div>

                {active && (
                  <span className="ml-auto h-1.5 w-1.5 rounded-full bg-cyan-300 shadow-[0_0_8px_#22d3ee]" />
                )}

              </button>
            )
          })}

        </div>

      </nav>


      {/* =====================================================
          SYSTEM FOOTER
          ===================================================== */}

      <div className="relative border-t border-cyan-300/[0.08] p-4">

        <div className="rounded-lg border border-white/[0.05] bg-white/[0.015] p-3">

          <div className="flex items-center justify-between">

            <div className="flex items-center gap-2">

              <span className="veytra-live-dot" />

              <span className="text-[8px] uppercase tracking-[0.16em] text-slate-400">
                System Operational
              </span>

            </div>

            <span className="text-[7px] text-slate-700">
              v1.0
            </span>

          </div>

          <div className="mt-3 flex items-center justify-between text-[7px] uppercase tracking-[0.15em] text-slate-700">

            <span>API</span>
            <span className="text-cyan-300/50">CONNECTED</span>

          </div>

          <div className="mt-1 flex items-center justify-between text-[7px] uppercase tracking-[0.15em] text-slate-700">

            <span>PIPELINE</span>
            <span className="text-cyan-300/50">ACTIVE</span>

          </div>

        </div>

        <div className="mt-4 text-center text-[7px] uppercase tracking-[0.22em] text-slate-700">
          VEYTRA // SIH 2026
        </div>

      </div>

    </aside>
  )
}

export default Sidebar