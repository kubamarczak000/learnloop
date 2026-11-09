"""Widoki i walidacja formularzy aplikacji."""

import calendar
from datetime import date, timedelta
import re
import sqlite3

from flask import Blueprint, abort, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db

bp = Blueprint("main", __name__)
STATUSES = {"active", "completed", "paused"}


@bp.before_app_request
def load_user_and_require_login():
    user_id = session.get("user_id")
    g.user = None
    if user_id is not None:
        g.user = get_db().execute(
            "SELECT id, email, role FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        if g.user is None:
            session.clear()
    if request.endpoint == "static":
        return None
    if g.user is not None and g.user["role"] == "root":
        if request.endpoint in {"main.logout", "main.switch_root_view"}:
            return None
        if session.get("root_user_mode"):
            if request.endpoint in {"main.admin_dashboard", "main.login", "main.register"}:
                return redirect(url_for("main.index"))
            return None
        if request.endpoint == "main.admin_dashboard":
            return None
        return redirect(url_for("main.admin_dashboard"))
    if request.endpoint in {"main.login", "main.register"}:
        return None
    if request.endpoint == "main.admin_dashboard":
        abort(403)
    if g.user is None:
        return redirect(url_for("main.login", next=request.full_path.rstrip("?")))
    return None


def _current_user_id() -> int:
    return g.user["id"]


def _safe_next_path(candidate: str | None) -> str:
    if candidate and candidate.startswith("/") and not candidate.startswith("//"):
        return candidate
    return url_for("main.index")


@bp.route("/register", methods=["GET", "POST"])
def register():
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    errors = []
    if request.method == "POST":
        if len(email) > 254 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            errors.append("Podaj poprawny adres e-mail.")
        if len(password) < 10:
            errors.append("Hasło musi mieć co najmniej 10 znaków.")
        elif len(password) > 128:
            errors.append("Hasło może mieć maksymalnie 128 znaków.")
        if not errors:
            connection = get_db()
            try:
                connection.execute("BEGIN IMMEDIATE")
                connection.execute(
                    "INSERT INTO users (email, password_hash) VALUES (?, ?)",
                    (email, generate_password_hash(password)),
                )
                user_id = connection.execute("SELECT last_insert_rowid()").fetchone()[0]
                is_first_regular_user = (
                    connection.execute("SELECT COUNT(*) FROM users WHERE role = 'user'").fetchone()[0]
                    == 1
                )
                if is_first_regular_user:
                    # Przenieś istniejące lokalne dane do pierwszego konta zamiast je kasować.
                    for table in ("goals", "calendar_events", "work_tasks"):
                        connection.execute(f"UPDATE {table} SET user_id = ? WHERE user_id IS NULL", (user_id,))
                    connection.execute(
                        """INSERT OR IGNORE INTO user_settings (user_id, setting_key, setting_value)
                           SELECT ?, setting_key, setting_value FROM app_settings""",
                        (user_id,),
                    )
                connection.execute(
                    """INSERT OR IGNORE INTO user_settings (user_id, setting_key, setting_value)
                       VALUES (?, 'weekly_goal_minutes', '180')""",
                    (user_id,),
                )
                connection.commit()
            except sqlite3.IntegrityError:
                connection.rollback()
                errors.append("Konto z tym adresem e-mail już istnieje.")
            else:
                session.clear()
                session["user_id"] = user_id
                flash("Konto utworzone. Witaj w LearnLoop!", "success")
                return redirect(url_for("main.index"))
    return render_template("auth.html", mode="register", email=email, errors=errors)


@bp.route("/login", methods=["GET", "POST"])
def login():
    email = request.form.get("email", "").strip().lower()
    if request.method == "POST":
        password = request.form.get("password", "")
        user = get_db().execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Nieprawidłowy e-mail lub hasło.", "error")
        else:
            session.clear()
            session["user_id"] = user["id"]
            if user["role"] == "root":
                return redirect(url_for("main.admin_dashboard"))
            return redirect(_safe_next_path(request.args.get("next")))
    return render_template("auth.html", mode="login", email=email, errors=[])


@bp.post("/logout")
def logout():
    session.clear()
    flash("Wylogowano z LearnLoop.", "success")
    return redirect(url_for("main.login"))


@bp.post("/admin/switch-view")
def switch_root_view():
    if g.user is None or g.user["role"] != "root":
        abort(403)
    target = request.form.get("target", "")
    if target == "user":
        session["root_user_mode"] = True
        flash("Przełączono na Twój prywatny planer.", "success")
        return redirect(url_for("main.index"))
    if target == "admin":
        session.pop("root_user_mode", None)
        flash("Wrócono do panelu administratora.", "success")
        return redirect(url_for("main.admin_dashboard"))
    abort(400)


@bp.get("/admin")
def admin_dashboard():
    connection = get_db()
    users = connection.execute(
        """SELECT u.id, u.email, u.role, u.created_at,
                  (SELECT COUNT(*) FROM goals g WHERE g.user_id = u.id) AS goal_count,
                  (SELECT COUNT(*) FROM work_tasks t WHERE t.user_id = u.id) AS task_count,
                  (SELECT COUNT(*) FROM calendar_events e WHERE e.user_id = u.id) AS event_count
           FROM users u ORDER BY u.created_at"""
    ).fetchall()
    goals = connection.execute(
        """SELECT g.title, g.category, g.status, g.target_date, u.email
           FROM goals g LEFT JOIN users u ON u.id = g.user_id
           ORDER BY g.created_at DESC LIMIT 100"""
    ).fetchall()
    tasks = connection.execute(
        """SELECT t.title, t.status, t.priority, t.due_date, t.estimate_minutes, u.email
           FROM work_tasks t LEFT JOIN users u ON u.id = t.user_id
           ORDER BY CASE t.status WHEN 'in_progress' THEN 0 WHEN 'todo' THEN 1 ELSE 2 END,
                    t.due_date LIMIT 100"""
    ).fetchall()
    events = connection.execute(
        """SELECT e.title, e.event_type, e.event_date, u.email
           FROM calendar_events e LEFT JOIN users u ON u.id = e.user_id
           ORDER BY e.event_date LIMIT 100"""
    ).fetchall()
    sessions = connection.execute(
        """SELECT s.studied_on, s.minutes, s.note, g.title AS goal_title, u.email
           FROM study_sessions s JOIN goals g ON g.id = s.goal_id
           LEFT JOIN users u ON u.id = g.user_id
           ORDER BY s.studied_on DESC, s.id DESC LIMIT 100"""
    ).fetchall()
    plans = connection.execute(
        """SELECT p.study_date, p.minutes, p.label, e.title AS event_title, u.email
           FROM planned_sessions p JOIN calendar_events e ON e.id = p.event_id
           LEFT JOIN users u ON u.id = e.user_id
           ORDER BY p.study_date LIMIT 100"""
    ).fetchall()
    return render_template(
        "admin.html", users=users, goals=goals, tasks=tasks, events=events, sessions=sessions, plans=plans
    )


def _goal_or_404(goal_id: int) -> sqlite3.Row:
    goal = get_db().execute(
        "SELECT * FROM goals WHERE id = ? AND user_id = ?", (goal_id, _current_user_id())
    ).fetchone()
    if goal is None:
        abort(404)
    return goal


def _goal_form_values() -> tuple[dict, list[str]]:
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    category = request.form.get("category", "Inne").strip() or "Inne"
    target_date = request.form.get("target_date", "").strip() or None
    errors = []
    if not title:
        errors.append("Podaj nazwę celu.")
    elif len(title) > 100:
        errors.append("Nazwa celu może mieć maksymalnie 100 znaków.")
    if len(description) > 2000:
        errors.append("Opis może mieć maksymalnie 2000 znaków.")
    if len(category) > 40:
        errors.append("Kategoria może mieć maksymalnie 40 znaków.")
    if target_date:
        try:
            date.fromisoformat(target_date)
        except ValueError:
            errors.append("Termin musi być poprawną datą.")
    return {
        "title": title,
        "description": description,
        "category": category,
        "target_date": target_date,
    }, errors


@bp.get("/")
def index():
    connection = get_db()
    selected_status = request.args.get("status", "all")
    if selected_status not in {"all", *STATUSES}:
        selected_status = "all"
    search = request.args.get("q", "").strip()[:100]

    conditions, parameters = ["g.user_id = ?"], [_current_user_id()]
    if selected_status != "all":
        conditions.append("g.status = ?")
        parameters.append(selected_status)
    if search:
        conditions.append("(g.title LIKE ? OR g.category LIKE ?)")
        parameters.extend((f"%{search}%", f"%{search}%"))
    where = f"WHERE {' AND '.join(conditions)}"
    goals = connection.execute(
        f"""SELECT g.*,
                   COALESCE(SUM(s.minutes), 0) AS total_minutes,
                  COUNT(s.id) AS session_count
            FROM goals g LEFT JOIN study_sessions s ON s.goal_id = g.id
            {where}
            GROUP BY g.id
            ORDER BY CASE g.status WHEN 'active' THEN 0 WHEN 'paused' THEN 1 ELSE 2 END,
                     CASE WHEN g.target_date IS NULL THEN 1 ELSE 0 END, g.target_date, g.created_at DESC""",
        parameters,
    ).fetchall()
    stats = connection.execute(
        """SELECT COUNT(*) AS goal_count,
                  SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) AS active_count,
                  SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed_count
           FROM goals WHERE user_id = ?""",
        (_current_user_id(),),
    ).fetchone()
    study = connection.execute(
        """SELECT COALESCE(SUM(s.minutes), 0) AS minutes FROM study_sessions s
           JOIN goals g ON g.id = s.goal_id WHERE g.user_id = ?""",
        (_current_user_id(),),
    ).fetchone()["minutes"]
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    week_minutes = connection.execute(
        """SELECT COALESCE(SUM(s.minutes), 0) AS minutes FROM study_sessions s
           JOIN goals g ON g.id = s.goal_id
           WHERE g.user_id = ? AND s.studied_on BETWEEN ? AND ?""",
        (_current_user_id(), week_start.isoformat(), week_end.isoformat()),
    ).fetchone()["minutes"]
    weekly_goal_row = connection.execute(
        """SELECT setting_value FROM user_settings
           WHERE user_id = ? AND setting_key = 'weekly_goal_minutes'""",
        (_current_user_id(),),
    ).fetchone()
    if weekly_goal_row is None:
        weekly_goal = 180
        connection.execute(
            """INSERT INTO user_settings (user_id, setting_key, setting_value)
               VALUES (?, 'weekly_goal_minutes', ?)""",
            (_current_user_id(), str(weekly_goal)),
        )
        connection.commit()
    else:
        weekly_goal = int(weekly_goal_row["setting_value"])
    weekly_progress = min(round(week_minutes / weekly_goal * 100), 100)
    return render_template(
        "index.html",
        goals=goals,
        stats=stats,
        total_minutes=study,
        week_minutes=week_minutes,
        week_start=week_start,
        week_end=week_end,
        weekly_goal=weekly_goal,
        weekly_progress=weekly_progress,
        selected_status=selected_status,
        search=search,
    )


@bp.post("/settings/weekly-goal")
def update_weekly_goal():
    raw_minutes = request.form.get("weekly_goal_minutes", "")
    try:
        weekly_goal = int(raw_minutes)
    except ValueError:
        weekly_goal = 0
    if not 15 <= weekly_goal <= 10080:
        flash("Tygodniowy cel musi wynosić od 15 do 10 080 minut.", "error")
        return redirect(url_for("main.index"))
    connection = get_db()
    connection.execute(
        """UPDATE user_settings SET setting_value = ?
           WHERE user_id = ? AND setting_key = 'weekly_goal_minutes'""",
        (str(weekly_goal), _current_user_id()),
    )
    connection.commit()
    flash("Zapisano tygodniowy cel nauki.", "success")
    return redirect(url_for("main.index"))


@bp.get("/calendar")
def calendar_view():
    today = date.today()
    try:
        year = int(request.args.get("year", today.year))
        month = int(request.args.get("month", today.month))
        if not 2000 <= year <= 2100 or not 1 <= month <= 12:
            raise ValueError
    except ValueError:
        abort(400)

    month_calendar = calendar.Calendar(firstweekday=0).monthdatescalendar(year, month)
    first_day, last_day = month_calendar[0][0], month_calendar[-1][-1]
    events = get_db().execute(
        """SELECT e.*, g.title AS goal_title
           FROM calendar_events e LEFT JOIN goals g ON g.id = e.goal_id AND g.user_id = e.user_id
           WHERE e.user_id = ? AND e.event_date BETWEEN ? AND ? ORDER BY e.event_date, e.title""",
        (_current_user_id(), first_day.isoformat(), last_day.isoformat()),
    ).fetchall()
    events_by_date = {}
    for event in events:
        events_by_date.setdefault(event["event_date"], []).append(event)

    work_tasks = get_db().execute(
        """SELECT * FROM work_tasks WHERE user_id = ? AND due_date BETWEEN ? AND ?
           ORDER BY CASE priority WHEN 'high' THEN 0 WHEN 'medium' THEN 1 ELSE 2 END, title""",
        (_current_user_id(), first_day.isoformat(), last_day.isoformat()),
    ).fetchall()
    tasks_by_date = {}
    for task in work_tasks:
        tasks_by_date.setdefault(task["due_date"], []).append(task)

    connection = get_db()
    upcoming_events = connection.execute(
        """SELECT e.*, g.title AS goal_title,
                  (SELECT COUNT(*) FROM planned_sessions p WHERE p.event_id = e.id) AS plan_count
           FROM calendar_events e LEFT JOIN goals g ON g.id = e.goal_id AND g.user_id = e.user_id
           WHERE e.user_id = ? AND e.event_date >= ? ORDER BY e.event_date, e.id LIMIT 8""",
        (_current_user_id(), today.isoformat()),
    ).fetchall()
    plans_by_event = {}
    for event in upcoming_events:
        plans_by_event[event["id"]] = {
            "count": event["plan_count"],
            "items": connection.execute(
                "SELECT * FROM planned_sessions WHERE event_id = ? ORDER BY study_date LIMIT 7",
                (event["id"],),
            ).fetchall(),
        }

    previous = date(year, month, 1) - timedelta(days=1)
    next_month = date(year, month, calendar.monthrange(year, month)[1]) + timedelta(days=1)
    goals = connection.execute(
        "SELECT id, title FROM goals WHERE user_id = ? AND status != 'completed' ORDER BY title",
        (_current_user_id(),),
    ).fetchall()
    return render_template(
        "calendar.html",
        year=year,
        month=month,
        today=today,
        month_calendar=month_calendar,
        events_by_date=events_by_date,
        tasks_by_date=tasks_by_date,
        upcoming_events=upcoming_events,
        plans_by_event=plans_by_event,
        goals=goals,
        previous_month=previous.month,
        previous_year=previous.year,
        next_month=next_month.month,
        next_year=next_month.year,
    )


@bp.get("/tasks")
def work_tasks_view():
    selected_status = request.args.get("status", "all")
    valid_statuses = {"all", "todo", "in_progress", "done"}
    if selected_status not in valid_statuses:
        selected_status = "all"
    if selected_status != "all":
        condition = "WHERE user_id = ? AND status = ?"
        parameters = (_current_user_id(), selected_status)
    else:
        condition = "WHERE user_id = ?"
        parameters = (_current_user_id(),)
    tasks = get_db().execute(
        f"""SELECT * FROM work_tasks {condition}
            ORDER BY CASE status WHEN 'in_progress' THEN 0 WHEN 'todo' THEN 1 ELSE 2 END,
                     CASE priority WHEN 'high' THEN 0 WHEN 'medium' THEN 1 ELSE 2 END,
                     CASE WHEN due_date IS NULL THEN 1 ELSE 0 END, due_date, created_at DESC""",
        parameters,
    ).fetchall()
    counts = get_db().execute(
        """SELECT COUNT(*) AS total,
                  SUM(CASE WHEN status = 'todo' THEN 1 ELSE 0 END) AS todo,
                  SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) AS in_progress,
                  SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END) AS done
           FROM work_tasks WHERE user_id = ?""",
        (_current_user_id(),),
    ).fetchone()
    return render_template("tasks.html", tasks=tasks, counts=counts, selected_status=selected_status)


@bp.post("/tasks")
def add_work_task():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    raw_due_date = request.form.get("due_date", "").strip()
    priority = request.form.get("priority", "medium")
    raw_estimate = request.form.get("estimate_minutes", "30")
    errors = []
    if not title:
        errors.append("Podaj nazwę zadania.")
    elif len(title) > 120:
        errors.append("Nazwa zadania może mieć maksymalnie 120 znaków.")
    if len(description) > 2000:
        errors.append("Opis może mieć maksymalnie 2000 znaków.")
    due_date = None
    if raw_due_date:
        try:
            due_date = date.fromisoformat(raw_due_date).isoformat()
        except ValueError:
            errors.append("Wybierz poprawny termin zadania.")
    if priority not in {"low", "medium", "high"}:
        errors.append("Wybierz poprawny priorytet.")
    try:
        estimate_minutes = int(raw_estimate)
    except ValueError:
        estimate_minutes = 0
    if not 5 <= estimate_minutes <= 1440:
        errors.append("Szacowany czas musi wynosić od 5 do 1440 minut.")
    if errors:
        for error in errors:
            flash(error, "error")
        return redirect(url_for("main.work_tasks_view"))

    get_db().execute(
        """INSERT INTO work_tasks
           (user_id, title, description, due_date, priority, estimate_minutes)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (_current_user_id(), title, description, due_date, priority, estimate_minutes),
    )
    get_db().commit()
    flash("Dodano zadanie do planu pracy.", "success")
    return redirect(url_for("main.work_tasks_view"))


@bp.post("/tasks/<int:task_id>/status")
def update_work_task_status(task_id: int):
    status = request.form.get("status", "")
    if status not in {"todo", "in_progress", "done"}:
        abort(400)
    connection = get_db()
    task = connection.execute(
        "SELECT id FROM work_tasks WHERE id = ? AND user_id = ?", (task_id, _current_user_id())
    ).fetchone()
    if task is None:
        abort(404)
    connection.execute(
        "UPDATE work_tasks SET status = ? WHERE id = ? AND user_id = ?",
        (status, task_id, _current_user_id()),
    )
    connection.commit()
    flash("Zmieniono status zadania.", "success")
    return redirect(url_for("main.work_tasks_view"))


@bp.post("/tasks/<int:task_id>/delete")
def delete_work_task(task_id: int):
    connection = get_db()
    cursor = connection.execute(
        "DELETE FROM work_tasks WHERE id = ? AND user_id = ?", (task_id, _current_user_id())
    )
    if cursor.rowcount == 0:
        abort(404)
    connection.commit()
    flash("Usunięto zadanie.", "success")
    return redirect(url_for("main.work_tasks_view"))


@bp.post("/calendar/events")
def add_calendar_event():
    title = request.form.get("title", "").strip()
    raw_date = request.form.get("event_date", "").strip()
    event_type = request.form.get("event_type", "other")
    notes = request.form.get("notes", "").strip()
    raw_goal_id = request.form.get("goal_id", "").strip()
    errors = []
    try:
        event_date = date.fromisoformat(raw_date)
        if event_date < date.today():
            errors.append("Wybierz dzisiejszą lub przyszłą datę.")
        elif event_date > date.today() + timedelta(days=730):
            errors.append("Wydarzenie może być maksymalnie 2 lata w przyszłości.")
    except ValueError:
        event_date = None
        errors.append("Wybierz poprawną datę wydarzenia.")
    if not title:
        errors.append("Podaj nazwę wydarzenia.")
    elif len(title) > 100:
        errors.append("Nazwa wydarzenia może mieć maksymalnie 100 znaków.")
    if event_type not in {"exam", "colloquium", "deadline", "other"}:
        errors.append("Wybierz poprawny typ wydarzenia.")
    if len(notes) > 1000:
        errors.append("Notatka może mieć maksymalnie 1000 znaków.")

    goal_id = None
    if raw_goal_id:
        try:
            goal_id = int(raw_goal_id)
            if get_db().execute(
                "SELECT 1 FROM goals WHERE id = ? AND user_id = ?", (goal_id, _current_user_id())
            ).fetchone() is None:
                errors.append("Wybrany cel nauki nie istnieje.")
        except ValueError:
            errors.append("Wybierz poprawny cel nauki.")

    if errors:
        for error in errors:
            flash(error, "error")
        return redirect(url_for("main.calendar_view"))

    connection = get_db()
    connection.execute(
        """INSERT INTO calendar_events (user_id, title, event_date, event_type, goal_id, notes)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (_current_user_id(), title, event_date.isoformat(), event_type, goal_id, notes),
    )
    connection.commit()
    flash("Dodano wydarzenie do kalendarza.", "success")
    return redirect(url_for("main.calendar_view", year=event_date.year, month=event_date.month))


@bp.post("/calendar/events/<int:event_id>/plan")
def generate_study_plan(event_id: int):
    connection = get_db()
    event = connection.execute(
        """SELECT e.*, g.title AS goal_title FROM calendar_events e
           LEFT JOIN goals g ON g.id = e.goal_id AND g.user_id = e.user_id
           WHERE e.id = ? AND e.user_id = ?""",
        (event_id, _current_user_id()),
    ).fetchone()
    if event is None:
        abort(404)
    exam_date = date.fromisoformat(event["event_date"])
    study_days = []
    day = date.today()
    while day < exam_date:
        if day.weekday() < 5:
            study_days.append(day)
        day += timedelta(days=1)
    study_days = study_days[-30:]
    if not study_days:
        flash("Przed tym wydarzeniem nie ma już dni roboczych na planowanie.", "error")
        return redirect(url_for("main.calendar_view", year=exam_date.year, month=exam_date.month))

    connection.execute("DELETE FROM planned_sessions WHERE event_id = ?", (event_id,))
    label = f"Powtórka: {event['goal_title']}" if event["goal_title"] else f"Przygotowanie: {event['title']}"
    connection.executemany(
        "INSERT INTO planned_sessions (event_id, study_date, minutes, label) VALUES (?, ?, 30, ?)",
        [(event_id, study_day.isoformat(), label) for study_day in study_days],
    )
    connection.commit()
    flash(f"Ułożono plan: {len(study_days)} sesji po 30 minut.", "success")
    return redirect(url_for("main.calendar_view", year=exam_date.year, month=exam_date.month))


@bp.post("/calendar/events/<int:event_id>/delete")
def delete_calendar_event(event_id: int):
    connection = get_db()
    event = connection.execute(
        "SELECT event_date FROM calendar_events WHERE id = ? AND user_id = ?",
        (event_id, _current_user_id()),
    ).fetchone()
    if event is None:
        abort(404)
    connection.execute("DELETE FROM calendar_events WHERE id = ?", (event_id,))
    connection.commit()
    event_date = date.fromisoformat(event["event_date"])
    flash("Usunięto wydarzenie i jego plan nauki.", "success")
    return redirect(url_for("main.calendar_view", year=event_date.year, month=event_date.month))


@bp.route("/goals/new", methods=["GET", "POST"])
def new_goal():
    values = {"title": "", "description": "", "category": "Inne", "target_date": ""}
    errors = []
    if request.method == "POST":
        values, errors = _goal_form_values()
        if not errors:
            get_db().execute(
                """INSERT INTO goals (user_id, title, description, category, target_date)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    _current_user_id(),
                    values["title"],
                    values["description"],
                    values["category"],
                    values["target_date"],
                ),
            )
            get_db().commit()
            flash("Dodano nowy cel nauki.", "success")
            return redirect(url_for("main.index"))
    return render_template("goal_form.html", values=values, errors=errors, page_title="Nowy cel")


@bp.route("/goals/<int:goal_id>/edit", methods=["GET", "POST"])
def edit_goal(goal_id: int):
    goal = _goal_or_404(goal_id)
    values = dict(goal)
    errors = []
    if request.method == "POST":
        values, errors = _goal_form_values()
        if not errors:
            get_db().execute(
                "UPDATE goals SET title = ?, description = ?, category = ?, target_date = ? WHERE id = ?",
                (values["title"], values["description"], values["category"], values["target_date"], goal_id),
            )
            get_db().commit()
            flash("Zapisano zmiany w celu.", "success")
            return redirect(url_for("main.goal_detail", goal_id=goal_id))
    return render_template("goal_form.html", values=values, errors=errors, page_title="Edytuj cel")


@bp.get("/goals/<int:goal_id>")
def goal_detail(goal_id: int):
    connection = get_db()
    goal = _goal_or_404(goal_id)
    sessions = connection.execute(
        "SELECT * FROM study_sessions WHERE goal_id = ? ORDER BY studied_on DESC, id DESC",
        (goal_id,),
    ).fetchall()
    total_minutes = sum(session["minutes"] for session in sessions)
    return render_template("goal_detail.html", goal=goal, sessions=sessions, total_minutes=total_minutes)


@bp.post("/goals/<int:goal_id>/status")
def update_status(goal_id: int):
    _goal_or_404(goal_id)
    status = request.form.get("status", "")
    if status not in STATUSES:
        abort(400)
    get_db().execute("UPDATE goals SET status = ? WHERE id = ?", (status, goal_id))
    get_db().commit()
    flash("Zmieniono status celu.", "success")
    next_url = request.form.get("next", "")
    if not next_url.startswith("/") or next_url.startswith("//"):
        next_url = url_for("main.goal_detail", goal_id=goal_id)
    return redirect(next_url)


@bp.post("/goals/<int:goal_id>/delete")
def delete_goal(goal_id: int):
    _goal_or_404(goal_id)
    get_db().execute("DELETE FROM goals WHERE id = ?", (goal_id,))
    get_db().commit()
    flash("Usunięto cel i przypisane do niego sesje.", "success")
    return redirect(url_for("main.index"))


@bp.post("/goals/<int:goal_id>/sessions")
def add_session(goal_id: int):
    goal = _goal_or_404(goal_id)
    raw_minutes = request.form.get("minutes", "")
    note = request.form.get("note", "").strip()
    studied_on = request.form.get("studied_on", "").strip()
    try:
        minutes = int(raw_minutes)
    except ValueError:
        minutes = 0
    errors = []
    if not 1 <= minutes <= 1440:
        errors.append("Czas sesji musi wynosić od 1 do 1440 minut.")
    try:
        date.fromisoformat(studied_on)
    except ValueError:
        errors.append("Wybierz poprawną datę sesji.")
    if len(note) > 500:
        errors.append("Notatka może mieć maksymalnie 500 znaków.")
    if errors:
        for error in errors:
            flash(error, "error")
        return redirect(url_for("main.goal_detail", goal_id=goal_id))
    get_db().execute(
        "INSERT INTO study_sessions (goal_id, minutes, note, studied_on) VALUES (?, ?, ?, ?)",
        (goal_id, minutes, note, studied_on),
    )
    get_db().commit()
    flash("Zapisano sesję nauki.", "success")
    return redirect(url_for("main.goal_detail", goal_id=goal["id"]))


@bp.post("/sessions/<int:session_id>/delete")
def delete_session(session_id: int):
    session = get_db().execute(
        """SELECT s.goal_id FROM study_sessions s JOIN goals g ON g.id = s.goal_id
           WHERE s.id = ? AND g.user_id = ?""",
        (session_id, _current_user_id()),
    ).fetchone()
    if session is None:
        abort(404)
    get_db().execute("DELETE FROM study_sessions WHERE id = ?", (session_id,))
    get_db().commit()
    flash("Usunięto sesję.", "success")
    return redirect(url_for("main.goal_detail", goal_id=session["goal_id"]))
