function LandingPage({ onEnter, onNavigate }) {
  const cameras = [
    { id: "CAM 01", location: "JUNCTION", status: "LIVE", real: true },
    { id: "CAM 02", location: "NORTH", status: "LIVE", real: true },
    { id: "CAM 03", location: "ITO", status: "LIVE", real: true },
    { id: "CAM 04", location: "CENTRAL", status: "NETWORK" },
    { id: "CAM 05", location: "RING ROAD", status: "NETWORK" },
    { id: "CAM 06", location: "SOUTH", status: "NETWORK" },
    { id: "CAM 07", location: "JUNCTION", status: "NETWORK" },
    { id: "CAM 08", location: "EAST", status: "NETWORK" },
    { id: "CAM 09", location: "NORTH", status: "NETWORK" },
    { id: "CAM 10", location: "CENTRAL", status: "NETWORK" },
    { id: "CAM 11", location: "WEST", status: "NETWORK" },
    { id: "CAM 12", location: "ITO", status: "NETWORK" },
    { id: "CAM 13", location: "SOUTH", status: "NETWORK" },
    { id: "CAM 14", location: "JUNCTION", status: "NETWORK" },
    { id: "CAM 15", location: "EAST", status: "NETWORK" },
    { id: "CAM 16", location: "NORTH", status: "NETWORK" },
    { id: "CAM 17", location: "RING ROAD", status: "NETWORK" },
    { id: "CAM 18", location: "CENTRAL", status: "NETWORK" },
    { id: "CAM 19", location: "WEST", status: "NETWORK" },
    { id: "CAM 20", location: "SOUTH", status: "NETWORK" },
  ]

  return (
    <div className="relative min-h-screen overflow-hidden bg-[#02070b] text-white">

      {/* ========================================================= */}
      {/* CAMERA WALL                                               */}
      {/* ========================================================= */}

      <div className="absolute inset-0">

        <div className="grid h-full w-full grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">

          {cameras.map((camera, index) => (

            <div
              key={camera.id}
              className="relative min-h-[180px] overflow-hidden border-r border-b border-cyan-300/[0.07]"
            >

              {/* Camera feed */}
              <div
                className={`absolute inset-0 ${
                  index % 4 === 0
                    ? "bg-gradient-to-br from-[#17242a] via-[#071116] to-[#020609]"
                    : index % 4 === 1
                    ? "bg-gradient-to-bl from-[#1b292e] via-[#091419] to-[#02070b]"
                    : index % 4 === 2
                    ? "bg-gradient-to-br from-[#111e24] via-[#050d12] to-[#020609]"
                    : "bg-gradient-to-tl from-[#18252a] via-[#071116] to-[#020609]"
                }`}
              >

                {/* Road */}
                <div className="absolute left-1/2 top-[-20%] h-[150%] w-[38%] -translate-x-1/2 rotate-[3deg] bg-slate-500/[0.09]" />

                {/* Road divider */}
                <div className="absolute left-1/2 top-0 h-full -translate-x-1/2 border-l border-dashed border-white/[0.10]" />

                {/* Fake vehicle */}
                <div
                  className="absolute h-8 w-4 rounded-sm bg-white/[0.09] blur-[1px]"
                  style={{
                    left: `${25 + (index * 13) % 45}%`,
                    top: `${20 + (index * 17) % 60}%`,
                    transform: `rotate(${index % 2 ? "-5deg" : "5deg"})`,
                  }}
                />

                <div
                  className="absolute h-10 w-5 rounded-sm bg-cyan-300/[0.10] blur-[1px]"
                  style={{
                    left: `${48 + (index * 7) % 25}%`,
                    top: `${35 + (index * 11) % 45}%`,
                    transform: `rotate(${index % 2 ? "4deg" : "-4deg"})`,
                  }}
                />

                {/* Scanlines */}
                <div className="absolute inset-0 bg-[linear-gradient(transparent_50%,rgba(34,211,238,0.025)_50%)] bg-[length:100%_4px]" />

                {/* Camera label */}
                <div className="absolute left-3 top-3 text-[8px] font-medium tracking-[0.18em] text-cyan-200/70">
                  {camera.id}
                </div>

                <div className="absolute left-3 top-6 text-[7px] uppercase tracking-[0.18em] text-white/30">
                  {camera.location}
                </div>

                {/* Status */}
                <div className="absolute right-3 top-3 flex items-center gap-1.5">

                  <span
                    className={`h-1.5 w-1.5 rounded-full ${
                      camera.real
                        ? "bg-cyan-300 shadow-[0_0_8px_#22d3ee]"
                        : "bg-white/20"
                    }`}
                  />

                  <span
                    className={`text-[7px] tracking-[0.15em] ${
                      camera.real
                        ? "text-cyan-200/70"
                        : "text-white/25"
                    }`}
                  >
                    {camera.status}
                  </span>

                </div>

                {/* Tracking box */}
                {index % 3 === 0 && (
                  <div
                    className="absolute h-10 w-7 border border-cyan-300/20"
                    style={{
                      left: `${30 + (index * 9) % 35}%`,
                      top: `${40 + (index * 5) % 30}%`,
                    }}
                  >

                    <div className="absolute -left-px -top-px h-2 w-2 border-l border-t border-cyan-300/60" />
                    <div className="absolute -right-px -top-px h-2 w-2 border-r border-t border-cyan-300/60" />
                    <div className="absolute -bottom-px -left-px h-2 w-2 border-b border-l border-cyan-300/60" />
                    <div className="absolute -bottom-px -right-px h-2 w-2 border-b border-r border-cyan-300/60" />

                  </div>
                )}

                {/* Bottom metadata */}
                <div className="absolute bottom-3 left-3 text-[6px] tracking-[0.15em] text-white/20">
                  VEHICLE TRACKING • ANPR
                </div>

              </div>

            </div>

          ))}

        </div>

        {/* Main darkness */}
        <div className="absolute inset-0 bg-[#02070b]/72" />

        {/* Center glow */}
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_45%,rgba(20,184,166,0.13),transparent_38%)]" />

        {/* Dark vignette */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_10%,rgba(0,0,0,0.88)_100%)]" />

        {/* Grid */}
        <div className="absolute inset-0 opacity-[0.08] bg-[linear-gradient(rgba(34,211,238,0.2)_1px,transparent_1px),linear-gradient(90deg,rgba(34,211,238,0.2)_1px,transparent_1px)] bg-[size:80px_80px]" />

      </div>


      {/* ========================================================= */}
      {/* TOP NAV                                                   */}
      {/* ========================================================= */}

      <nav className="relative z-30 flex items-center justify-between px-6 py-5 lg:px-12">

        {/* Logo */}
        <div className="flex items-center gap-3">

          <div className="flex h-10 w-10 items-center justify-center rounded-lg border border-cyan-300/30 bg-black/30 backdrop-blur-xl">

            <div className="relative h-5 w-5 rotate-45 border border-cyan-300/80">
              <div className="absolute inset-1 border border-cyan-300/30" />
            </div>

          </div>

          <div>

            <div className="text-sm font-bold tracking-[0.3em]">
              VEYTRA
            </div>

            <div className="text-[7px] uppercase tracking-[0.25em] text-slate-500">
              City Intelligence Network
            </div>

          </div>

        </div>


        {/* Center navigation */}
        <div className="hidden items-center gap-8 text-[9px] uppercase tracking-[0.18em] text-slate-500 lg:flex">

          <button
            onClick={() => onNavigate("command")}
            className="text-cyan-300/80 transition hover:text-cyan-200"
          >
            Overview
          </button>

          <button
            onClick={() => onNavigate("vehicles")}
            className="transition hover:text-cyan-300"
          >
            Trajectory
          </button>

          <button
            onClick={() => onNavigate("analytics")}
            className="transition hover:text-cyan-300"
          >
            Traffic
          </button>

          <button
            onClick={() => onNavigate("alerts")}
            className="transition hover:text-cyan-300"
          >
            Alerts
          </button>

          <button
            onClick={() => onNavigate("command")}
            className="transition hover:text-cyan-300"
          >
            City
          </button>

        </div>


        {/* Right side */}
        <div className="flex items-center gap-4">

          <div className="hidden items-center gap-2 text-[8px] uppercase tracking-[0.18em] text-slate-500 sm:flex">

            <span className="h-1.5 w-1.5 rounded-full bg-cyan-300 shadow-[0_0_8px_#22d3ee]" />

            SYSTEM ACTIVE

          </div>


          <button
            onClick={onEnter}
            className="rounded-lg border border-cyan-300/30 bg-black/30 px-4 py-2 text-[9px] font-semibold uppercase tracking-[0.15em] text-cyan-200 backdrop-blur-xl transition hover:border-cyan-300/70 hover:bg-cyan-300/10"
          >
            Authorized Access →
          </button>

        </div>

      </nav>


      {/* ========================================================= */}
      {/* HUD CORNERS                                               */}
      {/* ========================================================= */}

      <div className="pointer-events-none absolute left-5 top-24 z-20 hidden h-16 w-16 border-l border-t border-cyan-300/20 lg:block" />

      <div className="pointer-events-none absolute right-5 top-24 z-20 hidden h-16 w-16 border-r border-t border-cyan-300/20 lg:block" />

      <div className="pointer-events-none absolute bottom-5 left-5 z-20 hidden h-16 w-16 border-b border-l border-cyan-300/20 lg:block" />

      <div className="pointer-events-none absolute bottom-5 right-5 z-20 hidden h-16 w-16 border-b border-r border-cyan-300/20 lg:block" />


      {/* ========================================================= */}
      {/* HERO                                                      */}
      {/* ========================================================= */}

      <main className="relative z-10 flex min-h-[calc(100vh-80px)] items-center justify-center px-5 pb-16 pt-8">

        <div className="mx-auto w-full max-w-6xl text-center">

          {/* Status */}
          <div className="mb-7 inline-flex items-center gap-3 rounded-full border border-cyan-300/20 bg-black/35 px-5 py-2 backdrop-blur-xl">

            <span className="relative flex h-2 w-2">

              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-cyan-300 opacity-50" />

              <span className="relative inline-flex h-2 w-2 rounded-full bg-cyan-300" />

            </span>

            <span className="text-[8px] font-medium uppercase tracking-[0.25em] text-cyan-200/80">
              03 camera nodes connected • intelligence pipeline active
            </span>

          </div>


          {/* Eyebrow */}
          <div className="mb-5 text-[9px] uppercase tracking-[0.4em] text-cyan-300/50">
            CITY-WIDE VEHICLE & TRAFFIC INTELLIGENCE
          </div>


          {/* Heading */}
          <h1 className="text-5xl font-semibold leading-[0.9] tracking-[-0.05em] sm:text-7xl lg:text-[104px]">

            One city.
            <br />

            <span className="text-slate-400">
              One connected view.
            </span>

          </h1>


          {/* Description */}
          <p className="mx-auto mt-8 max-w-2xl text-sm leading-7 text-slate-300/70 sm:text-base">

            VEYTRA connects distributed ANPR and CCTV observations
            into a single operational picture — tracking vehicles,
            reconstructing trajectories, verifying movement and
            understanding traffic across the city.

          </p>


          {/* Buttons */}
          <div className="mt-9 flex flex-wrap justify-center gap-3">

            {/* Choose Analysis City */}
            <button
              onClick={() => onNavigate("command")}
              className="group rounded-lg bg-gradient-to-r from-cyan-300 to-teal-300 px-7 py-3.5 text-[10px] font-bold uppercase tracking-[0.12em] text-[#031016] shadow-[0_0_35px_rgba(45,212,191,0.16)] transition hover:scale-[1.02]"
            >

              Choose Analysis City

              <span className="ml-2 transition group-hover:ml-3">
                →
              </span>

            </button>


            {/* Explore Trajectory */}
            <button
              onClick={() => onNavigate("vehicles")}
              className="rounded-lg border border-white/10 bg-black/25 px-7 py-3.5 text-[10px] font-semibold uppercase tracking-[0.12em] text-slate-200 backdrop-blur-xl transition hover:border-cyan-300/30 hover:bg-white/5"
            >
              Explore Trajectory
            </button>

          </div>


          {/* ===================================================== */}
          {/* SYSTEM PANEL                                          */}
          {/* ===================================================== */}

          <div className="mx-auto mt-16 grid max-w-4xl grid-cols-2 border border-white/[0.08] bg-black/30 backdrop-blur-xl sm:grid-cols-4">

            <div className="border-b border-r border-white/[0.08] p-5 sm:border-b-0">

              <div className="text-xl font-semibold text-cyan-200">
                03
              </div>

              <div className="mt-1 text-[7px] uppercase tracking-[0.22em] text-slate-500">
                Connected cameras
              </div>

            </div>


            <div className="border-b border-white/[0.08] p-5 sm:border-b-0 sm:border-r">

              <div className="text-xl font-semibold text-cyan-200">
                ANPR
              </div>

              <div className="mt-1 text-[7px] uppercase tracking-[0.22em] text-slate-500">
                Plate intelligence
              </div>

            </div>


            <div className="border-r border-white/[0.08] p-5">

              <div className="text-xl font-semibold text-cyan-200">
                Re-ID
              </div>

              <div className="mt-1 text-[7px] uppercase tracking-[0.22em] text-slate-500">
                Cross-camera tracking
              </div>

            </div>


            <div className="p-5">

              <div className="text-xl font-semibold text-cyan-200">
                LIVE
              </div>

              <div className="mt-1 text-[7px] uppercase tracking-[0.22em] text-slate-500">
                Intelligence pipeline
              </div>

            </div>

          </div>


          {/* Bottom status */}
          <div className="mt-7 flex flex-wrap items-center justify-center gap-3 text-[7px] uppercase tracking-[0.25em] text-slate-600">

            <span>VEYTRA</span>

            <span>•</span>

            <span>Secure intelligence infrastructure</span>

            <span>•</span>

            <span>SIH 2026</span>

          </div>

        </div>

      </main>


      {/* ========================================================= */}
      {/* BOTTOM SYSTEM BAR                                        */}
      {/* ========================================================= */}

      <div className="pointer-events-none absolute bottom-4 left-6 z-30 hidden text-[7px] uppercase tracking-[0.25em] text-cyan-300/30 lg:block">

        NETWORK STATUS: OPERATIONAL

        <span className="mx-3">
          •
        </span>

        MULTI-CAMERA LINK ACTIVE

        <span className="mx-3">
          •
        </span>

        ENCRYPTED

      </div>


      <div className="pointer-events-none absolute bottom-4 right-6 z-30 hidden text-[7px] uppercase tracking-[0.25em] text-slate-600 lg:block">

        VEYTRA // COMMAND INFRASTRUCTURE // 2026

      </div>

    </div>
  )
}

export default LandingPage