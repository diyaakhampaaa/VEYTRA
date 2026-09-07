import { useState } from "react"

import Sidebar from "./components/Sidebar"

import CommandCenter from "./pages/CommandCenter"
import VehicleSearch from "./pages/VehicleSearch"
import SmartVerification from "./pages/SmartVerification"
import TrafficAnalytics from "./pages/TrafficAnalytics"
import Alerts from "./pages/Alerts"
import SimulationComparison from "./pages/SimulationComparison"

function App() {
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