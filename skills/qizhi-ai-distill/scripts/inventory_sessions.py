#!/usr/bin/env python3
"""Read recorder sessions without changing SQLite; compute per-room daily ordinal before filtering."""
import argparse
import datetime as dt
import json
from pathlib import Path
import sqlite3
from zoneinfo import ZoneInfo


def inventory(db, live_id, since=None, until=None, timezone='Asia/Shanghai'):
    tz = ZoneInfo(timezone)
    if since and until and since > until:
        raise ValueError('--since must not be after --until')
    counts, result = {}, []
    with sqlite3.connect(Path(db).resolve().as_uri() + '?mode=ro', uri=True) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute('SELECT id, live_id, start_time, end_time, end_reason '
                            'FROM live_sessions WHERE live_id=? ORDER BY start_time, id', (live_id,))
        for row in rows:
            start = dt.datetime.fromtimestamp(row['start_time'], tz)
            day = start.date()
            counts[day] = counts.get(day, 0) + 1
            ordinal = counts[day]
            if (since and day < since) or (until and day > until):
                continue
            end = dt.datetime.fromtimestamp(row['end_time'], tz) if row['end_time'] else None
            result.append({'session_id': row['id'], 'live_id': row['live_id'],
                           'start': start.isoformat(), 'end': end.isoformat() if end else None,
                           'start_date': day.isoformat(), 'daily_ordinal': ordinal,
                           'title': f'{day.isoformat()} · 第{ordinal}场直播',
                           'end_reason': row['end_reason'],
                           'preparation_eligible_by_db_only': bool(end and end > start and row['end_reason'] == 'normal')})
    return {'timezone': timezone, 'sessions': result,
            'limitations': 'Recorder rows must represent real sessions; verify reconnect semantics, repair logs and source stability. Does not start transcription or prove recording completeness.'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--db', type=Path, required=True)
    ap.add_argument('--live-id', required=True)
    ap.add_argument('--since', type=dt.date.fromisoformat)
    ap.add_argument('--until', type=dt.date.fromisoformat)
    ap.add_argument('--timezone', default='Asia/Shanghai')
    args = ap.parse_args()
    print(json.dumps(inventory(args.db, args.live_id, args.since, args.until, args.timezone), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
