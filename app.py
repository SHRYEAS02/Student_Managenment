from flask import Flask, request, render_template, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"

def get_db_connection():
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/login", methods=["GET", "POST"])
def login():
    message = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
        conn.close()
        if user:
            session["user"] = username
            return redirect(url_for("index"))
        else:
            message = "❌ Invalid username or password."
    return render_template("login.html", message=message)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/", methods=["GET", "POST"])
def index():
    if "user" not in session:
        return redirect(url_for("login"))

    message = None
    student = None
    students = []
    show_all = False
    conn = get_db_connection()

    if request.method == "POST":
        action = request.form.get("action")

        if action == "add":
            try:
                name = request.form["name"]
                roll = request.form["roll"]
                dept = request.form["department"]
                year = int(request.form["year"])
                conn.execute(
                    "INSERT INTO students (name, roll_number, department, year) VALUES (?, ?, ?, ?)",
                    (name, roll, dept, year)
                )
                conn.commit()
                message = "✅ Student added successfully!"
            except:
                message = "❌ Roll number already exists or error occurred."

        elif action == "get":
            roll = request.form["roll"]
            student = conn.execute("SELECT * FROM students WHERE roll_number = ?", (roll,)).fetchone()
            if not student:
                message = "❌ Student not found."

        elif action == "get_branch":
            branch = request.form["branch"]
            students = conn.execute("SELECT * FROM students WHERE LOWER(department) = LOWER(?) ORDER BY CAST(roll_number AS INTEGER) ASC",(branch,)).fetchall()
            if not students:
                message = f"❌ No students found in the {branch} department."

        elif action == "show_all":
            students = conn.execute("SELECT * FROM students ORDER BY roll_number ASC").fetchall()
            show_all = True

        elif action == "delete":
            roll = request.form["roll"]
            existing = conn.execute("SELECT * FROM students WHERE roll_number = ?", (roll,)).fetchone()
            if existing:
                conn.execute("DELETE FROM students WHERE roll_number = ?", (roll,))
                conn.commit()
                message = f"🗑️ Student with Roll Number {roll} deleted successfully."
            else:
                message = f"❌ Student with Roll Number {roll} does not exist."

    conn.close()
    return render_template("index.html", message=message, student=student, students=students, show_all=show_all)
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)