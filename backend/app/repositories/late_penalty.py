import sqlite3

COLUMNS = ("id", "name", "grace_days", "daily_rate", "enabled", "created_at")


def _row(r):
    d = dict(r)
    d["enabled"] = bool(d["enabled"])
    return d


def list_all(conn):
    return [_row(r) for r in conn.execute(
        "SELECT * FROM late_penalty_rules ORDER BY id").fetchall()]


def get(conn, rule_id):
    r = conn.execute("SELECT * FROM late_penalty_rules WHERE id=?", (rule_id,)).fetchone()
    return _row(r) if r else None


def active(conn):
    """当前命中的启用规则（取最近启用的一条）。"""
    rows = conn.execute(
        "SELECT * FROM late_penalty_rules WHERE enabled=1 ORDER BY id DESC").fetchall()
    return _row(rows[0]) if rows else None


def insert(conn, name, grace_days, daily_rate, enabled=True):
    cur = conn.execute(
        "INSERT INTO late_penalty_rules(name,grace_days,daily_rate,enabled,created_at) "
        "VALUES (?,?,?,?,datetime('now'))",
        (name, int(grace_days), float(daily_rate), 1 if enabled else 0))
    conn.commit()
    return get(conn, int(cur.lastrowid))


def update(conn, rule_id, name=None, grace_days=None, daily_rate=None, enabled=None):
    cur = conn.execute("SELECT * FROM late_penalty_rules WHERE id=?", (rule_id,)).fetchone()
    if not cur:
        return None
    name = cur["name"] if name is None else name
    grace_days = cur["grace_days"] if grace_days is None else int(grace_days)
    daily_rate = cur["daily_rate"] if daily_rate is None else float(daily_rate)
    enabled = cur["enabled"] if enabled is None else (1 if enabled else 0)
    conn.execute(
        "UPDATE late_penalty_rules SET name=?,grace_days=?,daily_rate=?,enabled=? WHERE id=?",
        (name, grace_days, daily_rate, enabled, rule_id))
    conn.commit()
    return get(conn, rule_id)


def set_enabled(conn, rule_id, enabled: bool):
    return update(conn, rule_id, enabled=enabled)
