import { useState, useEffect } from 'react'
import SearchCard from '../components/SearchCard'
import TeamCard from '../components/TeamCard'

function Home() {
  // useState(null) means "no data yet". Once the fetch completes it becomes
  // an array of team members. We use null (not []) so we can distinguish
  // "still loading" from "loaded but empty".
  const [team, setTeam] = useState(null)
  const [teamError, setTeamError] = useState(null)

  // useEffect(fn, []) — the empty array means "run fn once, after first render".
  // This is the React equivalent of "do this when the page loads".
  useEffect(() => {
    fetch('/api/team')
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json()
      })
      .then(data => setTeam(data.team))
      .catch(err => setTeamError(err.message))
  }, [])

  function handleIntelSearch(term) {
    // TODO: navigate to Intellution results page
    console.log('Intellution search:', term)
  }

  function handleAspenSearch(term) {
    // TODO: navigate to Aspen results page
    console.log('Aspen search:', term)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <h1 className="text-2xl font-bold text-gray-800">Argo Controls Platform</h1>
        <p className="text-sm text-gray-500 mt-1">
          Python utilities for Argo control systems
        </p>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-8 flex flex-col gap-10">

        {/* Search tools */}
        <section>
          <h2 className="text-lg font-semibold text-gray-700 mb-4">Search</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <SearchCard
              title="Intellution"
              description="Search the Argo HMI tag database"
              placeholder="e.g. V48123"
              onSearch={handleIntelSearch}
            />
            <SearchCard
              title="Aspen"
              description="Search the Argo process historian"
              placeholder="e.g. FinOil"
              onSearch={handleAspenSearch}
            />
          </div>
        </section>

        {/* Team */}
        <section>
          <h2 className="text-lg font-semibold text-gray-700 mb-4">Controls Team</h2>

          {teamError && (
            <p className="text-red-500 text-sm">Failed to load team: {teamError}</p>
          )}

          {/* null = still loading, [] = loaded but empty, [...] = has members */}
          {team === null && !teamError && (
            <p className="text-gray-400 text-sm">Loading...</p>
          )}

          {team !== null && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {team.map(member => (
                // key tells React which card is which when the list re-renders
                <TeamCard key={member.id} member={member} />
              ))}
            </div>
          )}
        </section>

      </main>
    </div>
  )
}

export default Home
