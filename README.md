# LearnLoop

**Polskojęzyczny planer nauki i pracy.** Zapisuj cele i sesje nauki, pilnuj egzaminów w kalendarzu i porządkuj zadania zawodowe.

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**[Otwórz działającą aplikację](https://learnloop-production-bfea.up.railway.app)** · **[Zgłoś błąd](https://github.com/kubamarczak000/learnloop/issues/new?template=bug_report.yml)** · **[Zapoznaj się z planem rozwoju](docs/ROADMAP.md)**

LearnLoop to projekt portfolio zbudowany we Flasku i SQLite. Aplikacja działa w przeglądarce, obsługuje osobne konta użytkowników i jest wdrożona na Railway.

## Funkcje

- Cele nauki z kategorią, terminem i statusem oraz historia sesji z notatkami.
- Statystyki czasu nauki i konfigurowalny tygodniowy cel.
- Kalendarz egzaminów, kolokwiów i innych ważnych dat.
- Generator planu przygotowań: do 30 sesji po 30 minut, w dni robocze przed terminem.
- Planer zadań zawodowych z priorytetem, terminem, szacowanym czasem i statusem.
- Rejestracja, logowanie, ochrona formularzy CSRF i oddzielne dane kont.
- Konto administratora `root` z podglądem kont i danych w aplikacji.

## Uruchomienie lokalne

Wymagany jest Python 3.11 lub nowszy. Na macOS upewnij się, że `python3 --version` wskazuje taką wersję.

```bash
git clone https://github.com/kubamarczak000/learnloop.git
cd learnloop
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
cp .env.example .env
```

Otwórz `.env`, wygeneruj własny `SECRET_KEY` poleceniem `python -c 'import secrets; print(secrets.token_hex(32))'` i wstaw wynik po `SECRET_KEY=`. Następnie uruchom serwer:

```bash
flask --app learnloop:create_app run --debug
```

Otwórz [http://127.0.0.1:5000](http://127.0.0.1:5000) i wybierz **Załóż konto**. Do korzystania z aplikacji wymagane jest konto LearnLoop; nie jest potrzebny zewnętrzny klucz API.

Konto `root` tworzy się z Terminala:

```bash
flask --app learnloop create-root
```

Polecenie poprosi o e-mail i hasło wpisywane bez wyświetlania. Hasło powinno być unikalne. Konto `root` ma dostęp do danych wszystkich użytkowników.

## Wdrożenie na Railway

Repozytorium zawiera konfigurację Railway w `railway.toml`. Wdrożenie używa Gunicorna, a SQLite musi być przechowywane na trwałym wolumenie.

1. Utwórz usługę Railway połączoną z repozytorium `kubamarczak000/learnloop`.
2. Dodaj wolumen do usługi i zamontuj go pod `/data`.
3. Ustaw zmienne `SECRET_KEY` (długi, losowy sekret) oraz `SESSION_COOKIE_SECURE=true`.
4. Wygeneruj domenę publiczną i upewnij się, że wdrożenie działa.
5. Zainstaluj i zaloguj Railway CLI, połącz go z projektem i usługą, a następnie utwórz administratora:

   ```bash
   railway ssh -- .venv/bin/flask --app learnloop:create_app create-root
   ```

   Jeśli Railway CLI nie jest połączone z właściwą usługą, najpierw wybierz projekt, środowisko i usługę poleceniami `railway link` oraz `railway service`.

Ustawień `SECRET_KEY` ani hasła administratora nie zapisuj w repozytorium. Konto `root` widzi dane użytkowników. Przed wdrożeniem na własne potrzeby sprawdź aktualne warunki i koszty [Railway](https://railway.com/pricing).

## Dane i bezpieczeństwo

- Dane są przechowywane w SQLite; lokalnie w `instance/naukaplan.sqlite3`.
- Na Railway ustaw `DATABASE_PATH` na ścieżkę wewnątrz zamontowanego wolumenu, jeśli automatyczna ścieżka `/data` nie jest używana.
- Hasła są przechowywane jako skróty, a widoki planera wymagają zalogowania.
- Konto administratora ma szeroki dostęp do danych i powinno mieć mocne, unikalne hasło.
- Aplikacja nie wysyła e-maili ani powiadomień i nie korzysta z zewnętrznego AI.

## Struktura projektu

```text
learnloop/              Aplikacja Flask, zapytania SQLite, szablony i CSS
tests/                  Testy automatyczne
docs/ROADMAP.md         Aktualny plan nauki i rozwoju projektu
.github/                Szablony zgłoszeń i pull requestów
pyproject.toml          Zależności i ustawienia pakietu
railway.toml            Ustawienia wdrożenia Railway
```

## Testy

Po instalacji zależności deweloperskich uruchom w katalogu projektu:

```bash
python -m pytest
```

Testy używają osobnej, tymczasowej bazy i nie modyfikują danych z lokalnej aplikacji.

## Dalszy rozwój

Otwarte pomysły i kolejność prac są opisane w [roadmapie](docs/ROADMAP.md). Jeśli chcesz zaproponować zmianę, utwórz issue. Przed pull requestem opisz problem, zmianę i sposób jej sprawdzenia.

## Licencja

LearnLoop jest udostępniony na licencji MIT. Szczegóły znajdują się w pliku [LICENSE](LICENSE).
