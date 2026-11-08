"""Testy najważniejszych zachowań LearnLoop."""

from datetime import date

import pytest

from learnloop import create_app


@pytest.fixture
def client(tmp_path):
    """Każdy test dostaje osobną, tymczasową bazę danych."""
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret-key",
            "DATABASE_PATH": str(tmp_path / "test.sqlite3"),
            "WTF_CSRF_ENABLED": False,
        }
    )
    with app.test_client() as test_client:
        yield test_client


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

