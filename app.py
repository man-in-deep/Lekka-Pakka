from flask import Flask, render_template

app = Flask(__name__)

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
    app.run(debug=True)