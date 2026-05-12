import sqlite3
import time
from config import BASE_DIR

DB_PATH = BASE_DIR / "query_log.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS query_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT,
            top_category TEXT,
            response_time_ms REAL,
            timestamp REAL
        )
    """)
    conn.commit()
    conn.close()


def log_query(query: str, top_category: str, response_time_ms: float):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO query_log (query, top_category, response_time_ms, timestamp) VALUES (?, ?, ?, ?)",
        (query, top_category, response_time_ms, time.time())
    )
    conn.commit()
    conn.close()


def get_recent_logs(limit: int = 50) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        "SELECT query, top_category, response_time_ms, timestamp FROM query_log ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {"query": r[0], "top_category": r[1], "response_time_ms": r[2], "timestamp": r[3]}
        for r in rows
    ]