"""Testy najważniejszych zachowań LearnLoop."""

from datetime import date, timedelta

import pytest

from learnloop import create_app


@pytest.fixture
def app(tmp_path):
    """Każdy test dostaje osobną, tymczasową bazę danych."""
    return create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret-key",
            "DATABASE_PATH": str(tmp_path / "test.sqlite3"),
            "WTF_CSRF_ENABLED": False,
        }
    )


@pytest.fixture
def client(app):
    test_client = app.test_client()
    test_client.post(
        "/register",
        data={"email": "owner@example.test", "password": "bezpieczne-haslo-123"},
    )
    return test_client


@pytest.fixture
def anonymous_client(app):
    return app.test_client()


def add_goal(client, title="Nauka Pythona"):
    return client.post(
        "/goals/new",
        data={
            "title": title,
            "description": "Ćwiczę podstawy",
            "category": "Programowanie",
            "target_date": "",
        },
        follow_redirects=True,
    )


def test_home_page_loads(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "Twoje cele" in response.get_data(as_text=True)


def test_user_can_create_and_find_goal(client):
    response = add_goal(client)

    assert response.status_code == 200
    assert "Nauka Pythona" in response.get_data(as_text=True)

    search_response = client.get("/?q=Python")
    assert "Nauka Pythona" in search_response.get_data(as_text=True)


def test_goal_requires_a_title(client):
    response = client.post(
        "/goals/new",
        data={"title": "", "description": "", "category": "Inne", "target_date": ""},
    )

    assert response.status_code == 200
    assert "Podaj nazwę celu." in response.get_data(as_text=True)


def test_user_can_add_study_session(client):
    add_goal(client)
    home = client.get("/").get_data(as_text=True)
    # Link do szczegółów wskazuje ID celu utworzonego powyżej.
    assert "/goals/1" in home

    response = client.post(
        "/goals/1/sessions",
        data={"minutes": "25", "studied_on": "2026-11-08", "note": "Zmienne i typy"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert "25 min nauki" in page
    assert "Zmienne i typy" in page


def test_weekly_goal_can_be_changed_and_tracks_this_week(client):
    add_goal(client)
    client.post(
        "/goals/1/sessions",
        data={"minutes": "25", "studied_on": date.today().isoformat(), "note": "Powtórka"},
    )

    response = client.post(
        "/settings/weekly-goal",
        data={"weekly_goal_minutes": "60"},
        follow_redirects=True,
    )

    page = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "25 min z 1 h 0 min" in page
    assert "42% celu" in page


def test_weekly_goal_rejects_values_below_minimum(client):
    response = client.post(
        "/settings/weekly-goal",
        data={"weekly_goal_minutes": "0"},
        follow_redirects=True,
    )

    assert "Tygodniowy cel musi wynosić od 15 do 10 080 minut." in response.get_data(as_text=True)


def test_calendar_event_can_generate_weekday_study_plan(client):
    event_date = date.today() + timedelta(days=7)
    response = client.post(
        "/calendar/events",
        data={
            "title": "Kolokwium z biologii",
            "event_date": event_date.isoformat(),
            "event_type": "colloquium",
            "goal_id": "",
            "notes": "Rozdziały 1–3",
        },
        follow_redirects=True,
    )
    assert "Kolokwium z biologii" in response.get_data(as_text=True)

    response = client.post("/calendar/events/1/plan", follow_redirects=True)
    page = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Ułożono plan:" in page
    assert "sesji po 30 min" in page
    assert "Przygotowanie: Kolokwium z biologii" in page


def test_calendar_rejects_past_events(client):
    yesterday = date.today() - timedelta(days=1)
    response = client.post(
        "/calendar/events",
        data={"title": "Minione kolokwium", "event_date": yesterday.isoformat(), "event_type": "exam"},
        follow_redirects=True,
    )

    assert "Wybierz dzisiejszą lub przyszłą datę." in response.get_data(as_text=True)
    assert "Minione kolokwium" not in response.get_data(as_text=True)


def test_work_task_can_be_added_and_started(client):
    response = client.post(
        "/tasks",
        data={
            "title": "Przygotować raport",
            "description": "Podsumować wyniki tygodnia",
            "due_date": date.today().isoformat(),
            "priority": "high",
            "estimate_minutes": "45",
        },
        follow_redirects=True,
    )
    page = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Przygotować raport" in page
    assert "Wysoki" in page

    response = client.post(
        "/tasks/1/status", data={"status": "in_progress"}, follow_redirects=True
    )
    assert "W trakcie" in response.get_data(as_text=True)


def test_work_task_due_date_appears_in_calendar(client):
    due_date = date.today() + timedelta(days=3)
    client.post(
        "/tasks",
        data={"title": "Wysłać ofertę", "due_date": due_date.isoformat()},
    )

    response = client.get(f"/calendar?year={due_date.year}&month={due_date.month}")

    assert "Wysłać ofertę" in response.get_data(as_text=True)

