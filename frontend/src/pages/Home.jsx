import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router'
import SearchCard from '../components/SearchCard'
import TeamCard from '../components/TeamCard'
import { fetchJson, trendUrl } from '../api'

function Home() {
  const navigate = useNavigate()
  const onSearch = (id, term) => navigate(`/search/${id}?q=${encodeURIComponent(term)}`)
  const onTrend = tags => navigate(trendUrl(tags))
  const onEos = eosType => navigate(`/gcc?eos=${encodeURIComponent(eosType)}`)

  // useState(null) means "no data yet". Once the fetch completes it becomes
  // an array of team members. We use null (not []) so we can distinguish
  // "still loading" from "loaded but empty".
  const [team, setTeam] = useState(null)
  const [teamError, setTeamError] = useState(null)

  // useEffect(fn, []) — the empty array means "run fn once, after first render".
  // This is the React equivalent of "do this when the page loads".
  useEffect(() => {
    fetchJson('/api/team')
      .then(data => setTeam(data.team))
      .catch(err => setTeamError(err.message))
  }, [])

  return (
    <main className="py-8 flex flex-col gap-10">

      {/* Search tools */}
      <section>
        <h2 className="text-lg font-semibold text-gray-700 dark:text-gray-200 mb-4">Search</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <SearchCard
            title="Intellution"
            description="Search the Argo HMI tag database"
            placeholder="e.g. V48123"
            onSearch={term => onSearch('intellution', term)}
          />
          <SearchCard
            title="DeltaV"
            description="Search the Argo DeltaV modules"
            placeholder="e.g. FV87088"
            onSearch={term => onSearch('deltav', term)}
          />
          <SearchCard
            title="DeltaV IO"
            description="Find DSTs and spare IO by controller or CIOC"
            placeholder="e.g. WMCP05"
            onSearch={term => onSearch('deltav_io', term)}
          />
          <SearchCard
            title="Aspen"
            description="Search the Argo process historian"
            placeholder="e.g. FinOil"
            onSearch={term => onSearch('aspen', term)}
          />
          <SearchCard
            title="Trend"
            description="Plot Aspen history for one or more tags"
            placeholder="e.g. FT21001"
            buttonLabel="Trend"
            onSearch={onTrend}
          />
          <SearchCard
            title="GCC"
            description="Translate end of step codes and read truthtables"
            placeholder="EOS type, e.g. 21"
            buttonLabel="Translate"
            onSearch={onEos}
          />
        </div>
      </section>

      {/* Team */}
      <section>
        <h2 className="text-lg font-semibold text-gray-700 dark:text-gray-200 mb-4">Controls Team</h2>

        {teamError && (
          <p className="text-red-500 text-sm">Failed to load team: {teamError}</p>
        )}

        {/* null = still loading, [] = loaded but empty, [...] = has members */}
        {team === null && !teamError && (
          <p className="text-gray-400 dark:text-gray-500 text-sm">Loading...</p>
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
  )
}

export default Home
