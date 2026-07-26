import sqlite3
import traceback
from datetime import datetime, timezone

CRASH_DB = "storage/octopus_crashes.db"


def init_crash_log():
    conn = sqlite3.connect(CRASH_DB)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS crashes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        user_id INTEGER,
        state TEXT,
        event TEXT,
        error_type TEXT,
        error_message TEXT,
        traceback TEXT,
        notified INTEGER DEFAULT 0,
        resolved INTEGER DEFAULT 0
    )""")
    conn.commit()
    conn.close()


def log_crash(user_id, state, event, exc):
    conn = sqlite3.connect(CRASH_DB)
    c = conn.cursor()
    c.execute("""INSERT INTO crashes
        (timestamp, user_id, state, event, error_type, error_message, traceback)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (datetime.now(timezone.utc).isoformat(), user_id, state, event,
         type(exc).__name__, str(exc), traceback.format_exc()))
    conn.commit()
    conn.close()


def get_unnotified_crashes():
    conn = sqlite3.connect(CRASH_DB)
    c = conn.cursor()
    c.execute("SELECT id, timestamp, user_id, state, event, error_type, error_message FROM crashes WHERE notified = 0")
    rows = c.fetchall()
    conn.close()
    return rows


def mark_notified(crash_id):
    conn = sqlite3.connect(CRASH_DB)
    c = conn.cursor()
    c.execute("UPDATE crashes SET notified = 1 WHERE id = ?", (crash_id,))
    conn.commit()
    conn.close()


def safe_dispatch(state, event, ctx):
    """Wraps dispatch() with crash logging. Same signature, same return."""
    from kernel.kernel import dispatch
    try:
        return dispatch(state, event, ctx)
    except Exception as e:
        log_crash(ctx.get("user_id"), state, event, e)
        try:
            ctx["bot"].send_message(ctx["user_id"],
                "Something went wrong on my end. The team's been notified — try again in a moment 🙏")
        except:
            pass
        return state, "CRASH"
