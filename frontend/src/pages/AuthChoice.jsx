export default function AuthChoice({ onLogin, onSignup, onBack }) {
  return (
    <div className="min-h-screen bg-[#02070b] text-white flex items-center justify-center relative overflow-hidden">

      {/* Background */}
      <div className="absolute inset-0 veytra-grid opacity-30" />
      <div className="absolute top-[-200px] left-1/2 -translate-x-1/2 w-[650px] h-[650px] rounded-full bg-cyan-400/5 blur-[140px]" />

      <div className="relative z-10 w-full max-w-3xl px-6">

        {/* Header */}
        <div className="text-center mb-10">
          <div className="flex justify-center mb-5">
            <div className="w-16 h-16 rounded-xl border border-cyan-400/30 bg-cyan-400/5 flex items-center justify-center veytra-glow">
              <div className="w-8 h-8 border border-cyan-300/70 rotate-45 flex items-center justify-center">
                <div className="w-3 h-3 border border-cyan-300/70" />
              </div>
            </div>
          </div>

          <h1 className="text-3xl font-semibold tracking-[0.25em]">
            VEYTRA
          </h1>

          <p className="text-[10px] tracking-[0.35em] text-slate-500 mt-2">
            CITY INTELLIGENCE NETWORK
          </p>
        </div>

        {/* Choice panel */}
        <div className="veytra-panel veytra-hud rounded-2xl p-8 md:p-10">

          <div className="text-center mb-10">
            <div className="text-cyan-400 text-[10px] tracking-[0.3em] uppercase mb-3">
              Network Access
            </div>

            <h2 className="text-2xl md:text-3xl font-semibold">
              Enter the intelligence network.
            </h2>

            <p className="text-sm text-slate-500 mt-3">
              Choose how you want to access VEYTRA.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-5">

            {/* Login */}
            <button
              onClick={onLogin}
              className="group text-left rounded-xl border border-cyan-400/15 bg-cyan-400/[0.03] p-7 transition-all duration-300 hover:border-cyan-400/40 hover:bg-cyan-400/[0.06] hover:shadow-[0_0_35px_rgba(34,211,238,0.08)]"
            >
              <div className="flex items-center justify-between mb-8">
                <div className="text-[10px] tracking-[0.25em] text-cyan-400 uppercase">
                  Existing Operator
                </div>

                <span className="text-cyan-400 text-lg transition-transform group-hover:translate-x-1">
                  →
                </span>
              </div>

              <h3 className="text-xl font-semibold mb-2">
                Log In
              </h3>

              <p className="text-sm text-slate-500 leading-relaxed">
                Access your existing VEYTRA command environment.
              </p>
            </button>

            {/* Signup */}
            <button
              onClick={onSignup}
              className="group text-left rounded-xl border border-cyan-400/15 bg-cyan-400/[0.03] p-7 transition-all duration-300 hover:border-cyan-400/40 hover:bg-cyan-400/[0.06] hover:shadow-[0_0_35px_rgba(34,211,238,0.08)]"
            >
              <div className="flex items-center justify-between mb-8">
                <div className="text-[10px] tracking-[0.25em] text-slate-500 uppercase">
                  New Operator
                </div>

                <span className="text-cyan-400 text-lg transition-transform group-hover:translate-x-1">
                  →
                </span>
              </div>

              <h3 className="text-xl font-semibold mb-2">
                Create Account
              </h3>

              <p className="text-sm text-slate-500 leading-relaxed">
                Register a new operator account for the VEYTRA network.
              </p>
            </button>

          </div>

          <div className="mt-8 pt-6 border-t border-cyan-400/10 text-center">
            <button
              onClick={onBack}
              className="text-[10px] tracking-[0.2em] text-slate-600 hover:text-cyan-400 transition"
            >
              ← RETURN TO LANDING
            </button>
          </div>

        </div>

        <div className="flex justify-between mt-6 px-1 text-[9px] tracking-[0.2em] text-slate-700 uppercase">
          <span>VEYTRA // SIH 2026</span>
          <span>Secure Network</span>
        </div>

      </div>
    </div>
  )
}