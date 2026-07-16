from flask import Flask, render_template, request, session, redirect, url_for
from apscheduler.schedulers.background import BackgroundScheduler
from database import check_and_refresh_data, get_all_workers
import atexit

app = Flask(__name__)
app.secret_key = '272b5b59806b40b20b29691bcaf7af99fea3d053a338cbd0f2d80d9efb15f9cf'   # change this in production

# ---------- Background scheduler: every 24 hours ----------
scheduler = BackgroundScheduler()
scheduler.add_job(func=check_and_refresh_data, trigger="interval", hours=24)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

# ---------- Before home page request, ensure data is fresh ----------
@app.before_request
def before_home():
    if request.endpoint == 'home':
        check_and_refresh_data()

# ---------- Routes ----------
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/admin", methods=["GET", "POST"])
def admin():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == "admin" and password == "1234":
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            error = "Invalid username or password. Please try again."
    return render_template("admin_login.html", error=error)

@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin"))
    workers = get_all_workers()   # list of tuples (priority, worker_type, hourly_rate)
    return render_template("admin_dashboard.html", workers=workers)

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