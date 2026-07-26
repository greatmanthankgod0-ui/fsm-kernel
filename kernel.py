import sqlite3
from datetime import datetime, timezone

RULES = {}
ACTIONS = {}
GUARDS = {}

TIMELINE_DB = "storage/kernel_timeline.db"


def _init_timeline_db():
    conn = sqlite3.connect(TIMELINE_DB)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS timeline (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        user_id INTEGER,
        state TEXT,
        event TEXT,
        action TEXT,
        next_state TEXT,
        result TEXT
    )""")
    conn.commit()
    conn.close()


_init_timeline_db()


def register_rule(state, event, action=None, guard=None, next_state=None):
    RULES[(state, event)] = {
        "action": action,
        "guard": guard,
        "next": next_state
    }


def register_action(name, fn):
    ACTIONS[name] = fn


def register_guard(name, fn):
    GUARDS[name] = fn


def _log_timeline(user_id, state, event, action, next_state, result):
    try:
        conn = sqlite3.connect(TIMELINE_DB)
        c = conn.cursor()
        c.execute("""INSERT INTO timeline
            (timestamp, user_id, state, event, action, next_state, result)
            VALUES (?,?,?,?,?,?,?)""",
            (datetime.now(timezone.utc).isoformat(), user_id, state, event, action, next_state, result))
        conn.commit()
        conn.close()
    except Exception:
        pass  # never let logging break the actual flow


def dispatch(state, event, ctx):
    user_id = ctx.get("user_id")
    rule = RULES.get((state, event))

    if not rule:
        _log_timeline(user_id, state, event, None, state, "NO_MATCH")
        return state, "NO_MATCH"

    guard_name = rule.get("guard")
    if guard_name:
        guard_fn = GUARDS.get(guard_name)
        if guard_fn and not guard_fn(ctx):
            _log_timeline(user_id, state, event, rule.get("action"), state, "GUARD_FAIL")
            return state, "GUARD_FAIL"

    action_name = rule.get("action")
    if action_name:
        action_fn = ACTIONS.get(action_name)
        if action_fn:
            action_fn(ctx)

    new_state = rule["next"]
    _log_timeline(user_id, state, event, action_name, new_state, "OK")
    return new_state, "OK"


def get_timeline(limit=50):
    conn = sqlite3.connect(TIMELINE_DB)
    c = conn.cursor()
    c.execute("""SELECT timestamp, user_id, state, event, action, next_state, result
                 FROM timeline ORDER BY id DESC LIMIT ?""", (limit,))
    rows = c.fetchall()
    conn.close()
    return [
        {"timestamp": r[0], "user_id": r[1], "state": r[2], "event": r[3],
         "action": r[4], "next": r[5], "result": r[6]}
        for r in rows
    ]
