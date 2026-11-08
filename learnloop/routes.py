"""Widoki i walidacja formularzy aplikacji."""

from datetime import date
import sqlite3

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from .db import get_db

bp = Blueprint("main", __name__)
STATUSES = {"active", "completed", "paused"}


def _goal_or_404(goal_id: int) -> sqlite3.Row:
    goal = get_db().execute("SELECT * FROM goals WHERE id = ?", (goal_id,)).fetchone()
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

    conditions, parameters = [], []
    if selected_status != "all":
        conditions.append("g.status = ?")
        parameters.append(selected_status)
    if search:
        conditions.append("(g.title LIKE ? OR g.category LIKE ?)")
        parameters.extend((f"%{search}%", f"%{search}%"))
    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
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
           FROM goals"""
    ).fetchone()
    study = connection.execute(
        "SELECT COALESCE(SUM(minutes), 0) AS minutes FROM study_sessions"
    ).fetchone()["minutes"]
    return render_template(
        "index.html",
        goals=goals,
        stats=stats,
        total_minutes=study,
        selected_status=selected_status,
        search=search,
    )


@bp.route("/goals/new", methods=["GET", "POST"])
def new_goal():
    values = {"title": "", "description": "", "category": "Inne", "target_date": ""}
    errors = []
    if request.method == "POST":
        values, errors = _goal_form_values()
        if not errors:
            get_db().execute(
                "INSERT INTO goals (title, description, category, target_date) VALUES (?, ?, ?, ?)",
                (values["title"], values["description"], values["category"], values["target_date"]),
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
        "SELECT goal_id FROM study_sessions WHERE id = ?", (session_id,)
    ).fetchone()
    if session is None:
        abort(404)
    get_db().execute("DELETE FROM study_sessions WHERE id = ?", (session_id,))
    get_db().commit()
    flash("Usunięto sesję.", "success")
    return redirect(url_for("main.goal_detail", goal_id=session["goal_id"]))
