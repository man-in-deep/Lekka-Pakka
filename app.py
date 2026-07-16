from flask import Flask, render_template, request
from apscheduler.schedulers.background import BackgroundScheduler
from database import check_and_refresh_data
import atexit

app = Flask(__name__)

# --- Background scheduler: every 24 hours ---
scheduler = BackgroundScheduler()
scheduler.add_job(func=check_and_refresh_data, trigger="interval", hours=24)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

# --- Before every home page request, verify data is fresh ---
@app.before_request
def before_home():
    if request.endpoint == 'home':
        check_and_refresh_data()

# --- Routes (your existing UI) ---
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/admin")
def admin():
    return render_template("admin_login.html")

@app.route("/contractor")
def contractor():
    return render_template("contractor_login.html")

@app.route("/labour")
def labour():
    return render_template("labour_login.html")

if __name__ == "__main__":
    # Initial check at application startup
    check_and_refresh_data()
    app.run(debug=True)