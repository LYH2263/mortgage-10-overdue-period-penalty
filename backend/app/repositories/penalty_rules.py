import sqlite3

def _row(r): return dict(r) if r else None

def list_all(conn):
    return [dict(r) for r in conn.execute("SELECT * FROM penalty_rules ORDER BY id").fetchall()]

def get(conn, rid):
    return _row(conn.execute("SELECT * FROM penalty_rules WHERE id=?", (rid,)).fetchone())

def create(conn, name, grace_days, daily_rate, enabled):
    cur = conn.execute("INSERT INTO penalty_rules(name,grace_days,daily_rate,enabled) VALUES (?,?,?,?)",
        (name, grace_days, daily_rate, 1 if enabled else 0))
    conn.commit()
    return get(conn, int(cur.lastrowid))

def update(conn, rid, name, grace_days, daily_rate, enabled):
    if not get(conn, rid): return None
    conn.execute("UPDATE penalty_rules SET name=?, grace_days=?, daily_rate=?, enabled=? WHERE id=?",
        (name, grace_days, daily_rate, 1 if enabled else 0, rid))
    conn.commit()
    return get(conn, rid)

def set_enabled(conn, rid, enabled):
    if not get(conn, rid): return None
    conn.execute("UPDATE penalty_rules SET enabled=? WHERE id=?", (1 if enabled else 0, rid))
    conn.commit()
    return get(conn, rid)

def active(conn):
    return _row(conn.execute("SELECT * FROM penalty_rules WHERE enabled=1 ORDER BY id LIMIT 1").fetchone())
