import { useState } from "react"

import Sidebar from "./components/Sidebar"
import TopBar from "./components/TopBar"

import LandingPage from "./pages/LandingPage"
import Login from "./pages/Login"
import SignUp from "./pages/SignUp"

import CommandCenter from "./pages/CommandCenter"
import VehicleSearch from "./pages/VehicleSearch"
import SmartVerification from "./pages/SmartVerification"
import TrafficAnalytics from "./pages/TrafficAnalytics"
import Alerts from "./pages/Alerts"

function App() {
  const [isEntered, setIsEntered] = useState(false)
  const [isLoggedIn, setIsLoggedIn] = useState(false)

  const [pendingPage, setPendingPage] = useState("command")
  const [activePage, setActivePage] = useState("command")

  const [authPage, setAuthPage] = useState("login")

  const [currentUser, setCurrentUser] = useState(null)

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

      case "command":
      default:
        return <CommandCenter />
    }
  }

  // --------------------------------------------------
  // LANDING PAGE
  // --------------------------------------------------

  if (!isEntered) {
    return (
      <LandingPage
        onEnter={() => {
          setIsEntered(true)
          setAuthPage("login")
        }}
        onNavigate={(page) => {
          setPendingPage(page)
          setIsEntered(true)
          setAuthPage("login")
        }}
      />
    )
  }

  // --------------------------------------------------
  // AUTHENTICATION
  // --------------------------------------------------

  if (!isLoggedIn) {
    if (authPage === "login") {
      return (
        <Login
          onLogin={(user) => {
            setCurrentUser(user)
            setIsLoggedIn(true)
            setActivePage(pendingPage)
          }}
          onGoToSignup={() => {
            setAuthPage("signup")
          }}
          onBack={() => {
            setIsEntered(false)
          }}
        />
      )
    }

    if (authPage === "signup") {
      return (
        <SignUp
          onSignup={(user) => {
            setCurrentUser(user)
            setIsLoggedIn(true)
            setActivePage(pendingPage)
          }}
          onGoToLogin={() => {
            setAuthPage("login")
          }}
          onBack={() => {
            setIsEntered(false)
          }}
        />
      )
    }
  }

  // --------------------------------------------------
  // MAIN DASHBOARD
  // --------------------------------------------------

  return (
    <div className="min-h-screen bg-[var(--veytra-bg)] text-[var(--veytra-text)]">

      <TopBar
        activePage={activePage}
        user={currentUser}
      />

      <div className="flex min-h-[calc(100vh-88px)]">

        <Sidebar
          activePage={activePage}
          setActivePage={setActivePage}
          user={currentUser}
        />

        <main className="min-w-0 flex-1 px-8 py-7 lg:px-10">
          {renderPage()}
        </main>

      </div>
    </div>
  )
}

export default App