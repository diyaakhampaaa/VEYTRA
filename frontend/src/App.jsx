import { useState } from "react"

import Sidebar from "./components/Sidebar"
import TopBar from "./components/TopBar"

import LandingPage from "./pages/LandingPage"
import AuthChoice from "./pages/AuthChoice"
import Login from "./pages/Login"
import SignUp from "./pages/SignUp"

import CommandCenter from "./pages/CommandCenter"
import VehicleSearch from "./pages/VehicleSearch"
import SmartVerification from "./pages/SmartVerification"
import TrafficAnalytics from "./pages/TrafficAnalytics"
import Alerts from "./pages/Alerts"
import SimulationComparison from "./pages/SimulationComparison"

function App() {
  const [isEntered, setIsEntered] = useState(false)
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [authPage, setAuthPage] = useState("choice")
  const [pendingPage, setPendingPage] = useState("command")
  const [activePage, setActivePage] = useState("command")

  const renderPage = () => {
    switch (activePage) {
      case "vehicles":
        return <VehicleSearch />

      case "verification":
        return <SmartVerification />

      case "analytics":
        return <TrafficAnalytics />

      case "alerts":
        return <Alerts />

      case "simulation":
        return <SimulationComparison />

      case "command":
      default:
        return <CommandCenter />
    }
  }

  if (!isEntered) {
    return (
      <LandingPage
        onEnter={() => {
          setIsEntered(true)
          setAuthPage("choice")
        }}
        onNavigate={(page) => {
          setPendingPage(page)
          setIsEntered(true)
          setAuthPage("choice")
        }}
      />
    )
  }

  if (!isLoggedIn) {
    if (authPage === "choice") {
      return (
        <AuthChoice
          onLogin={() => {
            setAuthPage("login")
          }}
          onSignup={() => {
            setAuthPage("signup")
          }}
          onBack={() => {
            setIsEntered(false)
          }}
        />
      )
    }

    if (authPage === "login") {
      return (
        <Login
          onLogin={() => {
            setIsLoggedIn(true)
            setActivePage(pendingPage)
          }}
          onGoToSignup={() => {
            setAuthPage("signup")
          }}
        />
      )
    }

    if (authPage === "signup") {
      return (
        <SignUp
          onSignup={() => {
            setIsLoggedIn(true)
            setActivePage(pendingPage)
          }}
          onGoToLogin={() => {
            setAuthPage("login")
          }}
        />
      )
    }
  }

  return (
    <div className="min-h-screen bg-[var(--veytra-bg)] text-[var(--veytra-text)]">
      {/* TOP SYSTEM BAR */}
      <TopBar activePage={activePage} />

      {/* SIDEBAR + MAIN CONTENT */}
      <div className="flex min-h-[calc(100vh-88px)]">
        <Sidebar
          activePage={activePage}
          setActivePage={setActivePage}
        />

        <main className="min-w-0 flex-1 px-8 py-7 lg:px-10">
          {renderPage()}
        </main>
      </div>
    </div>
  )
}

export default App