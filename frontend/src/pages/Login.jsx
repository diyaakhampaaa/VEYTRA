import { useState } from "react"

export default function Login({ onLogin, onGoToSignup }) {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")

  function handleSubmit(e) {
    e.preventDefault()

    if (!email || !password) return

    // Temporary frontend login.
    // Real authentication will be connected to FastAPI later.
    if (onLogin) {
      onLogin()
    }
  }

  return (
    <div className="min-h-screen bg-[#02070b] text-white flex items-center justify-center relative overflow-hidden">

      {/* Background grid */}
      <div className="absolute inset-0 veytra-grid opacity-30" />

      {/* Ambient glow */}
      <div className="absolute top-[-200px] left-1/2 -translate-x-1/2 w-[600px] h-[600px] rounded-full bg-cyan-400/5 blur-[120px]" />

      <div className="relative z-10 w-full max-w-md px-6">

        {/* Logo */}
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

        {/* Login card */}
        <div className="veytra-panel veytra-hud rounded-2xl p-8">

          <div className="mb-8">
            <div className="flex items-center gap-2 text-cyan-400 text-[10px] tracking-[0.25em] uppercase mb-3">
              <span className="veytra-live-dot" />
              Authorized Access
            </div>

            <h2 className="text-2xl font-semibold">
              Welcome back.
            </h2>

            <p className="text-sm text-slate-500 mt-2">
              Sign in to access the VEYTRA command network.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">

            {/* Email */}
            <div>
              <label className="block text-[10px] tracking-[0.2em] text-slate-500 uppercase mb-2">
                Operator Email
              </label>

              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="operator@veytra.network"
                className="w-full bg-[#02070b] border border-cyan-400/10 rounded-lg px-4 py-3 text-sm text-white placeholder:text-slate-700 outline-none focus:border-cyan-400/40 transition"
              />
            </div>

            {/* Password */}
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="block text-[10px] tracking-[0.2em] text-slate-500 uppercase">
                  Access Key
                </label>

                <button
                  type="button"
                  className="text-[9px] tracking-[0.15em] text-cyan-400/70 hover:text-cyan-300 transition"
                >
                  FORGOT KEY?
                </button>
              </div>

              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-[#02070b] border border-cyan-400/10 rounded-lg px-4 py-3 text-sm text-white placeholder:text-slate-700 outline-none focus:border-cyan-400/40 transition"
              />
            </div>

            {/* Submit */}
            <button
              type="submit"
              className="w-full mt-3 bg-cyan-300 hover:bg-cyan-200 text-[#02070b] font-semibold text-xs tracking-[0.18em] py-4 rounded-lg transition"
            >
              ENTER COMMAND CENTER →
            </button>

          </form>

          {/* Signup */}
          <div className="mt-7 pt-6 border-t border-cyan-400/10 text-center">
            <p className="text-xs text-slate-600">
              New operator?
            </p>

            <button
              onClick={onGoToSignup}
              className="mt-2 text-xs text-cyan-400 hover:text-cyan-300 tracking-[0.12em] transition"
            >
              REQUEST NETWORK ACCESS →
            </button>
          </div>

        </div>

        {/* Footer */}
        <div className="flex justify-between mt-6 px-1 text-[9px] tracking-[0.2em] text-slate-700 uppercase">
          <span>VEYTRA // SIH 2026</span>
          <span>Secure Network</span>
        </div>

      </div>
    </div>
  )
}