from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from database import check_and_refresh_data, get_all_workers, init_contractor_table, save_contractor_id
from excel_reader import get_map_data
import atexit

app = Flask(__name__)
app.secret_key = '272b5b59806b40b20b29691bcaf7af99fea3d053a338cbd0f2d80d9efb15f9cf'

scheduler = BackgroundScheduler()
scheduler.add_job(func=check_and_refresh_data, trigger="interval", hours=24)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

@app.before_request
def before_home():
    if request.endpoint == 'home':
        check_and_refresh_data()

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
    workers = get_all_workers()
    return render_template("admin_dashboard.html", workers=workers)

@app.route("/contractor")
def contractor():
    return render_template("contractor_login.html")

@app.route("/contractor/proceed", methods=["POST"])
def contractor_proceed():
    data = request.get_json()
    contractor_id = data.get("contractor_id", "").strip()
    if not contractor_id:
        return jsonify({"error": "No ID provided"}), 400
    init_contractor_table()
    save_contractor_id(contractor_id)
    session["contractor_id"] = contractor_id
    return jsonify({"redirect": url_for("contractor_dashboard")})

@app.route("/contractor/dashboard")
def contractor_dashboard():
    if not session.get("contractor_id"):
        return redirect(url_for("contractor"))
    contractor_id = session["contractor_id"]
    map_data = get_map_data()
    workers = get_all_workers()
    return render_template("contractor_dashboard.html",
                           contractor_id=contractor_id,
                           map_data=map_data,
                           workers=workers)

# ---------- Labour Routes (appended, no changes above) ----------
from database import init_labourer_table, save_labourer_id, get_labour_earnings, save_labour_entry

@app.route("/labour")
def labour():
    return render_template("labour_login.html")

@app.route("/labour/proceed", methods=["POST"])
def labour_proceed():
    data = request.get_json()
    labour_id = data.get("labour_id", "").strip()
    if not labour_id:
        return jsonify({"error": "No ID provided"}), 400
    init_labourer_table()
    save_labourer_id(labour_id)
    session["labour_id"] = labour_id
    return jsonify({"redirect": url_for("labour_dashboard")})

@app.route("/labour/dashboard")
def labour_dashboard():
    if not session.get("labour_id"):
        return redirect(url_for("labour"))
    labour_id = session["labour_id"]
    map_data = get_map_data()
    workers = get_all_workers()
    earnings = get_labour_earnings(labour_id)
    total_contractor_paid = sum(e["contractor_paid"] for e in earnings)
    return render_template("labour_dashboard.html",
                           labour_id=labour_id,
                           map_data=map_data,
                           workers=workers,
                           earnings=earnings,
                           total_contractor_paid=total_contractor_paid)

@app.route("/labour/save_entry", methods=["POST"])
def labour_save_entry():
    if not session.get("labour_id"):
        return jsonify({"error": "Not logged in"}), 401
    labour_id = session["labour_id"]
    data = request.get_json()
    worker_type = data.get("worker_type")
    hours = data.get("hours")
    calculated = data.get("calculated")
    contractor_paid = data.get("contractor_paid")
    if not all([worker_type, hours, calculated, contractor_paid]):
        return jsonify({"error": "Missing fields"}), 400
    try:
        hours = float(hours)
        calculated = float(calculated)
        contractor_paid = float(contractor_paid)
    except ValueError:
        return jsonify({"error": "Invalid numbers"}), 400
    if hours > 10:
        return jsonify({"error": "Hours cannot exceed 10"}), 400
    save_labour_entry(labour_id, worker_type, hours, calculated, contractor_paid)
    return jsonify({"success": True})

if __name__ == "__main__":
    check_and_refresh_data()
    app.run(debug=True)