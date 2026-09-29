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
export default function SignUp({
  onSignup,
  onGoToLogin,
  onBack,
}) {
  const [name, setName] = useState("")
  const [city, setCity] = useState("delhi")
  const [role, setRole] = useState("operator")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")

  function handleSubmit(e) {
    e.preventDefault()

    if (
      !name ||
      !city ||
      !role ||
      !email ||
      !password ||
      !confirmPassword
    ) {
      return
    }

    if (password !== confirmPassword) {
      alert("Passwords do not match.")
      return
    }

    /*
     * TEMPORARY FRONTEND AUTH CONTEXT
     *
     * Real account creation will be connected to FastAPI next.
     */
    if (onSignup) {
      onSignup({
        name,
        email,
        role,
        city,
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
        <div className="text-center mb-7">

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

        {/* Signup card */}
        <div className="veytra-panel veytra-hud rounded-2xl p-7">

          <div className="mb-6">

            <div className="flex items-center gap-2 text-cyan-400 text-[10px] tracking-[0.25em] uppercase mb-2">
              <span className="veytra-live-dot" />
              Network Registration
            </div>

            <h2 className="text-2xl font-semibold">
              Create account
            </h2>

          </div>

          <form onSubmit={handleSubmit} className="space-y-4">

            {/* Name */}
            <div>
              <label className="block text-[10px] tracking-[0.2em] text-slate-500 uppercase mb-2">
                Name
              </label>

              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Enter your name"
                className="w-full bg-[#02070b] border border-cyan-400/10 rounded-lg px-4 py-3 text-sm text-white placeholder:text-slate-700 outline-none focus:border-cyan-400/40 transition"
              />
            </div>

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
                placeholder="Create a password"
                className="w-full bg-[#02070b] border border-cyan-400/10 rounded-lg px-4 py-3 text-sm text-white placeholder:text-slate-700 outline-none focus:border-cyan-400/40 transition"
              />
            </div>

            {/* Confirm */}
            <div>
              <label className="block text-[10px] tracking-[0.2em] text-slate-500 uppercase mb-2">
                Confirm Password
              </label>

              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Confirm password"
                className="w-full bg-[#02070b] border border-cyan-400/10 rounded-lg px-4 py-3 text-sm text-white placeholder:text-slate-700 outline-none focus:border-cyan-400/40 transition"
              />
            </div>

            {/* Submit */}
            <button
              type="submit"
              className="w-full mt-2 py-4 rounded-lg bg-cyan-300 text-[#02070b] text-xs font-semibold tracking-[0.18em] hover:bg-cyan-200 transition"
            >
              CREATE ACCOUNT →
            </button>

          </form>

          {/* Login */}
          <div className="mt-6 pt-5 border-t border-cyan-400/10 text-center">

            <p className="text-xs text-slate-600">
              Already have an account?
            </p>

            <button
              onClick={onGoToLogin}
              className="mt-2 text-xs tracking-[0.12em] text-cyan-400 hover:text-cyan-300 transition"
            >
              RETURN TO LOGIN
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