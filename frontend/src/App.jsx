import { useState } from 'react'
import Home from './pages/Home'
import SearchResults from './pages/SearchResults'

// Everything the shared results page needs to know about each search.
// `id` must match the key; it's also used for saved column choices and CSV names.
const SEARCHES = {
  intellution: {
    id: 'intellution',
    title: 'Intellution',
    endpoint: '/api/intellution',
    defaultColumn: 'tag',
    searchColumns: [
      'database', 'name', 'tag', 'desc', 'ft_topic', 'ioad', 'source', 'opc_topic',
      'ienab', 'opendesc', 'closedesc', 'pri', 'sa1', 'sa2', 'sa3',
      'all_areas', 'almext1', 'almext2', 'prefix', 'loop', 'suffix',
      'alias_root', 'alias_field', 'alias_rest',
    ],
  },
  deltav: {
    id: 'deltav',
    title: 'DeltaV',
    endpoint: '/api/deltav',
    defaultColumn: 'name',
    searchColumns: [
      'name', 'desc', 'area', 'node_name', 'node_type', 'faceplate', 'detail',
      'default_display',
    ],
  },
}

// App is the root of the component tree.
// For now a piece of state decides which page to render. Once there are
// more pages (Aspen results, etc.) a router can replace this.
function App() {
  // null = show Home; { system, term, col } = show that search's results
  const [search, setSearch] = useState(null)

  if (search) {
    const config = SEARCHES[search.system]
    return (
      <SearchResults
        // A new key makes React throw away the old page and start fresh
        key={`${search.system}:${search.col}:${search.term}`}
        config={config}
        term={search.term}
        col={search.col}
        onSearch={(term, col) => setSearch({ ...search, term, col })}
        onBack={() => setSearch(null)}
      />
    )
  }

  // Home calls this with the system id ('intellution', 'deltav') and the term
  function startSearch(system, term) {
    setSearch({ system, term, col: SEARCHES[system].defaultColumn })
  }

  return <Home onSearch={startSearch} />
}

export default App
