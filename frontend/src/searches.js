// Search definitions shared by the router (App.jsx), the nav bar and the results page.

// Everything the shared results page needs to know about each search.
// `id` must match the key; it's also used in the URL (/search/<id>), saved column
// choices and CSV names. `dataset` names the /api/datasets entry whose load time
// is shown on the results page.
export const SEARCHES = {
  intellution: {
    id: 'intellution',
    title: 'Intellution',
    endpoint: '/api/intellution',
    dataset: 'intellution',
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
    dataset: 'deltav',
    defaultColumn: 'name',
    searchColumns: [
      'system', 'name', 'desc', 'area', 'node_name', 'node_type', 'faceplate', 'detail',
      'default_display',
    ],
  },
  deltav_io: {
    id: 'deltav_io',
    title: 'DeltaV IO',
    endpoint: '/api/deltav-io',
    dataset: 'deltav_io',
    defaultColumn: 'controller',
    searchColumns: [
      'controller', 'tag', 'description', 'status', 'system', 'card_slot', 'position',
      'io_type', 'card_definition', 'channel_definition', 'controller_assignment',
    ],
  },
  // Keep tables in sync with SEARCH_TABLES in acp_app/services/aspen.py
  aspen: {
    id: 'aspen',
    title: 'Aspen',
    tables: [
      {
        id: 'analog',
        label: 'IP_AnalogDef',
        endpoint: '/api/aspen/analog',
        defaultColumn: 'NAME',
        searchColumns: ['NAME', 'IP_DESCRIPTION', 'IP_ENG_UNITS'],
        trendTag: row => row.NAME,
      },
      {
        id: 'discrete',
        label: 'IP_DiscreteDef',
        endpoint: '/api/aspen/discrete',
        defaultColumn: 'NAME',
        searchColumns: ['NAME', 'IP_DESCRIPTION'],
        trendTag: row => row.NAME,
      },
      {
        id: 'iogetdef',
        label: 'IOGetDef',
        endpoint: '/api/aspen/iogetdef',
        defaultColumn: 'IO_TAGNAME',
        searchColumns: ['IO_TAGNAME', 'NAME', 'IO_VALUE_RECORD&&FLD'],
      },
      {
        id: 'iogethistdef',
        label: 'IOGetHistDef',
        endpoint: '/api/aspen/iogethistdef',
        defaultColumn: 'IO_TAGNAME',
        searchColumns: ['IO_TAGNAME', 'NAME', 'IO_VALUE_RECORD&&FLD'],
      },
    ],
  },
}

// Pages listed in the nav bar, in order
export const NAV_LINKS = [
  { to: '/', label: 'Home' },
  ...Object.values(SEARCHES).map(s => ({ to: `/search/${s.id}`, label: s.title })),
  { to: '/trend', label: 'Trend' },
  { to: '/gcc', label: 'GCC' },
  { to: '/nodeid', label: 'Node IDs' },
  { to: '/status', label: 'Status' },
]
