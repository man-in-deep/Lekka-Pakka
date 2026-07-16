import psycopg2
from datetime import date
import time   # needed for the 4-second delay (free tier)
from config import DATABASE_URL, WORKER_TYPES, REGIONS
from gemini_service import get_hourly_rate


def get_connection():
    """Return a new database connection."""
    return psycopg2.connect(DATABASE_URL)


def init_db():
    """Create the date_tracker table if it doesn't exist yet."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS date_tracker (
            id SERIAL PRIMARY KEY,
            start_date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


def get_latest_start_date():
    """Get the most recent start date, or None if the table is empty."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT start_date FROM date_tracker ORDER BY id DESC LIMIT 1;")
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0] if row else None


def insert_new_start_date(new_date):
    """Insert a new start date into date_tracker."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO date_tracker (start_date) VALUES (%s);", (new_date,))
    conn.commit()
    cur.close()
    conn.close()


def workers_table_exists():
    """Check if the workers table exists."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = 'workers'
        );
    """)
    exists = cur.fetchone()[0]
    cur.close()
    conn.close()
    return exists


def create_workers_table():
    """Create the workers table (if missing)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS workers (
            id SERIAL PRIMARY KEY,
            priority INTEGER NOT NULL,
            worker_type VARCHAR(100) NOT NULL,
            hourly_rate DECIMAL NOT NULL
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


def delete_workers_table():
    """Drop the workers table."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS workers;")
    conn.commit()
    cur.close()
    conn.close()


def populate_workers():
    """
    1. Calls Gemini ONLY for Gajuwaka, Visakhapatnam (32 calls).
    2. Derives Ibrahimpatnam rate = Visakhapatnam rate - 10 (min ₹10).
    3. Derives Araku Valley rate = Visakhapatnam rate - 20 (min ₹10).
    4. Inserts 96 rows: 32 workers × 3 priorities.
    5. Sleeps 4 seconds between API calls (respects free tier 15 RPM).
    """
    create_workers_table()   # make sure table exists
    conn = get_connection()
    cur = conn.cursor()

    # We only need the first region (Visakhapatnam) for the API call
    base_location = REGIONS[0]["name"]

    for worker in WORKER_TYPES:
        # Step 1: Get Visakhapatnam wage from Gemini
        base_rate = get_hourly_rate(worker, base_location)

        # Step 2: Derive the three rates (with floor ₹10)
        rate_p1 = base_rate                 # Priority 1
        rate_p2 = max(10, base_rate - 10)   # Priority 2 (Ibrahimpatnam)
        rate_p3 = max(10, base_rate - 20)   # Priority 3 (Araku Valley)

        # Step 3: Insert three rows
        cur.execute(
            "INSERT INTO workers (priority, worker_type, hourly_rate) VALUES (%s, %s, %s);",
            (1, worker, rate_p1)
        )
        cur.execute(
            "INSERT INTO workers (priority, worker_type, hourly_rate) VALUES (%s, %s, %s);",
            (2, worker, rate_p2)
        )
        cur.execute(
            "INSERT INTO workers (priority, worker_type, hourly_rate) VALUES (%s, %s, %s);",
            (3, worker, rate_p3)
        )

        # Wait 4 seconds to stay within free‑tier 15 RPM limit
        time.sleep(4)

    conn.commit()
    cur.close()
    conn.close()


def check_and_refresh_data():
    """
    Main entry point – called before home page & every 24 hours.
    Ensures the 15‑day cycle is respected:
      - No start date? → create one & refresh.
      - Older than 15 days? → new start date & refresh.
      - Otherwise → do nothing (just ensure table exists).
    """
    init_db()
    today = date.today()
    latest_date = get_latest_start_date()

    if latest_date is None:
        # First run ever
        insert_new_start_date(today)
        refresh_workers_cycle()
        return

    days_passed = (today - latest_date).days
    if days_passed >= 15:
        # 15‑day cycle ended → refresh everything
        insert_new_start_date(today)
        refresh_workers_cycle()
    else:
        # Within the 15‑day window – make sure workers table exists
        if not workers_table_exists():
            refresh_workers_cycle()


def refresh_workers_cycle():
    """Delete old workers table and repopulate from Gemini."""
    delete_workers_table()
    populate_workers()