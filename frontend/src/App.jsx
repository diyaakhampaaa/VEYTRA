import { useState } from "react"

import Sidebar from "./components/Sidebar"

import LandingPage from "./pages/LandingPage"
import AuthChoice from "./pages/AuthChoice"
import Login from "./pages/Login"
import Signup from "./pages/Signup"

import CommandCenter from "./pages/CommandCenter"
import VehicleSearch from "./pages/VehicleSearch"
import SmartVerification from "./pages/SmartVerification"
import TrafficAnalytics from "./pages/TrafficAnalytics"
import Alerts from "./pages/Alerts"
import SimulationComparison from "./pages/SimulationComparison"


function App() {
  // --------------------------------
  // APPLICATION STATE
  // --------------------------------

  const [isEntered, setIsEntered] = useState(false)
  const [isLoggedIn, setIsLoggedIn] = useState(false)

  // Controls the authentication screen:
  // "choice" → choose Login or Signup
  // "login"  → Login page
  // "signup" → Signup page
  const [authPage, setAuthPage] = useState("choice")

  // Stores the page the user wanted to visit
  // before authentication.
  const [pendingPage, setPendingPage] = useState("command")

  // Current dashboard page
  const [activePage, setActivePage] = useState("command")


  // --------------------------------
  // DASHBOARD PAGE ROUTER
  // --------------------------------

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


  // --------------------------------
  // LANDING PAGE
  // --------------------------------

  if (!isEntered) {
    return (
      <LandingPage

        // Authorized Access button
        onEnter={() => {
          setIsEntered(true)
          setAuthPage("choice")
        }}

        // Landing-page navigation
        onNavigate={(page) => {
          setPendingPage(page)
          setIsEntered(true)
          setAuthPage("choice")
        }}

      />
    )
  }


  // --------------------------------
  // AUTHENTICATION
  // --------------------------------

  if (!isLoggedIn) {

    // ==============================
    // LOGIN / SIGNUP CHOICE
    // ==============================

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


    // ==============================
    // LOGIN
    // ==============================

    if (authPage === "login") {
      return (
        <Login

          onLogin={() => {
            setIsLoggedIn(true)

            // Take the user to the page
            // they originally selected.
            setActivePage(pendingPage)
          }}

          onGoToSignup={() => {
            setAuthPage("signup")
          }}

        />
      )
    }


    // ==============================
    // SIGNUP
    // ==============================

    if (authPage === "signup") {
      return (
        <Signup

          onSignup={() => {
            setIsLoggedIn(true)

            // Take the new user to the
            // page they originally selected.
            setActivePage(pendingPage)
          }}

          onGoToLogin={() => {
            setAuthPage("login")
          }}

        />
      )
    }
  }


  // --------------------------------
  // VEYTRA DASHBOARD
  // --------------------------------

  return (
    <div className="flex min-h-screen bg-slate-950 text-white">

      <Sidebar
        activePage={activePage}
        setActivePage={setActivePage}
      />

      <main className="flex-1 p-10">
        {renderPage()}
      </main>

    </div>
  )
}


export default App