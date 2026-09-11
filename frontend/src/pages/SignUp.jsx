import { useState } from "react"

export default function Signup({ onSignup, onGoToLogin }) {
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")

  function handleSubmit(e) {
    e.preventDefault()

    if (!name || !email || !password || !confirmPassword) return

    if (password !== confirmPassword) {
      alert("Access keys do not match.")
      return
    }

    // Temporary frontend-only signup.
    // Real authentication will be connected to FastAPI later.
    if (onSignup) onSignup()
  }

  return (
    <div className="min-h-screen bg-[#02070b] text-white flex items-center justify-center relative overflow-hidden">

      {/* Background */}
      <div className="absolute inset-0 veytra-grid opacity-30" />

      <div className="absolute top-[-200px] left-1/2 -translate-x-1/2 w-[600px] h-[600px] rounded-full bg-cyan-400/5 blur-[120px]" />

      <div className="relative z-10 w-full max-w-md px-6">

        {/* Logo */}
        <div className="text-center mb-8">

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


        {/* Signup Card */}
        <div className="veytra-panel veytra-hud rounded-2xl p-8">

          <div className="mb-7">

            <div className="flex items-center gap-2 text-cyan-400 text-[10px] tracking-[0.25em] uppercase mb-3">
              <span className="veytra-live-dot" />
              Network Registration
            </div>

            <h2 className="text-2xl font-semibold">
              Create your account.
            </h2>

            <p className="text-sm text-slate-500 mt-2">
              Register as an authorized VEYTRA operator.
            </p>

          </div>


          <form onSubmit={handleSubmit} className="space-y-5">

            {/* Name */}
            <div>
              <label className="block text-[10px] tracking-[0.2em] text-slate-500 uppercase mb-2">
                Operator Name
              </label>

              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Enter your name"
                className="w-full bg-black/20 border border-cyan-400/10 rounded-lg px-4 py-3 text-sm text-white placeholder-slate-700 outline-none focus:border-cyan-400/40 transition"
              />
            </div>


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
                className="w-full bg-black/20 border border-cyan-400/10 rounded-lg px-4 py-3 text-sm text-white placeholder-slate-700 outline-none focus:border-cyan-400/40 transition"
              />
            </div>


            {/* Password */}
            <div>
              <label className="block text-[10px] tracking-[0.2em] text-slate-500 uppercase mb-2">
                Access Key
              </label>

              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Create an access key"
                className="w-full bg-black/20 border border-cyan-400/10 rounded-lg px-4 py-3 text-sm text-white placeholder-slate-700 outline-none focus:border-cyan-400/40 transition"
              />
            </div>


            {/* Confirm Password */}
            <div>
              <label className="block text-[10px] tracking-[0.2em] text-slate-500 uppercase mb-2">
                Confirm Access Key
              </label>

              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Confirm your access key"
                className="w-full bg-black/20 border border-cyan-400/10 rounded-lg px-4 py-3 text-sm text-white placeholder-slate-700 outline-none focus:border-cyan-400/40 transition"
              />
            </div>


            {/* Submit */}
            <button
              type="submit"
              className="w-full py-3.5 rounded-lg bg-cyan-400 text-[#02070b] text-xs font-semibold tracking-[0.18em] hover:bg-cyan-300 transition shadow-[0_0_25px_rgba(34,211,238,0.15)]"
            >
              CREATE OPERATOR ACCOUNT →
            </button>

          </form>


          {/* Login */}
          <div className="mt-7 pt-6 border-t border-cyan-400/10 text-center">

            <p className="text-xs text-slate-600 mb-2">
              Already registered?
            </p>

            <button
              onClick={onGoToLogin}
              className="text-[10px] tracking-[0.2em] text-cyan-400 hover:text-cyan-300 transition"
            >
              RETURN TO LOGIN →
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