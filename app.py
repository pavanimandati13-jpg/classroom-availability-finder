"""Classroom Availability Finder - a small cloud-deployable web service.

Finds classrooms that are free for a given date/time by checking the weekly
timetable and one-off bookings. Exposes a REST API plus a single-page UI.
"""
import os
import random
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Flask, g, jsonify, render_template, request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("DB_PATH", os.path.join(BASE_DIR, "classrooms.db"))
APP_TZ = ZoneInfo(os.environ.get("APP_TZ", "Asia/Kolkata"))
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

app = Flask(__name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    building TEXT NOT NULL,
    floor INTEGER NOT NULL,
    capacity INTEGER NOT NULL,
    type TEXT NOT NULL DEFAULT 'Classroom'
);
CREATE TABLE IF NOT EXISTS timetable (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id INTEGER NOT NULL REFERENCES rooms(id),
    day TEXT NOT NULL,
    start TEXT NOT NULL,
    end TEXT NOT NULL,
    subject TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id INTEGER NOT NULL REFERENCES rooms(id),
    date TEXT NOT NULL,
    start TEXT NOT NULL,
    end TEXT NOT NULL,
    booked_by TEXT NOT NULL,
    purpose TEXT DEFAULT ''
);
"""

PERIODS = [("09:00", "10:00"), ("10:00", "11:00"), ("11:20", "12:20"),
           ("12:20", "13:20"), ("14:00", "15:00"), ("15:00", "16:00")]
SUBJECTS = ["Cloud Computing", "Deep Learning", "DBMS", "Operating Systems",
            "Computer Networks", "Software Engineering", "Data Structures", "Maths"]


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.executescript(SCHEMA)
    if db.execute("SELECT COUNT(*) FROM rooms").fetchone()[0] == 0:
        rnd = random.Random(42)
        rooms = [("A-101", "Block A", 1, 60, "Classroom"), ("A-102", "Block A", 1, 60, "Classroom"),
                 ("A-201", "Block A", 2, 70, "Classroom"), ("A-202", "Block A", 2, 70, "Classroom"),
                 ("B-101", "Block B", 1, 40, "Classroom"), ("B-102", "Block B", 1, 40, "Classroom"),
                 ("B-201", "Block B", 2, 90, "Seminar Hall"), ("B-301", "Block B", 3, 120, "Auditorium"),
                 ("C-LAB1", "Block C", 0, 30, "Computer Lab"), ("C-LAB2", "Block C", 0, 30, "Computer Lab"),
                 ("C-LAB3", "Block C", 1, 35, "Computer Lab"), ("C-201", "Block C", 2, 50, "Classroom")]
        db.executemany("INSERT INTO rooms(name,building,floor,capacity,type) VALUES (?,?,?,?,?)", rooms)
        for rid in range(1, len(rooms) + 1):
            for day in DAYS[:6]:
                for s, e in PERIODS:
                    if rnd.random() < 0.55:
                        db.execute("INSERT INTO timetable(room_id,day,start,end,subject) VALUES (?,?,?,?,?)",
                                   (rid, day, s, e, rnd.choice(SUBJECTS)))
    db.commit()
    db.close()


# ---------- helpers ----------
def valid_time(t):
    try:
        datetime.strptime(t, "%H:%M")
        return True
    except (TypeError, ValueError):
        return False


def valid_date(d):
    try:
        datetime.strptime(d, "%Y-%m-%d")
        return True
    except (TypeError, ValueError):
        return False


def day_name(date_str):
    return DAYS[datetime.strptime(date_str, "%Y-%m-%d").weekday()]


def busy_reason(db, room_id, date, start, end):
    """Return a description if the room is occupied in [start, end), else None."""
    t = db.execute(
        "SELECT subject, start, end FROM timetable WHERE room_id=? AND day=? AND start<? AND end>?",
        (room_id, day_name(date), end, start)).fetchone()
    if t:
        return f"Class: {t['subject']} ({t['start']}-{t['end']})"
    b = db.execute(
        "SELECT booked_by, purpose, start, end FROM bookings WHERE room_id=? AND date=? AND start<? AND end>?",
        (room_id, date, end, start)).fetchone()
    if b:
        return f"Booked by {b['booked_by']} ({b['start']}-{b['end']})"
    return None


# ---------- routes ----------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify(status="ok", time=datetime.now(APP_TZ).isoformat(timespec="seconds"))


@app.route("/api/now")
def now():
    n = datetime.now(APP_TZ)
    return jsonify(date=n.strftime("%Y-%m-%d"), time=n.strftime("%H:%M"))


@app.route("/api/rooms")
def rooms():
    rows = get_db().execute("SELECT * FROM rooms ORDER BY building, name").fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/availability")
def availability():
    n = datetime.now(APP_TZ)
    date = request.args.get("date", n.strftime("%Y-%m-%d"))
    start = request.args.get("start", n.strftime("%H:%M"))
    end = request.args.get("end")
    if not valid_date(date) or not valid_time(start):
        return jsonify(error="Invalid date (YYYY-MM-DD) or start time (HH:MM)"), 400
    if end is None:
        end = f"{min(int(start[:2]) + 1, 23):02d}:{start[3:]}"
    if not valid_time(end) or end <= start:
        return jsonify(error="End time must be after start time (HH:MM)"), 400

    sql, params = "SELECT * FROM rooms WHERE capacity>=?", [int(request.args.get("min_capacity", 0) or 0)]
    for key in ("building", "type"):
        if request.args.get(key):
            sql += f" AND {key}=?"
            params.append(request.args[key])
    db = get_db()
    free, busy = [], []
    for r in db.execute(sql + " ORDER BY building, name", params).fetchall():
        reason = busy_reason(db, r["id"], date, start, end)
        (busy if reason else free).append({**dict(r), "reason": reason})
    return jsonify(date=date, day=day_name(date), start=start, end=end,
                   free=free, busy=busy, free_count=len(free))


@app.route("/api/bookings", methods=["GET", "POST"])
def bookings():
    db = get_db()
    if request.method == "GET":
        date = request.args.get("date")
        q = ("SELECT b.*, r.name AS room FROM bookings b JOIN rooms r ON r.id=b.room_id"
             + (" WHERE b.date=?" if date else "") + " ORDER BY b.date, b.start")
        return jsonify([dict(r) for r in db.execute(q, (date,) if date else ()).fetchall()])

    d = request.get_json(silent=True) or {}
    room_id, date, start, end = d.get("room_id"), d.get("date"), d.get("start"), d.get("end")
    who = (d.get("booked_by") or "").strip()
    if not (room_id and who and valid_date(date) and valid_time(start) and valid_time(end) and end > start):
        return jsonify(error="room_id, booked_by, date, start, end are required and must be valid"), 400
    if not db.execute("SELECT 1 FROM rooms WHERE id=?", (room_id,)).fetchone():
        return jsonify(error="Room not found"), 404
    reason = busy_reason(db, room_id, date, start, end)
    if reason:
        return jsonify(error=f"Room not available - {reason}"), 409
    cur = db.execute("INSERT INTO bookings(room_id,date,start,end,booked_by,purpose) VALUES (?,?,?,?,?,?)",
                     (room_id, date, start, end, who, d.get("purpose", "")))
    db.commit()
    return jsonify(id=cur.lastrowid, message="Booked"), 201


@app.route("/api/bookings/<int:bid>", methods=["DELETE"])
def cancel(bid):
    db = get_db()
    cur = db.execute("DELETE FROM bookings WHERE id=?", (bid,))
    db.commit()
    return (jsonify(message="Cancelled"), 200) if cur.rowcount else (jsonify(error="Not found"), 404)


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
