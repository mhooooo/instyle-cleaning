#!/usr/bin/env python3
"""
InStyle Cleaning — Business Operations CLI
==========================================
Premium residential & commercial cleaning company, Gainesville FL.

Usage:
    python instyle_cli.py <command> [options]

Commands:
    init                Initialize database with schema + sample data
    quote               Generate a price quote
    schedule-add        Add a job to the schedule
    schedule-view       View schedule for a date/range
    schedule-optimize   Optimize crew route for a day
    client-add          Add a new client
    client-view         View client details + history
    client-search       Search clients
    client-list         List all clients
    recurring-add       Set up recurring schedule
    recurring-view      View upcoming recurring jobs
    crew-status         Show crew availability
    forecast            Seasonal demand forecast
    revenue-report      Revenue summary by period
    zone-report         Job density and revenue by zone
    dashboard           Full operational dashboard
"""

import argparse
import json
import math
import os
import sqlite3
import sys
from datetime import datetime, timedelta, date
from itertools import permutations
from typing import Optional

# ─── Brand Constants ────────────────────────────────────────────────
BRAND_NAVY = "#1B2A4A"
BRAND_GOLD = "#C9A84C"
COMPANY_NAME = "InStyle Cleaning"
COMPANY_TAGLINE = "Premium Clean. Every Time."
LOCATION = "Gainesville, FL"

# ─── Database Path ──────────────────────────────────────────────────
DB_PATH = os.environ.get("INSTYLE_DB", "instyle_cleaning.db")

# ─── Zone Drive Time Matrix (minutes) ──────────────────────────────
ZONES = ["NW", "NE", "SW", "SE", "DT"]
DRIVE_TIMES = {
    ("NW", "NW"): 5,  ("NW", "NE"): 20, ("NW", "SW"): 15, ("NW", "SE"): 25, ("NW", "DT"): 12,
    ("NE", "NW"): 20, ("NE", "NE"): 5,  ("NE", "SW"): 22, ("NE", "SE"): 15, ("NE", "DT"): 10,
    ("SW", "NW"): 15, ("SW", "NE"): 22, ("SW", "SW"): 5,  ("SW", "SE"): 18, ("SW", "DT"): 8,
    ("SE", "NW"): 25, ("SE", "NE"): 15, ("SE", "SW"): 18, ("SE", "SE"): 5,  ("SE", "DT"): 15,
    ("DT", "NW"): 12, ("DT", "NE"): 10, ("DT", "SW"): 8,  ("DT", "SE"): 15, ("DT", "DT"): 5,
}

# ─── Service Duration (hours) ──────────────────────────────────────
SERVICE_DURATION = {
    "standard": 2.0,
    "deep": 4.0,
    "move-out": 3.0,
    "commercial": 3.0,
}

# ─── Seasonal Demand Multipliers ───────────────────────────────────
SEASONAL_MULTIPLIERS = {
    1: 0.85,   # Jan — post-holiday slow
    2: 0.90,   # Feb — steady
    3: 0.95,   # Mar — spring break cleans
    4: 1.00,   # Apr — pre-summer prep
    5: 1.40,   # May — UF move-out surge
    6: 0.80,   # Jun — summer low
    7: 0.75,   # Jul — summer low
    8: 1.80,   # Aug — UF move-in surge (PEAK)
    9: 1.10,   # Sep — post move-in settling
    10: 1.00,  # Oct — steady
    11: 0.95,  # Nov — pre-holiday
    12: 1.05,  # Dec — holiday cleans
}

# ─── Pricing Constants ─────────────────────────────────────────────
PRICING = {
    "standard":  {"base": 80,  "per_room": 20, "per_sqft": 0.03, "min": 120, "max": 250},
    "deep":      {"base": 150, "per_room": 35, "per_sqft": 0.06, "min": 250, "max": 500},
    "move-out":  {"base": 120, "per_room": 25, "per_sqft": 0.05, "min": 200, "max": 400},
}

COMMERCIAL_RATES = {
    "warehouse": 0.10,
    "office":    0.15,
    "retail":    0.20,
    "medical":   0.30,
    "food":      0.30,
}

ADDONS = {
    "fridge":   35,
    "oven":     40,
    "windows":  5,    # per window
    "carpet":   25,   # per room
    "garage":   75,   # average
    "laundry":  25,   # per load
    "dishes":   15,
    "walls":    20,
}

RECURRING_DISCOUNTS = {
    "weekly":   0.15,
    "biweekly": 0.10,
    "monthly":  0.05,
}


# ═══════════════════════════════════════════════════════════════════
# DATABASE
# ═══════════════════════════════════════════════════════════════════

def get_db():
    """Get database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(with_sample_data=True):
    """Initialize database schema and optionally load sample data."""
    conn = get_db()
    c = conn.cursor()

    # ── Schema ──
    c.executescript("""
        DROP TABLE IF EXISTS job_history;
        DROP TABLE IF EXISTS scheduled_jobs;
        DROP TABLE IF EXISTS recurring_schedules;
        DROP TABLE IF EXISTS clients;
        DROP TABLE IF EXISTS crews;

        CREATE TABLE crews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            member_1 TEXT NOT NULL,
            member_2 TEXT NOT NULL,
            active INTEGER DEFAULT 1,
            phone TEXT,
            notes TEXT
        );

        CREATE TABLE clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            address TEXT NOT NULL,
            zone TEXT NOT NULL CHECK (zone IN ('NW','NE','SW','SE','DT')),
            sqft INTEGER,
            rooms INTEGER,
            notes TEXT,
            preferred_crew_id INTEGER REFERENCES crews(id),
            created_at TEXT DEFAULT (datetime('now')),
            lifetime_value REAL DEFAULT 0
        );

        CREATE TABLE scheduled_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL REFERENCES clients(id),
            crew_id INTEGER NOT NULL REFERENCES crews(id),
            date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT,
            service_type TEXT NOT NULL CHECK (service_type IN ('standard','deep','move-out','commercial')),
            zone TEXT NOT NULL CHECK (zone IN ('NW','NE','SW','SE','DT')),
            price REAL,
            status TEXT DEFAULT 'scheduled' CHECK (status IN ('scheduled','in-progress','completed','cancelled')),
            notes TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE recurring_schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL REFERENCES clients(id),
            crew_id INTEGER REFERENCES crews(id),
            service_type TEXT NOT NULL,
            frequency TEXT NOT NULL CHECK (frequency IN ('weekly','biweekly','monthly')),
            preferred_day TEXT CHECK (preferred_day IN ('Mon','Tue','Wed','Thu','Fri','Sat')),
            preferred_time TEXT,
            zone TEXT NOT NULL,
            price REAL,
            active INTEGER DEFAULT 1,
            next_date TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE job_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL REFERENCES clients(id),
            crew_id INTEGER NOT NULL REFERENCES crews(id),
            date TEXT NOT NULL,
            service_type TEXT NOT NULL,
            zone TEXT NOT NULL,
            price REAL NOT NULL,
            duration_hours REAL,
            rating INTEGER CHECK (rating BETWEEN 1 AND 5),
            notes TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE INDEX idx_jobs_date ON scheduled_jobs(date);
        CREATE INDEX idx_jobs_crew ON scheduled_jobs(crew_id, date);
        CREATE INDEX idx_clients_zone ON clients(zone);
        CREATE INDEX idx_history_client ON job_history(client_id);
        CREATE INDEX idx_history_date ON job_history(date);
    """)

    if with_sample_data:
        _load_sample_data(c)

    conn.commit()
    conn.close()
    print(f"✅ Database initialized at {DB_PATH}")
    if with_sample_data:
        print("   Loaded sample data: 3 crews, 12 clients, 15 scheduled jobs, 30 history records")


def _load_sample_data(c):
    """Load realistic sample data for Gainesville market."""

    # Crews
    crews = [
        ("Alpha Team", "Maria Santos", "James Wilson", 1, "352-555-0101", "Most experienced, handles deep cleans"),
        ("Bravo Team", "Ashley Chen", "David Brown", 1, "352-555-0102", "Fast and efficient, great for standards"),
        ("Charlie Team", "Nicole Taylor", "Robert Garcia", 1, "352-555-0103", "New team, training phase"),
    ]
    c.executemany("INSERT INTO crews (name, member_1, member_2, active, phone, notes) VALUES (?,?,?,?,?,?)", crews)

    # Clients — realistic Gainesville addresses
    clients = [
        ("Sarah Johnson", "352-555-0201", "sarah.j@email.com", "4521 NW 23rd Ave", "NW", 2200, 4,
         "Two dogs. Eco-friendly products only. Gate code: 4521#", 1, 4800.0),
        ("Mike Chen", "352-555-0202", "mchen@ufl.edu", "1250 SW 16th Ave, Apt 204", "SW", 850, 2,
         "UF grad student. Key under mat. Quiet hours after 10pm", None, 960.0),
        ("Gainesville Dental Group", "352-555-0203", "office@gvilledental.com", "6200 NW 43rd St, Suite B", "NW", 3500, 8,
         "Medical facility. Must use hospital-grade disinfectant. After hours only (6pm+)", 1, 12600.0),
        ("Patricia Williams", "352-555-0204", "pwilliams@gmail.com", "8901 SW Archer Rd, Unit 12", "SW", 1100, 3,
         "Retired professor. Prefers Thursday mornings. Has cat — keep doors closed", 2, 3200.0),
        ("Tom & Lisa Martinez", "352-555-0205", "martinez.family@email.com", "3345 NW 51st Terr", "NW", 2800, 5,
         "Large family home. Kids' rooms need extra attention. Biweekly service", 1, 6400.0),
        ("Campus Realty Group", "352-555-0206", "turns@campusrealty.com", "2100 SW 34th St", "SW", None, None,
         "Property management company. Move-out cleans for student apartments. Bulk pricing", None, 18500.0),
        ("David Park", "352-555-0207", "dpark@hotmail.com", "1501 NE 8th Ave", "NE", 1600, 3,
         "Works from home — prefers afternoon slots. Has home office that needs careful handling", 2, 2100.0),
        ("The Swamp Restaurant", "352-555-0208", "manager@theswampgville.com", "1642 W University Ave", "DT", 4000, 6,
         "Restaurant. Deep kitchen clean weekly. Must be done before 10am opening", 1, 9800.0),
        ("Jennifer Adams", "352-555-0209", "jadams@bellsouth.net", "5678 SE Williston Rd", "SE", 1800, 3,
         "New client. First deep clean scheduled. Interested in recurring biweekly", None, 0.0),
        ("UF Innovation Hub", "352-555-0210", "facilities@ufinnov.edu", "747 SW 2nd Ave", "DT", 8000, 15,
         "Office complex. 3x/week cleaning. Badge access required — contact Jim at x4501", 3, 22000.0),
        ("Robert & Amy Kim", "352-555-0211", "kimfamily@email.com", "7890 NW 39th Ave", "NW", 3200, 6,
         "Premium home. Monthly deep clean + weekly standard. Wine cellar area needs special care", 1, 8900.0),
        ("Haile Village Shops", "352-555-0212", "property@hailevillage.com", "5010 SW 91st Terr", "SW", 5500, 10,
         "Retail complex — 4 shops. Weekend cleaning preferred. Parking lot sweep included", None, 5200.0),
    ]
    c.executemany("""INSERT INTO clients (name, phone, email, address, zone, sqft, rooms, notes,
                     preferred_crew_id, lifetime_value) VALUES (?,?,?,?,?,?,?,?,?,?)""", clients)

    # Scheduled jobs — next 5 business days
    today = date.today()
    jobs = []
    job_templates = [
        # Day 1
        (1, 1, 0, "08:30", "10:30", "standard", "NW", 195.0, "scheduled", "Biweekly recurring"),
        (4, 2, 0, "09:00", "11:00", "standard", "SW", 155.0, "scheduled", "Weekly recurring"),
        (3, 1, 0, "11:00", "14:00", "commercial", "NW", 525.0, "scheduled", "Medical grade — after hours"),
        (7, 2, 0, "11:30", "13:30", "standard", "NE", 170.0, "scheduled", "WFH client — afternoon"),
        (8, 1, 0, "15:00", "18:00", "commercial", "DT", 800.0, "scheduled", "Restaurant deep kitchen"),
        # Day 2
        (5, 1, 1, "08:00", "10:30", "standard", "NW", 225.0, "scheduled", "Biweekly — kids rooms"),
        (2, 2, 1, "08:30", "10:30", "standard", "SW", 135.0, "scheduled", "Quick apartment standard"),
        (10, 3, 1, "09:00", "12:00", "commercial", "DT", 1200.0, "scheduled", "Office complex — badge needed"),
        (11, 1, 1, "11:00", "15:00", "deep", "NW", 450.0, "scheduled", "Monthly deep incl wine cellar"),
        (6, 2, 1, "11:00", "14:00", "move-out", "SW", 245.0, "scheduled", "Apt 5B turnover"),
        # Day 3
        (1, 1, 2, "08:30", "10:30", "standard", "NW", 195.0, "scheduled", "Recurring"),
        (9, 2, 2, "09:00", "13:00", "deep", "SE", 360.0, "scheduled", "First clean — new client"),
        (12, 3, 2, "09:00", "12:00", "commercial", "SW", 550.0, "scheduled", "Retail complex"),
        (4, 1, 2, "11:00", "13:00", "standard", "SW", 155.0, "scheduled", "Recurring"),
        (7, 2, 2, "14:00", "16:00", "standard", "NE", 170.0, "scheduled", "Biweekly"),
    ]
    for cid, crew, day_offset, start, end, stype, zone, price, status, notes in job_templates:
        job_date = (today + timedelta(days=day_offset)).isoformat()
        jobs.append((cid, crew, job_date, start, end, stype, zone, price, status, notes))

    c.executemany("""INSERT INTO scheduled_jobs (client_id, crew_id, date, start_time, end_time,
                     service_type, zone, price, status, notes) VALUES (?,?,?,?,?,?,?,?,?,?)""", jobs)

    # Job history — past 30 days
    history = []
    history_templates = [
        (1, 1, "standard", "NW", 195.0, 2.0, 5, "Perfect as always"),
        (1, 1, "standard", "NW", 195.0, 2.0, 5, ""),
        (2, 2, "standard", "SW", 135.0, 1.5, 4, "Quick and clean"),
        (3, 1, "commercial", "NW", 525.0, 3.0, 5, "Hospital-grade done"),
        (3, 1, "commercial", "NW", 525.0, 3.0, 5, ""),
        (4, 2, "standard", "SW", 155.0, 2.0, 5, "Cat was friendly"),
        (4, 2, "standard", "SW", 155.0, 2.0, 4, ""),
        (5, 1, "standard", "NW", 225.0, 2.5, 5, "Extra time on kids rooms"),
        (5, 1, "standard", "NW", 225.0, 2.5, 5, ""),
        (6, 2, "move-out", "SW", 245.0, 3.0, 4, "Apt 3A — passed inspection"),
        (6, 2, "move-out", "SW", 280.0, 3.5, 5, "Apt 7C — heavy cleaning needed"),
        (6, 2, "move-out", "SW", 245.0, 3.0, 4, "Apt 2B — standard turnover"),
        (7, 2, "standard", "NE", 170.0, 2.0, 5, "WFH — cleaned around office"),
        (7, 2, "standard", "NE", 170.0, 2.0, 4, ""),
        (8, 1, "commercial", "DT", 800.0, 3.5, 5, "Kitchen spotless"),
        (8, 1, "commercial", "DT", 800.0, 3.0, 5, ""),
        (8, 1, "commercial", "DT", 800.0, 3.0, 5, "Health inspector next week"),
        (8, 1, "commercial", "DT", 800.0, 3.0, 5, ""),
        (10, 3, "commercial", "DT", 1200.0, 3.5, 4, "Badge worked, all good"),
        (10, 3, "commercial", "DT", 1200.0, 3.0, 5, ""),
        (10, 3, "commercial", "DT", 1200.0, 3.0, 4, "Restroom on 3rd floor extra dirty"),
        (11, 1, "deep", "NW", 450.0, 4.0, 5, "Wine cellar handled with care"),
        (11, 1, "standard", "NW", 250.0, 2.5, 5, ""),
        (11, 1, "standard", "NW", 250.0, 2.0, 5, ""),
        (11, 1, "standard", "NW", 250.0, 2.0, 5, ""),
        (5, 1, "standard", "NW", 225.0, 2.5, 4, "Biweekly regular"),
        (4, 2, "standard", "SW", 155.0, 2.0, 5, ""),
        (2, 2, "standard", "SW", 135.0, 1.5, 4, ""),
        (1, 1, "standard", "NW", 195.0, 2.0, 5, ""),
        (3, 1, "commercial", "NW", 525.0, 3.0, 5, ""),
    ]
    for i, (cid, crew, stype, zone, price, dur, rating, notes) in enumerate(history_templates):
        hist_date = (today - timedelta(days=30 - i)).isoformat()
        history.append((cid, crew, hist_date, stype, zone, price, dur, rating, notes))

    c.executemany("""INSERT INTO job_history (client_id, crew_id, date, service_type, zone,
                     price, duration_hours, rating, notes) VALUES (?,?,?,?,?,?,?,?,?)""", history)

    # Recurring schedules
    recurring = [
        (1, 1, "standard", "biweekly", "Tue", "08:30", "NW", 175.50, 1),  # 10% off $195
        (4, 2, "standard", "weekly", "Thu", "09:00", "SW", 131.75, 1),     # 15% off $155
        (5, 1, "standard", "biweekly", "Mon", "08:00", "NW", 202.50, 1),   # 10% off $225
        (7, 2, "standard", "biweekly", "Wed", "14:00", "NE", 153.00, 1),   # 10% off $170
        (8, 1, "commercial", "weekly", "Mon", "06:00", "DT", 680.00, 1),   # 15% off $800
        (10, 3, "commercial", "weekly", "Tue", "09:00", "DT", 1020.00, 1), # 15% off $1200 (3x/week, approx)
        (11, 1, "standard", "weekly", "Fri", "08:00", "NW", 212.50, 1),    # 15% off $250
    ]
    for cid, crew, stype, freq, day, time, zone, price, active in recurring:
        next_d = _next_weekday(today, day)
        c.execute("""INSERT INTO recurring_schedules (client_id, crew_id, service_type, frequency,
                     preferred_day, preferred_time, zone, price, active, next_date)
                     VALUES (?,?,?,?,?,?,?,?,?,?)""",
                  (cid, crew, stype, freq, day, time, zone, price, active, next_d.isoformat()))


def _next_weekday(from_date, day_name):
    """Find the next occurrence of a weekday."""
    days = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}
    target = days[day_name]
    delta = (target - from_date.weekday()) % 7
    if delta == 0:
        delta = 7
    return from_date + timedelta(days=delta)


# ═══════════════════════════════════════════════════════════════════
# QUOTE GENERATOR
# ═══════════════════════════════════════════════════════════════════

def generate_quote(service_type, sqft=None, rooms=None, commercial_type=None,
                   addons=None, recurring=None):
    """Generate a professional price quote."""

    result = {
        "company": COMPANY_NAME,
        "tagline": COMPANY_TAGLINE,
        "service_type": service_type,
        "line_items": [],
        "subtotal": 0,
        "discount": 0,
        "discount_label": None,
        "total": 0,
        "estimated_duration": SERVICE_DURATION.get(service_type, 2.0),
    }

    if service_type == "commercial":
        if not sqft:
            return {"error": "Commercial quotes require --sqft"}
        ctype = commercial_type or "office"
        rate = COMMERCIAL_RATES.get(ctype, 0.15)
        base_price = sqft * rate
        result["line_items"].append({
            "item": f"Commercial Clean ({ctype})",
            "detail": f"{sqft:,} sqft × ${rate:.2f}/sqft",
            "price": round(base_price, 2)
        })
        result["subtotal"] = round(base_price, 2)
        result["estimated_duration"] = max(2.0, sqft / 2000)
    else:
        if not sqft or not rooms:
            return {"error": f"{service_type} quotes require --sqft and --rooms"}

        p = PRICING[service_type]
        base_price = p["base"] + (rooms * p["per_room"]) + (sqft * p["per_sqft"])
        base_price = max(p["min"], min(p["max"], base_price))

        result["line_items"].append({
            "item": f"{service_type.replace('-', ' ').title()} Clean",
            "detail": f"{rooms} rooms, {sqft:,} sqft",
            "price": round(base_price, 2)
        })
        result["subtotal"] = round(base_price, 2)

    # Add-ons
    if addons:
        for addon_str in addons:
            parts = addon_str.split(":")
            addon_name = parts[0].lower()
            quantity = int(parts[1]) if len(parts) > 1 else 1

            if addon_name in ADDONS:
                unit_price = ADDONS[addon_name]
                total_price = unit_price * quantity
                qty_str = f" × {quantity}" if quantity > 1 else ""
                result["line_items"].append({
                    "item": f"Add-on: {addon_name.title()}{qty_str}",
                    "detail": f"${unit_price}{qty_str}",
                    "price": total_price
                })
                result["subtotal"] += total_price
                result["estimated_duration"] += 0.25 * quantity

    # Recurring discount
    if recurring and recurring in RECURRING_DISCOUNTS:
        discount_pct = RECURRING_DISCOUNTS[recurring]
        result["discount"] = round(result["subtotal"] * discount_pct, 2)
        result["discount_label"] = f"{recurring.title()} recurring ({int(discount_pct*100)}% off)"

    result["subtotal"] = round(result["subtotal"], 2)
    result["total"] = round(result["subtotal"] - result["discount"], 2)
    result["estimated_duration"] = round(result["estimated_duration"], 1)

    return result


def print_quote(quote):
    """Pretty-print a quote."""
    if "error" in quote:
        print(f"❌ Error: {quote['error']}")
        return

    w = 60
    print()
    print("═" * w)
    print(f"  {COMPANY_NAME}".center(w))
    print(f"  {COMPANY_TAGLINE}".center(w))
    print(f"  {LOCATION}".center(w))
    print("═" * w)
    print(f"  SERVICE QUOTE — {quote['service_type'].upper().replace('-', ' ')}")
    print("─" * w)

    for item in quote["line_items"]:
        print(f"  {item['item']:<38} ${item['price']:>8.2f}")
        print(f"    {item['detail']}")

    print("─" * w)
    print(f"  {'Subtotal':<38} ${quote['subtotal']:>8.2f}")

    if quote["discount"] > 0:
        print(f"  {quote['discount_label']:<38} -${quote['discount']:>7.2f}")

    print("═" * w)
    print(f"  {'TOTAL':<38} ${quote['total']:>8.2f}")
    print("═" * w)
    print(f"  Estimated Duration: {quote['estimated_duration']} hours (2-person crew)")
    print()


# ═══════════════════════════════════════════════════════════════════
# SCHEDULING
# ═══════════════════════════════════════════════════════════════════

def schedule_add(client_id, crew_id, job_date, start_time, service_type, zone, price=None, notes=""):
    """Add a job to the schedule."""
    conn = get_db()
    duration = SERVICE_DURATION.get(service_type, 2.0)
    start_h, start_m = map(int, start_time.split(":"))
    end_h = start_h + int(duration)
    end_m = start_m + int((duration % 1) * 60)
    if end_m >= 60:
        end_h += 1
        end_m -= 60
    end_time = f"{end_h:02d}:{end_m:02d}"

    conn.execute("""INSERT INTO scheduled_jobs (client_id, crew_id, date, start_time, end_time,
                    service_type, zone, price, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                 (client_id, crew_id, job_date, start_time, end_time, service_type, zone, price, notes))
    conn.commit()

    # Get client name
    client = conn.execute("SELECT name FROM clients WHERE id = ?", (client_id,)).fetchone()
    crew = conn.execute("SELECT name FROM crews WHERE id = ?", (crew_id,)).fetchone()
    conn.close()

    print(f"✅ Job scheduled:")
    print(f"   Client: {client['name']} (#{client_id})")
    print(f"   Crew:   {crew['name']} (#{crew_id})")
    print(f"   Date:   {job_date}  {start_time}–{end_time}")
    print(f"   Type:   {service_type}  |  Zone: {zone}")
    if price:
        print(f"   Price:  ${price:.2f}")


def schedule_view(target_date, end_date=None):
    """View schedule for a date or range."""
    conn = get_db()

    if end_date:
        jobs = conn.execute("""
            SELECT j.*, c.name as client_name, cr.name as crew_name
            FROM scheduled_jobs j
            JOIN clients c ON j.client_id = c.id
            JOIN crews cr ON j.crew_id = cr.id
            WHERE j.date BETWEEN ? AND ?
            ORDER BY j.date, j.crew_id, j.start_time
        """, (target_date, end_date)).fetchall()
    else:
        jobs = conn.execute("""
            SELECT j.*, c.name as client_name, cr.name as crew_name
            FROM scheduled_jobs j
            JOIN clients c ON j.client_id = c.id
            JOIN crews cr ON j.crew_id = cr.id
            WHERE j.date = ?
            ORDER BY j.crew_id, j.start_time
        """, (target_date,)).fetchall()

    conn.close()

    if not jobs:
        print(f"📋 No jobs scheduled for {target_date}" + (f" to {end_date}" if end_date else ""))
        return

    current_date = None
    current_crew = None
    total_revenue = 0

    for job in jobs:
        if job["date"] != current_date:
            current_date = job["date"]
            day_name = datetime.strptime(current_date, "%Y-%m-%d").strftime("%A")
            print(f"\n{'═' * 60}")
            print(f"  📅 {current_date} ({day_name})")
            print(f"{'═' * 60}")
            current_crew = None

        if job["crew_name"] != current_crew:
            current_crew = job["crew_name"]
            print(f"\n  🚐 {current_crew}")
            print(f"  {'─' * 50}")

        status_icon = {"scheduled": "⬜", "in-progress": "🔵", "completed": "✅", "cancelled": "❌"}
        icon = status_icon.get(job["status"], "⬜")
        price_str = f"${job['price']:.0f}" if job["price"] else "TBD"
        print(f"  {icon} {job['start_time']}–{job['end_time']}  {job['client_name']:<20}  "
              f"{job['service_type']:<10} [{job['zone']}]  {price_str}")
        if job["notes"]:
            print(f"     📝 {job['notes']}")
        total_revenue += (job["price"] or 0)

    print(f"\n{'─' * 60}")
    print(f"  Total jobs: {len(jobs)}  |  Revenue: ${total_revenue:,.0f}")
    print()


# ═══════════════════════════════════════════════════════════════════
# ROUTE OPTIMIZATION
# ═══════════════════════════════════════════════════════════════════

def schedule_optimize(target_date, crew_id):
    """Optimize job order for a crew to minimize drive time."""
    conn = get_db()

    jobs = conn.execute("""
        SELECT j.*, c.name as client_name, c.address
        FROM scheduled_jobs j
        JOIN clients c ON j.client_id = c.id
        WHERE j.date = ? AND j.crew_id = ? AND j.status = 'scheduled'
        ORDER BY j.start_time
    """, (target_date, crew_id)).fetchall()

    crew = conn.execute("SELECT name FROM crews WHERE id = ?", (crew_id,)).fetchone()
    conn.close()

    if not jobs:
        print(f"No scheduled jobs for crew #{crew_id} on {target_date}")
        return

    if len(jobs) <= 1:
        print(f"Only {len(jobs)} job — no optimization needed")
        return

    job_list = [dict(j) for j in jobs]
    n = len(job_list)

    # Calculate original drive time
    original_time = sum(
        DRIVE_TIMES.get((job_list[i]["zone"], job_list[i+1]["zone"]), 15)
        for i in range(n - 1)
    )

    # Try all permutations for small lists, nearest-neighbor for larger
    if n <= 6:
        best_order = None
        best_time = float("inf")
        for perm in permutations(range(n)):
            total = sum(
                DRIVE_TIMES.get((job_list[perm[i]]["zone"], job_list[perm[i+1]]["zone"]), 15)
                for i in range(n - 1)
            )
            if total < best_time:
                best_time = total
                best_order = perm
        optimized = [job_list[i] for i in best_order]
    else:
        # Nearest-neighbor heuristic
        remaining = list(range(n))
        order = [remaining.pop(0)]
        while remaining:
            last_zone = job_list[order[-1]]["zone"]
            nearest = min(remaining, key=lambda j: DRIVE_TIMES.get((last_zone, job_list[j]["zone"]), 15))
            order.append(nearest)
            remaining.remove(nearest)
        optimized = [job_list[i] for i in order]
        best_time = sum(
            DRIVE_TIMES.get((optimized[i]["zone"], optimized[i+1]["zone"]), 15)
            for i in range(n - 1)
        )

    saved = original_time - best_time

    print(f"\n🗺️  Route Optimization — {crew['name']} — {target_date}")
    print("═" * 60)

    print(f"\n  Original route ({original_time} min drive time):")
    for i, j in enumerate(job_list):
        arrow = " → " if i < n - 1 else ""
        print(f"    {i+1}. [{j['zone']}] {j['client_name']} ({j['start_time']}){arrow}", end="")
    print()

    print(f"\n  ✅ Optimized route ({best_time} min drive time):")
    current_time_str = optimized[0]["start_time"]
    for i, j in enumerate(optimized):
        zone_transition = ""
        if i > 0:
            drive = DRIVE_TIMES.get((optimized[i-1]["zone"], j["zone"]), 15)
            zone_transition = f"  (+{drive} min drive)"
        print(f"    {i+1}. [{j['zone']}] {j['client_name']} — {j['service_type']}{zone_transition}")

    print(f"\n  ⏱️  Drive time saved: {saved} minutes")
    if saved > 0:
        print(f"  💰 That's ~${saved * 0.50:.0f} in fuel + wear savings")
    print()


# ═══════════════════════════════════════════════════════════════════
# CLIENT CRM
# ═══════════════════════════════════════════════════════════════════

def client_add(name, address, zone, phone=None, email=None, sqft=None, rooms=None,
               notes=None, preferred_crew_id=None):
    """Add a new client."""
    conn = get_db()
    c = conn.cursor()
    c.execute("""INSERT INTO clients (name, phone, email, address, zone, sqft, rooms,
                 notes, preferred_crew_id) VALUES (?,?,?,?,?,?,?,?,?)""",
              (name, phone, email, address, zone, sqft, rooms, notes, preferred_crew_id))
    conn.commit()
    client_id = c.lastrowid
    conn.close()
    print(f"✅ Client added: {name} (#{client_id}) — Zone {zone}")
    return client_id


def client_view(client_id):
    """View full client profile with service history."""
    conn = get_db()
    client = conn.execute("SELECT * FROM clients WHERE id = ?", (client_id,)).fetchone()

    if not client:
        print(f"❌ Client #{client_id} not found")
        conn.close()
        return

    history = conn.execute("""
        SELECT h.*, cr.name as crew_name
        FROM job_history h
        JOIN crews cr ON h.crew_id = cr.id
        WHERE h.client_id = ?
        ORDER BY h.date DESC LIMIT 10
    """, (client_id,)).fetchall()

    recurring = conn.execute("""
        SELECT r.*, cr.name as crew_name
        FROM recurring_schedules r
        LEFT JOIN crews cr ON r.crew_id = cr.id
        WHERE r.client_id = ? AND r.active = 1
    """, (client_id,)).fetchall()

    upcoming = conn.execute("""
        SELECT j.*, cr.name as crew_name
        FROM scheduled_jobs j
        JOIN crews cr ON j.crew_id = cr.id
        WHERE j.client_id = ? AND j.date >= date('now') AND j.status = 'scheduled'
        ORDER BY j.date LIMIT 5
    """, (client_id,)).fetchall()

    # Calculate stats
    stats = conn.execute("""
        SELECT COUNT(*) as total_jobs, SUM(price) as total_revenue,
               AVG(rating) as avg_rating, MAX(date) as last_service
        FROM job_history WHERE client_id = ?
    """, (client_id,)).fetchone()

    conn.close()

    print(f"\n{'═' * 60}")
    print(f"  👤 {client['name']}  (Client #{client_id})")
    print(f"{'═' * 60}")
    print(f"  📞 {client['phone'] or 'N/A'}  |  📧 {client['email'] or 'N/A'}")
    print(f"  📍 {client['address']}  |  Zone: {client['zone']}")
    if client["sqft"]:
        print(f"  🏠 {client['sqft']:,} sqft  |  {client['rooms']} rooms")
    print(f"  📝 {client['notes'] or 'No notes'}")

    print(f"\n  📊 Stats")
    print(f"  {'─' * 50}")
    print(f"  Total jobs: {stats['total_jobs']}  |  Revenue: ${stats['total_revenue'] or 0:,.0f}")
    print(f"  Avg rating: {'⭐' * int(stats['avg_rating'] or 0)} ({stats['avg_rating'] or 0:.1f}/5)")
    print(f"  Last service: {stats['last_service'] or 'Never'}")
    print(f"  Lifetime value: ${client['lifetime_value']:,.0f}")

    if recurring:
        print(f"\n  🔄 Recurring Schedules")
        print(f"  {'─' * 50}")
        for r in recurring:
            crew_str = f" — {r['crew_name']}" if r['crew_name'] else ""
            print(f"  {r['frequency'].title()} {r['service_type']} on {r['preferred_day']}s "
                  f"at {r['preferred_time']}{crew_str}  ${r['price']:.0f}")

    if upcoming:
        print(f"\n  📅 Upcoming Jobs")
        print(f"  {'─' * 50}")
        for j in upcoming:
            print(f"  {j['date']}  {j['start_time']}  {j['service_type']}  "
                  f"{j['crew_name']}  ${j['price']:.0f}")

    if history:
        print(f"\n  📜 Recent History (last 10)")
        print(f"  {'─' * 50}")
        for h in history:
            rating_str = "⭐" * (h["rating"] or 0)
            print(f"  {h['date']}  {h['service_type']:<10}  {h['crew_name']:<12}  "
                  f"${h['price']:.0f}  {rating_str}")
            if h["notes"]:
                print(f"    → {h['notes']}")
    print()


def client_search(query):
    """Search clients by name, address, or zone."""
    conn = get_db()
    clients = conn.execute("""
        SELECT * FROM clients
        WHERE name LIKE ? OR address LIKE ? OR zone LIKE ? OR email LIKE ?
        ORDER BY name
    """, (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%")).fetchall()
    conn.close()

    if not clients:
        print(f"🔍 No clients found matching '{query}'")
        return

    print(f"\n🔍 Found {len(clients)} client(s) matching '{query}':")
    print(f"{'─' * 70}")
    print(f"  {'ID':<4} {'Name':<25} {'Zone':<4} {'Phone':<14} {'LTV':>8}")
    print(f"{'─' * 70}")
    for c in clients:
        print(f"  {c['id']:<4} {c['name']:<25} {c['zone']:<4} {c['phone'] or 'N/A':<14} "
              f"${c['lifetime_value']:>7,.0f}")
    print()


def client_list(zone_filter=None, sort_by="name"):
    """List all clients with optional filters."""
    conn = get_db()
    query = "SELECT * FROM clients"
    params = []
    if zone_filter:
        query += " WHERE zone = ?"
        params.append(zone_filter.upper())

    sort_map = {"name": "name", "ltv": "lifetime_value DESC", "zone": "zone, name",
                "created": "created_at DESC"}
    query += f" ORDER BY {sort_map.get(sort_by, 'name')}"

    clients = conn.execute(query, params).fetchall()
    conn.close()

    header = f"All Clients" + (f" — Zone {zone_filter.upper()}" if zone_filter else "")
    print(f"\n📋 {header} ({len(clients)} total)")
    print(f"{'─' * 80}")
    print(f"  {'ID':<4} {'Name':<25} {'Zone':<4} {'Sqft':>6} {'Rooms':>5} {'LTV':>10} {'Recurring':>9}")
    print(f"{'─' * 80}")
    for c in clients:
        sqft_str = f"{c['sqft']:,}" if c['sqft'] else "—"
        rooms_str = str(c['rooms']) if c['rooms'] else "—"
        print(f"  {c['id']:<4} {c['name']:<25} {c['zone']:<4} {sqft_str:>6} {rooms_str:>5} "
              f"${c['lifetime_value']:>9,.0f}")
    print()


# ═══════════════════════════════════════════════════════════════════
# RECURRING SCHEDULES
# ═══════════════════════════════════════════════════════════════════

def recurring_add(client_id, service_type, frequency, preferred_day, preferred_time,
                  zone, price, crew_id=None):
    """Set up a recurring cleaning schedule."""
    conn = get_db()
    client = conn.execute("SELECT name FROM clients WHERE id = ?", (client_id,)).fetchone()
    if not client:
        print(f"❌ Client #{client_id} not found")
        conn.close()
        return

    # Apply recurring discount
    discount = RECURRING_DISCOUNTS.get(frequency, 0)
    discounted_price = round(price * (1 - discount), 2)

    next_d = _next_weekday(date.today(), preferred_day)

    conn.execute("""INSERT INTO recurring_schedules (client_id, crew_id, service_type, frequency,
                    preferred_day, preferred_time, zone, price, active, next_date)
                    VALUES (?,?,?,?,?,?,?,?,1,?)""",
                 (client_id, crew_id, service_type, frequency, preferred_day, preferred_time,
                  zone, discounted_price, next_d.isoformat()))
    conn.commit()
    conn.close()

    print(f"✅ Recurring schedule set:")
    print(f"   Client: {client['name']} (#{client_id})")
    print(f"   {frequency.title()} {service_type} on {preferred_day}s at {preferred_time}")
    print(f"   Zone: {zone}  |  Price: ${discounted_price:.0f} ({int(discount*100)}% recurring discount)")
    print(f"   Next service: {next_d.isoformat()}")


def recurring_view(weeks_ahead=4):
    """View upcoming recurring jobs."""
    conn = get_db()
    schedules = conn.execute("""
        SELECT r.*, c.name as client_name, cr.name as crew_name
        FROM recurring_schedules r
        JOIN clients c ON r.client_id = c.id
        LEFT JOIN crews cr ON r.crew_id = cr.id
        WHERE r.active = 1
        ORDER BY r.preferred_day, r.preferred_time
    """).fetchall()
    conn.close()

    if not schedules:
        print("📋 No active recurring schedules")
        return

    weekly_revenue = sum(
        s["price"] * (1 if s["frequency"] == "weekly" else
                      0.5 if s["frequency"] == "biweekly" else 0.25)
        for s in schedules
    )

    print(f"\n🔄 Active Recurring Schedules ({len(schedules)} total)")
    print(f"{'═' * 75}")
    print(f"  {'Client':<22} {'Service':<10} {'Freq':<9} {'Day':<4} {'Time':<6} "
          f"{'Zone':<4} {'Price':>7} {'Crew':<12}")
    print(f"{'─' * 75}")
    for s in schedules:
        print(f"  {s['client_name']:<22} {s['service_type']:<10} {s['frequency']:<9} "
              f"{s['preferred_day']:<4} {s['preferred_time']:<6} {s['zone']:<4} "
              f"${s['price']:>6.0f} {s['crew_name'] or 'Unassigned':<12}")

    print(f"{'─' * 75}")
    print(f"  Est. weekly revenue from recurring: ${weekly_revenue:,.0f}")
    print(f"  Est. monthly revenue from recurring: ${weekly_revenue * 4.33:,.0f}")
    print()


# ═══════════════════════════════════════════════════════════════════
# CREW MANAGEMENT
# ═══════════════════════════════════════════════════════════════════

def crew_status(target_date=None):
    """Show crew availability and workload."""
    if not target_date:
        target_date = date.today().isoformat()

    conn = get_db()
    crews = conn.execute("SELECT * FROM crews WHERE active = 1").fetchall()

    print(f"\n🚐 Crew Status — {target_date}")
    print("═" * 60)

    for crew in crews:
        jobs = conn.execute("""
            SELECT j.*, c.name as client_name
            FROM scheduled_jobs j
            JOIN clients c ON j.client_id = c.id
            WHERE j.crew_id = ? AND j.date = ? AND j.status != 'cancelled'
            ORDER BY j.start_time
        """, (crew["id"], target_date)).fetchall()

        total_hours = sum(SERVICE_DURATION.get(j["service_type"], 2.0) for j in jobs)
        total_revenue = sum(j["price"] or 0 for j in jobs)
        available_hours = 8.0 - total_hours

        status = "🟢 Available" if available_hours >= 2 else "🟡 Limited" if available_hours > 0 else "🔴 Full"

        print(f"\n  {crew['name']} ({crew['member_1']} + {crew['member_2']})")
        print(f"  📞 {crew['phone']}  |  {status}")
        print(f"  Jobs: {len(jobs)}  |  Hours: {total_hours:.1f}/8  |  Revenue: ${total_revenue:,.0f}")
        print(f"  Available: {max(0, available_hours):.1f} hours")

        if jobs:
            print(f"  {'─' * 48}")
            for j in jobs:
                print(f"    {j['start_time']}–{j['end_time']}  {j['client_name']:<18}  "
                      f"{j['service_type']:<10} [{j['zone']}]")

    conn.close()
    print()


# ═══════════════════════════════════════════════════════════════════
# FORECASTING & REPORTS
# ═══════════════════════════════════════════════════════════════════

def forecast(start_month, months=6, base_monthly_revenue=None):
    """Generate seasonal demand forecast."""
    conn = get_db()

    # Calculate base from history if not provided
    if not base_monthly_revenue:
        result = conn.execute("""
            SELECT AVG(monthly_rev) as avg_rev FROM (
                SELECT strftime('%Y-%m', date) as month, SUM(price) as monthly_rev
                FROM job_history
                GROUP BY month
            )
        """).fetchone()
        base_monthly_revenue = result["avg_rev"] if result["avg_rev"] else 15000

    conn.close()

    year, month = map(int, start_month.split("-"))
    crew_capacity_monthly = 22 * 3.5 * 180  # 22 workdays × 3.5 jobs/day × $180 avg

    print(f"\n📊 Seasonal Demand Forecast — InStyle Cleaning")
    print(f"   Base monthly revenue: ${base_monthly_revenue:,.0f}")
    print(f"{'═' * 75}")
    print(f"  {'Month':<10} {'Multiplier':>10} {'Projected Rev':>14} {'Jobs/Day':>9} "
          f"{'Crews Needed':>12} {'Action':>12}")
    print(f"{'─' * 75}")

    total_revenue = 0
    for i in range(months):
        m = ((month - 1 + i) % 12) + 1
        y = year + ((month - 1 + i) // 12)
        mult = SEASONAL_MULTIPLIERS[m]
        projected = base_monthly_revenue * mult
        total_revenue += projected
        jobs_per_day = (projected / 22) / 180  # 22 workdays, $180 avg job
        crews_needed = math.ceil(jobs_per_day / 3.5)  # 3.5 jobs per crew per day

        month_name = datetime(y, m, 1).strftime("%b %Y")

        if mult >= 1.4:
            action = "🔴 HIRE"
        elif mult >= 1.1:
            action = "🟡 PREP"
        elif mult <= 0.8:
            action = "⬇️  SLOW"
        else:
            action = "🟢 NORMAL"

        print(f"  {month_name:<10} {mult:>9.2f}x {projected:>13,.0f} {jobs_per_day:>8.1f} "
              f"{crews_needed:>11} {action:>12}")

    print(f"{'─' * 75}")
    print(f"  Total projected revenue ({months} months): ${total_revenue:,.0f}")
    print(f"  Average monthly: ${total_revenue/months:,.0f}")

    # Recommendations
    print(f"\n  💡 Recommendations:")
    for i in range(months):
        m = ((month - 1 + i) % 12) + 1
        y = year + ((month - 1 + i) // 12)
        mult = SEASONAL_MULTIPLIERS[m]
        month_name = datetime(y, m, 1).strftime("%b %Y")
        if mult >= 1.4:
            if m == 5:
                print(f"  • {month_name}: UF move-out surge. Pre-book apartment complexes. "
                      f"Hire 1-2 temp crews. Focus on SW zone.")
            elif m == 8:
                print(f"  • {month_name}: UF move-in PEAK. Maximum crew deployment. "
                      f"Pre-schedule property managers. SW zone will be 3x normal.")
        elif mult <= 0.8:
            print(f"  • {month_name}: Summer slow period. Focus on commercial recurring. "
                  f"Use downtime for training and equipment maintenance.")
    print()


def revenue_report(period=None):
    """Revenue summary by period."""
    conn = get_db()

    if period:
        # Specific month
        rows = conn.execute("""
            SELECT service_type, zone, COUNT(*) as jobs, SUM(price) as revenue,
                   AVG(price) as avg_price, AVG(rating) as avg_rating
            FROM job_history
            WHERE strftime('%Y-%m', date) = ?
            GROUP BY service_type, zone
            ORDER BY revenue DESC
        """, (period,)).fetchall()

        total = conn.execute("""
            SELECT COUNT(*) as total_jobs, SUM(price) as total_revenue
            FROM job_history WHERE strftime('%Y-%m', date) = ?
        """, (period,)).fetchone()

        print(f"\n💰 Revenue Report — {period}")
    else:
        rows = conn.execute("""
            SELECT service_type, zone, COUNT(*) as jobs, SUM(price) as revenue,
                   AVG(price) as avg_price, AVG(rating) as avg_rating
            FROM job_history
            GROUP BY service_type, zone
            ORDER BY revenue DESC
        """).fetchall()

        total = conn.execute("""
            SELECT COUNT(*) as total_jobs, SUM(price) as total_revenue
            FROM job_history
        """).fetchone()

        print(f"\n💰 Revenue Report — All Time")

    print("═" * 70)
    print(f"  {'Type':<12} {'Zone':<5} {'Jobs':>5} {'Revenue':>10} {'Avg Price':>10} {'Rating':>7}")
    print(f"{'─' * 70}")

    for r in rows:
        rating_str = f"{r['avg_rating']:.1f}" if r["avg_rating"] else "N/A"
        print(f"  {r['service_type']:<12} {r['zone']:<5} {r['jobs']:>5} "
              f"${r['revenue']:>9,.0f} ${r['avg_price']:>9,.0f} {rating_str:>7}")

    print(f"{'─' * 70}")
    print(f"  {'TOTAL':<18} {total['total_jobs']:>5} ${total['total_revenue']:>9,.0f}")
    conn.close()
    print()


def zone_report():
    """Job density and revenue breakdown by zone."""
    conn = get_db()
    zones = conn.execute("""
        SELECT zone, COUNT(DISTINCT client_id) as clients, COUNT(*) as total_jobs,
               SUM(price) as revenue, AVG(price) as avg_job
        FROM job_history
        GROUP BY zone
        ORDER BY revenue DESC
    """).fetchall()

    client_counts = conn.execute("""
        SELECT zone, COUNT(*) as clients FROM clients GROUP BY zone
    """).fetchall()

    conn.close()

    print(f"\n📍 Zone Performance Report")
    print("═" * 70)
    print(f"  {'Zone':<5} {'Clients':>8} {'Jobs':>6} {'Revenue':>10} {'Avg Job':>9} {'Rev/Client':>11}")
    print(f"{'─' * 70}")

    for z in zones:
        rev_per_client = z["revenue"] / z["clients"] if z["clients"] > 0 else 0
        print(f"  {z['zone']:<5} {z['clients']:>8} {z['total_jobs']:>6} "
              f"${z['revenue']:>9,.0f} ${z['avg_job']:>8,.0f} ${rev_per_client:>10,.0f}")

    print()


def dashboard():
    """Full operational dashboard — today's snapshot."""
    today = date.today().isoformat()
    conn = get_db()

    # Today's jobs
    today_jobs = conn.execute("""
        SELECT COUNT(*) as cnt, SUM(price) as rev
        FROM scheduled_jobs WHERE date = ? AND status != 'cancelled'
    """, (today,)).fetchone()

    # This week
    week_start = (date.today() - timedelta(days=date.today().weekday())).isoformat()
    week_end = (date.today() + timedelta(days=6 - date.today().weekday())).isoformat()
    week_jobs = conn.execute("""
        SELECT COUNT(*) as cnt, SUM(price) as rev
        FROM scheduled_jobs WHERE date BETWEEN ? AND ? AND status != 'cancelled'
    """, (week_start, week_end)).fetchone()

    # Active clients
    active_clients = conn.execute("""
        SELECT COUNT(DISTINCT client_id) as cnt FROM scheduled_jobs
        WHERE date >= date('now', '-30 days')
    """).fetchone()

    # Recurring revenue
    recurring_weekly = conn.execute("""
        SELECT SUM(CASE WHEN frequency='weekly' THEN price
                       WHEN frequency='biweekly' THEN price*0.5
                       WHEN frequency='monthly' THEN price*0.25 END) as weekly
        FROM recurring_schedules WHERE active = 1
    """).fetchone()

    # Average rating
    avg_rating = conn.execute("""
        SELECT AVG(rating) as avg FROM job_history
        WHERE date >= date('now', '-30 days') AND rating IS NOT NULL
    """).fetchone()

    conn.close()

    day_name = datetime.strptime(today, "%Y-%m-%d").strftime("%A")
    month_mult = SEASONAL_MULTIPLIERS.get(date.today().month, 1.0)

    print(f"\n{'═' * 60}")
    print(f"  🏠 {COMPANY_NAME} — Operational Dashboard")
    print(f"  {today} ({day_name})")
    print(f"{'═' * 60}")

    print(f"\n  📊 Today")
    print(f"  {'─' * 48}")
    print(f"  Jobs scheduled:    {today_jobs['cnt'] or 0}")
    print(f"  Expected revenue:  ${today_jobs['rev'] or 0:,.0f}")

    print(f"\n  📅 This Week ({week_start} to {week_end})")
    print(f"  {'─' * 48}")
    print(f"  Total jobs:        {week_jobs['cnt'] or 0}")
    print(f"  Expected revenue:  ${week_jobs['rev'] or 0:,.0f}")

    print(f"\n  📈 Key Metrics (30-day)")
    print(f"  {'─' * 48}")
    print(f"  Active clients:    {active_clients['cnt'] or 0}")
    weekly_val = recurring_weekly['weekly'] or 0
    print(f"  Recurring weekly:  ${weekly_val:,.0f}")
    print(f"  Recurring monthly: ${weekly_val * 4.33:,.0f}")
    rating_val = avg_rating['avg'] or 0
    print(f"  Avg rating:        {'⭐' * int(rating_val)} ({rating_val:.1f}/5)")

    print(f"\n  🌡️  Seasonal Status")
    print(f"  {'─' * 48}")
    month_name = date.today().strftime("%B")
    if month_mult >= 1.4:
        status = "🔴 SURGE MONTH"
    elif month_mult >= 1.1:
        status = "🟡 Above Average"
    elif month_mult <= 0.8:
        status = "⬇️  Below Average"
    else:
        status = "🟢 Normal"
    print(f"  {month_name} demand:    {month_mult:.2f}x ({status})")
    print()

    # Show today's schedule
    print("  📋 Today's Schedule:")
    schedule_view(today)


# ═══════════════════════════════════════════════════════════════════
# JSON OUTPUT
# ═══════════════════════════════════════════════════════════════════

def output_json(data):
    """Print data as formatted JSON."""
    print(json.dumps(data, indent=2, default=str))


# ═══════════════════════════════════════════════════════════════════
# CLI ARGUMENT PARSER
# ═══════════════════════════════════════════════════════════════════

def build_parser():
    parser = argparse.ArgumentParser(
        description=f"{COMPANY_NAME} — Business Operations CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python instyle_cli.py init
  python instyle_cli.py quote --service-type deep --sqft 1800 --rooms 4
  python instyle_cli.py schedule-view --date 2026-04-10
  python instyle_cli.py client-view --client-id 1
  python instyle_cli.py forecast --start-month 2026-04 --months 6
  python instyle_cli.py dashboard
        """
    )
    sub = parser.add_subparsers(dest="command", help="Command to run")

    # init
    p_init = sub.add_parser("init", help="Initialize database")
    p_init.add_argument("--no-sample-data", action="store_true")

    # quote
    p_quote = sub.add_parser("quote", help="Generate price quote")
    p_quote.add_argument("--service-type", required=True, choices=["standard", "deep", "move-out", "commercial"])
    p_quote.add_argument("--sqft", type=int)
    p_quote.add_argument("--rooms", type=int)
    p_quote.add_argument("--commercial-type", choices=["warehouse", "office", "retail", "medical", "food"])
    p_quote.add_argument("--addons", nargs="+", help="e.g. fridge oven windows:12")
    p_quote.add_argument("--recurring", choices=["weekly", "biweekly", "monthly"])
    p_quote.add_argument("--json", action="store_true", help="Output as JSON")

    # schedule-add
    p_sadd = sub.add_parser("schedule-add", help="Add job to schedule")
    p_sadd.add_argument("--client-id", type=int, required=True)
    p_sadd.add_argument("--crew-id", type=int, required=True)
    p_sadd.add_argument("--date", required=True)
    p_sadd.add_argument("--start-time", required=True)
    p_sadd.add_argument("--service-type", required=True, choices=["standard", "deep", "move-out", "commercial"])
    p_sadd.add_argument("--zone", required=True, choices=ZONES)
    p_sadd.add_argument("--price", type=float)
    p_sadd.add_argument("--notes", default="")

    # schedule-view
    p_sview = sub.add_parser("schedule-view", help="View schedule")
    p_sview.add_argument("--date", required=True)
    p_sview.add_argument("--end-date")

    # schedule-optimize
    p_sopt = sub.add_parser("schedule-optimize", help="Optimize crew route")
    p_sopt.add_argument("--date", required=True)
    p_sopt.add_argument("--crew-id", type=int, required=True)

    # client-add
    p_cadd = sub.add_parser("client-add", help="Add new client")
    p_cadd.add_argument("--name", required=True)
    p_cadd.add_argument("--address", required=True)
    p_cadd.add_argument("--zone", required=True, choices=ZONES)
    p_cadd.add_argument("--phone")
    p_cadd.add_argument("--email")
    p_cadd.add_argument("--sqft", type=int)
    p_cadd.add_argument("--rooms", type=int)
    p_cadd.add_argument("--notes")
    p_cadd.add_argument("--preferred-crew-id", type=int)

    # client-view
    p_cview = sub.add_parser("client-view", help="View client details")
    p_cview.add_argument("--client-id", type=int, required=True)

    # client-search
    p_csearch = sub.add_parser("client-search", help="Search clients")
    p_csearch.add_argument("--query", required=True)

    # client-list
    p_clist = sub.add_parser("client-list", help="List all clients")
    p_clist.add_argument("--zone", choices=ZONES)
    p_clist.add_argument("--sort", choices=["name", "ltv", "zone", "created"], default="name")

    # recurring-add
    p_radd = sub.add_parser("recurring-add", help="Set up recurring schedule")
    p_radd.add_argument("--client-id", type=int, required=True)
    p_radd.add_argument("--service-type", required=True, choices=["standard", "deep", "move-out", "commercial"])
    p_radd.add_argument("--frequency", required=True, choices=["weekly", "biweekly", "monthly"])
    p_radd.add_argument("--day", required=True, choices=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"])
    p_radd.add_argument("--time", required=True)
    p_radd.add_argument("--zone", required=True, choices=ZONES)
    p_radd.add_argument("--price", type=float, required=True)
    p_radd.add_argument("--crew-id", type=int)

    # recurring-view
    p_rview = sub.add_parser("recurring-view", help="View recurring schedules")
    p_rview.add_argument("--weeks", type=int, default=4)

    # crew-status
    p_crew = sub.add_parser("crew-status", help="Show crew availability")
    p_crew.add_argument("--date")

    # forecast
    p_fc = sub.add_parser("forecast", help="Seasonal demand forecast")
    p_fc.add_argument("--start-month", required=True, help="YYYY-MM")
    p_fc.add_argument("--months", type=int, default=6)
    p_fc.add_argument("--base-revenue", type=float)

    # revenue-report
    p_rev = sub.add_parser("revenue-report", help="Revenue summary")
    p_rev.add_argument("--period", help="YYYY-MM or omit for all-time")

    # zone-report
    sub.add_parser("zone-report", help="Zone performance report")

    # dashboard
    sub.add_parser("dashboard", help="Full operational dashboard")

    return parser


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "init":
        init_db(with_sample_data=not args.no_sample_data)

    elif args.command == "quote":
        quote = generate_quote(
            args.service_type, args.sqft, args.rooms,
            args.commercial_type, args.addons, args.recurring
        )
        if hasattr(args, "json") and args.json:
            output_json(quote)
        else:
            print_quote(quote)

    elif args.command == "schedule-add":
        schedule_add(args.client_id, args.crew_id, args.date,
                     args.start_time, args.service_type, args.zone,
                     args.price, args.notes)

    elif args.command == "schedule-view":
        schedule_view(args.date, args.end_date)

    elif args.command == "schedule-optimize":
        schedule_optimize(args.date, args.crew_id)

    elif args.command == "client-add":
        client_add(args.name, args.address, args.zone, args.phone,
                   args.email, args.sqft, args.rooms, args.notes,
                   args.preferred_crew_id)

    elif args.command == "client-view":
        client_view(args.client_id)

    elif args.command == "client-search":
        client_search(args.query)

    elif args.command == "client-list":
        client_list(args.zone, args.sort)

    elif args.command == "recurring-add":
        recurring_add(args.client_id, args.service_type, args.frequency,
                      args.day, args.time, args.zone, args.price, args.crew_id)

    elif args.command == "recurring-view":
        recurring_view(args.weeks)

    elif args.command == "crew-status":
        crew_status(args.date)

    elif args.command == "forecast":
        forecast(args.start_month, args.months, args.base_revenue)

    elif args.command == "revenue-report":
        revenue_report(args.period)

    elif args.command == "zone-report":
        zone_report()

    elif args.command == "dashboard":
        dashboard()


if __name__ == "__main__":
    main()
