from flask import Blueprint, jsonify, current_app, request
from mfgkit.aspen import AspenConn
from acp_app import limiter
from acp_app.services.common import df_to_records
from acp_app.services.aspen import (SEARCH_TABLES, parse_trend_tags, trend_period_seconds,
                                    trend_to_json, trend_window)

bp = Blueprint('api_aspen', __name__)


def _aspen_rate_limit():
    return current_app.config['ASPEN_RATE_LIMIT']


def _connect(**kwargs):
    """Open an Aspen connection with the configured server and timeout."""
    return AspenConn(current_app.config.get('ASPEN_SERVER'),
                     timeout=current_app.config['ASPEN_TIMEOUT'], **kwargs)


def _connection_error():
    current_app.logger.exception('Aspen request failed')
    server = current_app.config.get('ASPEN_SERVER')
    return jsonify({'error': f'Unable to connect to Aspen server: {server}'}), 503


@bp.route('/api/aspen/status')
@limiter.limit(_aspen_rate_limit)
def aspen_status():
    try:
        with _connect() as conn:
            return jsonify({'status': df_to_records(conn.io_task_status())})
    except Exception:
        return _connection_error()


@bp.route('/api/aspen/trend')
@limiter.limit(_aspen_rate_limit)
def aspen_trend():
    """Interpolated history for trending.

    Query args: tags (repeat or comma-separate), and either hours (back from
    now) or start and end (e.g. 2026-09-14T06:00, Aspen server local time).
    """
    try:
        tags = parse_trend_tags(request.args.getlist('tags'))
        start, end = trend_window(request.args.get('hours'),
                                  request.args.get('start'), request.args.get('end'))
    except ValueError as err:
        return jsonify({'error': str(err)}), 400

    period = trend_period_seconds(start, end)
    # One date chunk covers the whole range; TREND_POINTS keeps it well under MAX_ROWS
    chunk_days = (end - start).total_seconds() / 86400 + 1

    try:
        with _connect() as conn:
            wide = conn.interpolated(tags, start, end, period_seconds=period,
                                     chunk_days=chunk_days)
    except ValueError as err:  # a tag name mfgkit won't send to SQLplus
        return jsonify({'error': str(err)}), 400
    except Exception:
        return _connection_error()

    return jsonify({
        **trend_to_json(wide, tags),
        'start': start.strftime('%Y-%m-%dT%H:%M:%S'),
        'end': end.strftime('%Y-%m-%dT%H:%M:%S'),
        'period_seconds': period,
    })


# Flask matches the fixed routes above (status, trend) before this one
@bp.route('/api/aspen/<table>/<search_term>')
@limiter.limit(_aspen_rate_limit)
def aspen_table_search(table, search_term):
    settings = SEARCH_TABLES.get(table)
    if settings is None:
        return jsonify({'error': f'Invalid table: {table}'}), 400

    col = request.args.get('col', settings['fields'][0])
    if col not in settings['fields']:
        return jsonify({'error': f'Invalid column: {col}'}), 400

    max_rows = current_app.config['ASPEN_SEARCH_MAX_ROWS']
    try:
        # One extra row tells us the search was cut off. SET MAX_ROWS makes the
        # Aspen server stop there, so a broad search like "A" stays cheap.
        with _connect(max_rows=max_rows + 1) as conn:
            search = getattr(conn, settings['method'])
            df = search(search_term, field=col, table=settings['table'])
    except ValueError as err:  # e.g. a search term with characters SQLplus can't take
        return jsonify({'error': str(err)}), 400
    except Exception:
        return _connection_error()

    # Also trim here in case the server ignored SET MAX_ROWS
    truncated = len(df) > max_rows
    df = df.head(max_rows)

    return jsonify({
        'data': df_to_records(df),
        'total': len(df),
        'truncated': truncated,
        'max_rows': max_rows,
        'search_term': search_term,
        'col': col,
    })
