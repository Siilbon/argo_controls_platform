"""App-specific helpers on top of mfgkit.deltav.

Export parsing lives in mfgkit; this module only shapes its output for the
deltav_modules and deltav_io tables and the search APIs.
"""

import pandas as pd

DEFAULT_COLS = [
    'system', 'name', 'desc', 'area', 'node_name', 'node_type', 'faceplate', 'detail',
    'default_display', 'area_seq', 'doid', 'uploaded'
]

IO_COLS = [
    'system', 'status', 'controller', 'card_slot', 'position', 'tag', 'description',
    'enabled', 'io_type', 'card_definition', 'channel_definition',
    'controller_assignment', 'subsystem', 'uploaded'
]

# DeltaV names an unassigned channel's DST after its location, e.g. WMCP04C12CH07
DEFAULT_DST_PATTERN = r'\w*C\d{2}CH\d{2}'


def clean_deltav_df(df):
    return df[DEFAULT_COLS]


def io_status(df):
    """Label each IO channel for finding spares.

    Spare    - no DST (or the default location-named DST) and disabled,
               or an empty CHARM slot
    Disabled - a real DST, but the channel is disabled (possibly reclaimable)
    No DST   - enabled with no real DST; worth checking
    Assigned - enabled with a real DST
    """
    no_dst = (df['tag'] == '') | df['tag'].str.fullmatch(DEFAULT_DST_PATTERN)
    undefined = df['card_definition'] == 'CHMIO_UNDEFINED_CHARM'
    enabled = df['enabled'].fillna(False).astype(bool)

    status = pd.Series('Assigned', index=df.index)
    status[enabled & no_dst] = 'No DST'
    status[~enabled & ~no_dst] = 'Disabled'
    status[(~enabled & no_dst) | undefined] = 'Spare'
    return status


def clean_io_df(df):
    df = df.copy()
    df['status'] = io_status(df)
    return df[IO_COLS]
