import psycopg2
from datetime import date
import time
from config import DATABASE_URL, WORKER_TYPES, REGIONS
from gemini_service import get_hourly_rate


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def init_db():
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
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT start_date FROM date_tracker ORDER BY id DESC LIMIT 1;")
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0] if row else None


def insert_new_start_date(new_date):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO date_tracker (start_date) VALUES (%s);", (new_date,))
    conn.commit()
    cur.close()
    conn.close()


def workers_table_exists():
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
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS workers;")
    conn.commit()
    cur.close()
    conn.close()


def populate_workers():
    create_workers_table()
    conn = get_connection()
    cur = conn.cursor()
    base_location = REGIONS[0]["name"]
    for worker in WORKER_TYPES:
        base_rate = get_hourly_rate(worker, base_location)
        rate_p1 = base_rate
        rate_p2 = max(10, base_rate - 10)
        rate_p3 = max(10, base_rate - 20)
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
        time.sleep(4)
    conn.commit()
    cur.close()
    conn.close()


def check_and_refresh_data():
    init_db()
    today = date.today()
    latest_date = get_latest_start_date()
    if latest_date is None:
        insert_new_start_date(today)
        refresh_workers_cycle()
        return
    days_passed = (today - latest_date).days
    if days_passed >= 15:
        insert_new_start_date(today)
        refresh_workers_cycle()
    else:
        if not workers_table_exists():
            refresh_workers_cycle()


def refresh_workers_cycle():
    delete_workers_table()
    populate_workers()


def get_all_workers():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT priority, worker_type, hourly_rate FROM workers ORDER BY priority, worker_type;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def init_contractor_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS contractors (
            id SERIAL PRIMARY KEY,
            contractor_id TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


def save_contractor_id(contractor_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO contractors (contractor_id)
        VALUES (%s)
        ON CONFLICT (contractor_id) DO NOTHING;
    """, (contractor_id,))
    conn.commit()
    cur.close()
    conn.close()


# ========== LABOUR FUNCTIONS (appended below) ==========
def init_labourer_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS labourers (
            id SERIAL PRIMARY KEY,
            labour_id TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


def save_labourer_id(labour_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO labourers (labour_id)
        VALUES (%s)
        ON CONFLICT (labour_id) DO NOTHING;
    """, (labour_id,))
    conn.commit()
    cur.close()
    conn.close()


def init_labour_earnings_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS labour_earnings (
            id SERIAL PRIMARY KEY,
            labour_id TEXT NOT NULL,
            date DATE NOT NULL DEFAULT CURRENT_DATE,
            worker_type VARCHAR(100) NOT NULL,
            hours DECIMAL NOT NULL,
            calculated_earnings DECIMAL NOT NULL,
            contractor_paid DECIMAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


def save_labour_entry(labour_id, worker_type, hours, calculated, contractor_paid):
    init_labour_earnings_table()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO labour_earnings (labour_id, worker_type, hours, calculated_earnings, contractor_paid)
        VALUES (%s, %s, %s, %s, %s);
    """, (labour_id, worker_type, hours, calculated, contractor_paid))
    conn.commit()
    cur.close()
    conn.close()


def get_labour_earnings(labour_id):
    init_labour_earnings_table()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT date, worker_type, hours, calculated_earnings, contractor_paid
        FROM labour_earnings
        WHERE labour_id = %s
        ORDER BY date DESC;
    """, (labour_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {
            "date": row[0].strftime("%Y-%m-%d"),
            "worker_type": row[1],
            "hours": float(row[2]),
            "calculated_earnings": float(row[3]),
            "contractor_paid": float(row[4])
        }
        for row in rows
    ]