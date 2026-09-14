"""App-specific helpers on top of mfgkit.deltav.

Export parsing lives in mfgkit; this module only shapes its output for the
deltav_modules table and the search API.
"""

DEFAULT_COLS = [
    'name', 'desc', 'area', 'node_name', 'node_type', 'faceplate', 'detail',
    'default_display', 'area_seq', 'doid', 'uploaded'
]


def clean_deltav_df(df):
    return df[DEFAULT_COLS]
