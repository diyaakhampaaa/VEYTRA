function Sidebar({ activePage, setActivePage }) {
  const pages = [
    {
      id: "command",
      name: "Command Center",
      icon: "◉",
    },
    {
      id: "vehicles",
      name: "Vehicle Search",
      icon: "🚗",
    },
    {
      id: "verification",
      name: "Smart Verification",
      icon: "✓",
    },
    {
      id: "analytics",
      name: "Traffic Analytics",
      icon: "▥",
    },
    {
      id: "alerts",
      name: "Alerts",
      icon: "⚠",
    },
    {
      id: "simulation",
      name: "Simulation",
      icon: "◇",
    },
  ]

  return (
    <aside className="flex min-h-screen w-64 flex-col border-r border-slate-800 bg-slate-950">
      {/* Logo */}
      <div className="border-b border-slate-800 p-6">
        <h1 className="text-2xl font-bold tracking-wide">
          VEYTRA
        </h1>

        <p className="mt-1 text-xs text-slate-500">
          Intelligent Traffic Intelligence
        </p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <p className="mb-3 px-3 text-xs font-semibold uppercase tracking-wider text-slate-500">
          Operations
        </p>

        <div className="space-y-1">
          {pages.map((page) => (
            <button
              key={page.id}
              onClick={() => setActivePage(page.id)}
              className={`flex w-full items-center gap-3 rounded-lg px-3 py-3 text-left text-sm transition ${
                activePage === page.id
                  ? "bg-slate-800 text-white"
                  : "text-slate-400 hover:bg-slate-900 hover:text-white"
              }`}
            >
              <span className="w-5 text-center">
                {page.icon}
              </span>

              <span>{page.name}</span>
            </button>
          ))}
        </div>
      </nav>

      {/* System Status */}
      <div className="border-t border-slate-800 p-4">
        <div className="rounded-lg bg-slate-900 p-3">
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-green-400" />

            <span className="text-xs text-slate-400">
              System Operational
            </span>
          </div>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar