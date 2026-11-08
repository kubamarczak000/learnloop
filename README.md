# LearnLoop

**LearnLoop** to lokalna aplikacja webowa do układania celów nauki i zapisywania czasu poświęconego na każdy z nich. Zamiast trzymać postanowienia w kilku notatnikach, możesz w jednym miejscu zaplanować temat, ustawić termin, robić krótkie sesje i wracać do własnych notatek.

> Projekt portfolio w Pythonie. Interfejs i instrukcje są po polsku. Aplikacja działa na własnym komputerze, a dane zapisuje w lokalnym pliku SQLite.

## Co potrafi

- Tworzy, edytuje i usuwa cele z opisem, kategorią i opcjonalnym terminem.
- Oznacza cel jako aktywny, wstrzymany lub ukończony.
- Zapisuje sesje nauki: datę, liczbę minut i krótką notatkę.
- Pokazuje podsumowanie czasu, liczbę sesji i statystyki celów.
- Filtruje listę po statusie, a także wyszukuje tytuły i kategorie.
- Chroni formularze tokenem CSRF i waliduje dane po stronie serwera.
- Zachowuje dane po zamknięciu aplikacji w bazie SQLite.

## Zrzuty ekranu

Po uruchomieniu projektu zrób zrzuty widoku przeglądu i szczegółów celu, a następnie dodaj je tutaj, na przykład do katalogu `docs/screenshots/`. Autentyczne zrzuty z działającej aplikacji pomagają rekruterowi szybko zrozumieć projekt.

## Wymagania

- Python 3.11 lub nowszy
- pip
- Przeglądarka internetowa

Nie potrzebujesz konta, zewnętrznej bazy danych ani klucza API. Aplikacja może działać bez połączenia z internetem.

## Uruchomienie lokalne

### macOS / Linux

```bash
git clone https://github.com/TWOJ_LOGIN/learnloop.git
cd learnloop
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
cp .env.example .env
```

Otwórz `.env`, wstaw własny losowy `SECRET_KEY`, a następnie uruchom:

```bash
flask --app learnloop:create_app run --debug
```

Wejdź na [http://127.0.0.1:5000](http://127.0.0.1:5000).

### Windows PowerShell

```powershell
git clone https://github.com/TWOJ_LOGIN/learnloop.git
cd learnloop
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
Copy-Item .env.example .env
```

Uzupełnij własny `SECRET_KEY` w `.env`, potem uruchom:

```powershell
flask --app learnloop:create_app run --debug
```

Serwer deweloperski Flask jest przeznaczony do lokalnej pracy i nauki. Nie wystawiaj go bezpośrednio do publicznego internetu.

## Uruchamianie testów

Testy korzystają z osobnej, tymczasowej bazy danych, więc nie zmieniają Twoich celów w `instance/naukaplan.sqlite3`. Po instalacji zależności deweloperskich uruchom w katalogu projektu:

```bash
python -m pytest
```

Każdy zielony `.` oznacza zaliczony test. Jeśli pojawi się błąd, pytest pokaże nazwę testu i szczegóły, które pomogą znaleźć przyczynę.

## Gdzie są dane?

Przy pierwszym uruchomieniu aplikacja utworzy katalog `instance/` i plik `naukaplan.sqlite3` (nazwa pliku bazy pozostaje taka sama, by zachować istniejące dane po zmianie nazwy aplikacji). Ten katalog jest celowo pomijany przez Git, więc Twoje lokalne cele nie trafią przez pomyłkę do repozytorium. Możesz wskazać inny plik, ustawiając `DATABASE_PATH` w `.env`.

## Jak to jest zbudowane

```text
learnloop/
├── __init__.py       # fabryka Flask, konfiguracja i rejestracja komponentów
├── db.py             # połączenie SQLite i inicjalizacja schematu
├── routes.py         # adresy URL, zapisy i walidacja formularzy
├── schema.sql        # tabele, ograniczenia i indeksy
├── templates/        # widoki Jinja/HTML
└── static/style.css  # responsywny interfejs
```

Przeglądarka wysyła żądanie do widoku Flask. Widok sprawdza dane, korzysta z SQLite przez `db.py`, a potem zwraca szablon HTML. Każde zapytanie SQL używa parametrów zamiast doklejania wartości użytkownika do tekstu zapytania. Połączenie jest zamykane po zakończeniu żądania. Schemat tworzy się przy starcie przez `CREATE TABLE IF NOT EXISTS`.

## Model danych

- **Cel (`goals`)** ma tytuł, opis, kategorię, opcjonalny termin, status i datę utworzenia.
- **Sesja (`study_sessions`)** należy do jednego celu i przechowuje minuty, datę oraz notatkę.
- Usunięcie celu usuwa jego sesje dzięki relacji `ON DELETE CASCADE`.

## Jak uczyć się na tym projekcie

Możesz przejść repozytorium od prostszych pojęć do bardziej zaawansowanych:

1. Przeczytaj `learnloop/routes.py` i prześledź drogę formularza od URL do zapisu w bazie.
2. Zmień pole celu (np. dodaj „poziom trudności”) w formularzu, walidacji i schemacie.
3. Przejrzyj zapytania z `JOIN`, agregatami `SUM` i `COUNT` w widoku przeglądu.
4. Zobacz, jak szablony Jinja dziedziczą wspólny układ z `base.html`.
5. Dodaj własną funkcję, opisz ją w README i umieść na osobnym branchu Git.

Przed większymi zmianami zrób commit. Jeśli przypadkowo usuniesz lokalną bazę, SQLite utworzy pustą przy kolejnym uruchomieniu — dlatego przed eksperymentami skopiuj plik `instance/naukaplan.sqlite3`.

## Rozwój projektu

Aktualna wersja to kompletna baza do samodzielnego rozwoju. Propozycje kolejnych etapów wraz z tematami do nauki są w [docs/ROADMAP.md](docs/ROADMAP.md). Taki plan pozwala rozwijać projekt przez kolejne tygodnie i miesiące bez przypisywania mu fikcyjnej historii.

## Licencja

Projekt udostępniony na licencji MIT — szczegóły w pliku [LICENSE](LICENSE).
