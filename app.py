import sqlite3
from datetime import datetime
from pathlib import Path

from flask import Flask, flash, g, redirect, render_template, request, url_for


BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "taskforge.db"

PRIORITIES = ["Low", "Medium", "High"]
STATUSES = ["To Do", "In Progress", "Blocked", "Completed"]
SDLC_PHASES = [
    "Requirements",
    "Design",
    "Implementation",
    "Testing",
    "Documentation",
    "Bug Fixing",
]

app = Flask(__name__)
app.config["SECRET_KEY"] = "taskforge-dev-secret-key"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT NOT NULL,
            status TEXT NOT NULL,
            sdlc_phase TEXT NOT NULL,
            due_date TEXT,
            developer_notes TEXT,
            blocker_reason TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    db.commit()


@app.before_request
def before_request():
    init_db()


def validate_task(form):
    errors = []
    title = form.get("title", "").strip()

    if not title:
        errors.append("Title is required.")
    if form.get("priority") not in PRIORITIES:
        errors.append("Please choose a valid priority.")
    if form.get("status") not in STATUSES:
        errors.append("Please choose a valid status.")
    if form.get("sdlc_phase") not in SDLC_PHASES:
        errors.append("Please choose a valid SDLC phase.")

    return errors


def get_task_form_data(form):
    return {
        "title": form.get("title", "").strip(),
        "description": form.get("description", "").strip(),
        "priority": form.get("priority", "Medium"),
        "status": form.get("status", "To Do"),
        "sdlc_phase": form.get("sdlc_phase", "Implementation"),
        "due_date": form.get("due_date", ""),
        "developer_notes": form.get("developer_notes", "").strip(),
        "blocker_reason": form.get("blocker_reason", "").strip(),
    }


@app.route("/")
def dashboard():
    db = get_db()
    total_tasks = db.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    completed_tasks = db.execute(
        "SELECT COUNT(*) FROM tasks WHERE status = ?", ("Completed",)
    ).fetchone()[0]
    blocked_tasks = db.execute(
        "SELECT COUNT(*) FROM tasks WHERE status = ?", ("Blocked",)
    ).fetchone()[0]
    phase_rows = db.execute(
        """
        SELECT sdlc_phase, COUNT(*) AS count
        FROM tasks
        GROUP BY sdlc_phase
        ORDER BY sdlc_phase
        """
    ).fetchall()
    recent_tasks = db.execute(
        "SELECT * FROM tasks ORDER BY updated_at DESC LIMIT 5"
    ).fetchall()

    counts_by_phase = {phase: 0 for phase in SDLC_PHASES}
    for row in phase_rows:
        counts_by_phase[row["sdlc_phase"]] = row["count"]

    return render_template(
        "dashboard.html",
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        blocked_tasks=blocked_tasks,
        counts_by_phase=counts_by_phase,
        recent_tasks=recent_tasks,
    )


@app.route("/tasks")
def tasks():
    rows = get_db().execute("SELECT * FROM tasks ORDER BY created_at DESC").fetchall()
    return render_template("tasks.html", tasks=rows)


@app.route("/tasks/new", methods=["GET", "POST"])
def create_task():
    task = {
        "title": "",
        "description": "",
        "priority": "Medium",
        "status": "To Do",
        "sdlc_phase": "Implementation",
        "due_date": "",
        "developer_notes": "",
        "blocker_reason": "",
    }

    if request.method == "POST":
        errors = validate_task(request.form)
        task = get_task_form_data(request.form)

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("task_form.html", task=task, form_title="New Task")

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        get_db().execute(
            """
            INSERT INTO tasks (
                title, description, priority, status, sdlc_phase, due_date,
                developer_notes, blocker_reason, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                task["title"],
                task["description"],
                task["priority"],
                task["status"],
                task["sdlc_phase"],
                task["due_date"],
                task["developer_notes"],
                task["blocker_reason"],
                now,
                now,
            ),
        )
        get_db().commit()
        flash("Task created successfully.", "success")
        return redirect(url_for("tasks"))

    return render_template("task_form.html", task=task, form_title="New Task")


@app.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
def edit_task(task_id):
    db = get_db()
    task = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()

    if task is None:
        flash("Task not found.", "warning")
        return redirect(url_for("tasks"))

    if request.method == "POST":
        errors = validate_task(request.form)
        task_data = get_task_form_data(request.form)

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template(
                "task_form.html", task=task_data, form_title="Edit Task"
            )

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.execute(
            """
            UPDATE tasks
            SET title = ?, description = ?, priority = ?, status = ?,
                sdlc_phase = ?, due_date = ?, developer_notes = ?,
                blocker_reason = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                task_data["title"],
                task_data["description"],
                task_data["priority"],
                task_data["status"],
                task_data["sdlc_phase"],
                task_data["due_date"],
                task_data["developer_notes"],
                task_data["blocker_reason"],
                now,
                task_id,
            ),
        )
        db.commit()
        flash("Task updated successfully.", "success")
        return redirect(url_for("tasks"))

    return render_template("task_form.html", task=task, form_title="Edit Task")


@app.route("/tasks/<int:task_id>/delete", methods=["POST"])
def delete_task(task_id):
    db = get_db()
    db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    db.commit()
    flash("Task deleted successfully.", "success")
    return redirect(url_for("tasks"))


@app.context_processor
def inject_options():
    return {
        "priorities": PRIORITIES,
        "statuses": STATUSES,
        "sdlc_phases": SDLC_PHASES,
    }


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=True)
