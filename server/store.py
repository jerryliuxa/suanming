# -*- coding: utf-8 -*-
"""命例库：SQLite 存储保存的命例。"""

import json
import os
import sqlite3
import threading
from datetime import datetime

_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "charts.db")
_lock = threading.Lock()
_conn = None


def _get_conn():
    global _conn
    if _conn is None:
        os.makedirs(os.path.dirname(_DB_PATH), exist_ok=True)
        _conn = sqlite3.connect(_DB_PATH, check_same_thread=False)
        _conn.row_factory = sqlite3.Row
        _conn.execute("""CREATE TABLE IF NOT EXISTS charts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            gender TEXT NOT NULL,
            input_json TEXT NOT NULL,
            summary TEXT DEFAULT '',
            created_at TEXT NOT NULL
        )""")
        _conn.commit()
    return _conn


def list_charts():
    with _lock:
        rows = _get_conn().execute(
            "SELECT id, name, gender, input_json, summary, created_at FROM charts ORDER BY id DESC LIMIT 200"
        ).fetchall()
    out = []
    for r in rows:
        try:
            inp = json.loads(r["input_json"])
        except Exception:
            inp = {}
        out.append({"id": r["id"], "name": r["name"], "gender": r["gender"],
                    "input": inp, "summary": r["summary"], "created_at": r["created_at"]})
    return out


def add_chart(name, gender, input_obj, summary=""):
    with _lock:
        cur = _get_conn().execute(
            "INSERT INTO charts (name, gender, input_json, summary, created_at) VALUES (?,?,?,?,?)",
            (name, gender, json.dumps(input_obj, ensure_ascii=False), summary,
             datetime.now().strftime("%Y-%m-%d %H:%M")))
        _get_conn().commit()
        return cur.lastrowid


def delete_chart(chart_id):
    with _lock:
        cur = _get_conn().execute("DELETE FROM charts WHERE id=?", (chart_id,))
        _get_conn().commit()
        return cur.rowcount > 0
