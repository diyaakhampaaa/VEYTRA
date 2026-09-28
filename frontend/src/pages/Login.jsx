import { useState } from "react"

const ROLES = [
  {
    value: "admin",
    label: "Administrator",
  },
  {
    value: "operator",
    label: "Traffic Operator",
  },
  {
    value: "analyst",
    label: "Traffic Analyst",
  },
  {
    value: "supervisor",
    label: "Control Room Supervisor",
  },
  {
    value: "enforcement",
    label: "Traffic Enforcement Officer",
  },
  {
    value: "emergency",
    label: "Emergency Response Coordinator",
  },
  {
    value: "planner",
    label: "City Mobility Planner",
  },
]

const CITIES = [
  {
    value: "delhi",
    label: "Delhi",
  },
  {
    value: "bangalore",
    label: "Bangalore",
  },
  {
    value: "mumbai",
    label: "Mumbai",
  },
  {
    value: "bhopal",
    label: "Bhopal",
  },
  {
    value: "hyderabad",
    label: "Hyderabad",
  },
  {
    value: "chennai",
    label: "Chennai",
  },
  {
    value: "kolkata",
    label: "Kolkata",
  },
  {
    value: "pune",
    label: "Pune",
  },
  {
    value: "ahmedabad",
    label: "Ahmedabad",
  },
  {
    value: "jaipur",
    label: "Jaipur",
  },
]

export default function Login({ onLogin, onGoToSignup, onBack }) {
  const [city, setCity] = useState("delhi")
  const [role, setRole] = useState("operator")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")

  function handleSubmit(e) {
    e.preventDefault()

    if (!city || !role || !email || !password) {
      return
    }

    /*
     * TEMPORARY FRONTEND AUTH CONTEXT
     *
     * Backend authentication will replace this later.
     * The selected role will NOT be trusted by the backend.
     */
    if (onLogin) {
      onLogin({
        email,
        role,
        city,
        name: email.split("@")[0],
      })
    }
  }

  return (
    <div className="min-h-screen bg-[#02070b] text-white flex items-center justify-center relative overflow-hidden">

      {/* Background */}
      <div className="absolute inset-0 veytra-grid opacity-30" />

      {/* Ambient glow */}
      <div className="absolute top-[-200px] left-1/2 -translate-x-1/2 w-[600px] h-[600px] rounded-full bg-cyan-400/5 blur-[120px]" />

      <div className="relative z-10 w-full max-w-md px-6">

        {/* Logo */}
        <div className="text-center mb-8">

          <div className="flex justify-center mb-4">
            <div className="w-14 h-14 rounded-xl border border-cyan-400/30 bg-cyan-400/5 flex items-center justify-center veytra-glow">
              <div className="w-7 h-7 border border-cyan-300/70 rotate-45 flex items-center justify-center">
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
        <div className="veytra-panel veytra-hud rounded-2xl p-7">

          <div className="mb-6">

            <div className="flex items-center gap-2 text-cyan-400 text-[10px] tracking-[0.25em] uppercase mb-2">
              <span className="veytra-live-dot" />
              Authorized Access
            </div>

            <h2 className="text-2xl font-semibold">
              Sign in
            </h2>

          </div>

          <form onSubmit={handleSubmit} className="space-y-4">

            {/* City */}
            <div>
              <label className="block text-[10px] tracking-[0.2em] text-slate-500 uppercase mb-2">
                Analysis City
              </label>

              <select
                value={city}
                onChange={(e) => setCity(e.target.value)}
                className="w-full bg-[#02070b] border border-cyan-400/10 rounded-lg px-4 py-3 text-sm text-white outline-none focus:border-cyan-400/40 transition"
              >
                {CITIES.map((item) => (
                  <option
                    key={item.value}
                    value={item.value}
                    className="bg-[#02070b]"
                  >
                    {item.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Role */}
            <div>
              <label className="block text-[10px] tracking-[0.2em] text-slate-500 uppercase mb-2">
                Role
              </label>

              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full bg-[#02070b] border border-cyan-400/10 rounded-lg px-4 py-3 text-sm text-white outline-none focus:border-cyan-400/40 transition"
              >
                {ROLES.map((item) => (
                  <option
                    key={item.value}
                    value={item.value}
                    className="bg-[#02070b]"
                  >
                    {item.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Email */}
            <div>
              <label className="block text-[10px] tracking-[0.2em] text-slate-500 uppercase mb-2">
                Email
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
              <label className="block text-[10px] tracking-[0.2em] text-slate-500 uppercase mb-2">
                Password
              </label>

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
              className="w-full mt-2 bg-cyan-300 hover:bg-cyan-200 text-[#02070b] font-semibold text-xs tracking-[0.18em] py-4 rounded-lg transition"
            >
              SIGN IN →
            </button>

          </form>

          {/* Signup */}
          <div className="mt-6 pt-5 border-t border-cyan-400/10 text-center">

            <p className="text-xs text-slate-600">
              Don't have an account?
            </p>

            <button
              onClick={onGoToSignup}
              className="mt-2 text-xs text-cyan-400 hover:text-cyan-300 tracking-[0.12em] transition"
            >
              CREATE ACCOUNT
            </button>

          </div>

          {/* Back */}
          <button
            onClick={onBack}
            className="w-full mt-4 text-[9px] tracking-[0.18em] text-slate-600 hover:text-slate-400 uppercase transition"
          >
            ← Back to Landing
          </button>

        </div>

        {/* Footer */}
        <div className="flex justify-between mt-5 px-1 text-[9px] tracking-[0.2em] text-slate-700 uppercase">
          <span>VEYTRA // SIH 2026</span>
          <span>Secure Network</span>
        </div>

      </div>
    </div>
  )
}