"""App-specific helpers on top of mfgkit.aspen.

Queries live in mfgkit; this module holds the search table settings, parses
tag lists, and shapes history for the trend API.
"""

import math
from datetime import datetime, timedelta

import pandas as pd

# Each searchable Aspen table: the mfgkit method arguments and the fields the
# API allows searching on. Keep in sync with the aspen entry in frontend/src/App.jsx.
SEARCH_TABLES = {
    'analog': {
        'method': 'search_tags', 'table': 'IP_AnalogDef',
        'fields': ['NAME', 'IP_DESCRIPTION', 'IP_ENG_UNITS'],
    },
    'discrete': {
        'method': 'search_tags', 'table': 'IP_DiscreteDef',
        'fields': ['NAME', 'IP_DESCRIPTION'],
    },
    'iogetdef': {
        'method': 'search_io_defs', 'table': 'IOGetDef',
        'fields': ['IO_TAGNAME', 'NAME', 'IO_VALUE_RECORD&&FLD'],
    },
    'iogethistdef': {
        'method': 'search_io_defs', 'table': 'IOGetHistDef',
        'fields': ['IO_TAGNAME', 'NAME', 'IO_VALUE_RECORD&&FLD'],
    },
}

# Roughly how many points each trend line gets; the interpolation period is
# picked to hit this so long ranges stay quick to pull and draw
TREND_POINTS = 1000
MAX_TREND_TAGS = 20
MAX_TREND_DAYS = 366

# Tags per OPC UA node ID request; each chunk of 200 costs one All_Records query
MAX_NODEID_TAGS = 500


def trend_window(hours=None, start=None, end=None, now=None):
    """Resolve the trend time range from either hours back or start/end strings.

    Times are naive and in the Aspen server's local time, which is what IP21
    returns. Raises ValueError for a missing, reversed or too-long range.
    """
    if start and end:
        start, end = pd.to_datetime(start).to_pydatetime(), pd.to_datetime(end).to_pydatetime()
    elif hours:
        end = now or datetime.now()
        start = end - timedelta(hours=float(hours))
    else:
        raise ValueError('Pass hours, or both start and end')

    if end <= start:
        raise ValueError('End must be after start')
    if end - start > timedelta(days=MAX_TREND_DAYS):
        raise ValueError(f'Trend range can be at most {MAX_TREND_DAYS} days')
    return start, end


def trend_period_seconds(start, end, points=TREND_POINTS):
    """Interpolation period that gives about `points` values across the range."""
    return max(1, math.ceil((end - start).total_seconds() / points))


def parse_tags(values, max_tags, action='Look up'):
    """Tags from repeated and/or comma- or whitespace-separated query args, de-duplicated in order."""
    tags = []
    for value in values:
        for tag in value.replace(',', ' ').split():
            if tag not in tags:
                tags.append(tag)
    if not tags:
        raise ValueError('Pass at least one tag')
    if len(tags) > max_tags:
        raise ValueError(f'{action} at most {max_tags} tags at once')
    return tags


def parse_trend_tags(values):
    return parse_tags(values, MAX_TREND_TAGS, 'Trend')


def trend_to_json(wide, tags):
    """Turn a wide history frame (TS index x tag columns) into trend JSON.

    Numeric tags come back as numbers. A tag with no numeric values (e.g. a
    discrete state like "RUNNING") keeps its text values. Tags with no history
    at all are listed in `missing`.
    """
    ts = [] if wide.empty else wide.index.strftime('%Y-%m-%dT%H:%M:%S').tolist()
    series, missing = [], []
    for tag in tags:
        if tag not in wide.columns or wide[tag].isna().all():
            missing.append(tag)
            continue
        raw = wide[tag]
        numeric = pd.to_numeric(raw, errors='coerce')
        values = numeric if numeric.notna().any() else raw
        # Cast to object so gaps become None (null in JSON) rather than NaN
        values = values.astype(object).where(values.notna(), None).tolist()
        series.append({'tag': tag, 'values': values})
    return {'ts': ts, 'series': series, 'missing': missing}
