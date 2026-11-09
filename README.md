# LearnLoop

**LearnLoop** to lokalny planer nauki i pracy. Pozwala organizować cele nauki, zapisywać sesje, śledzić egzaminy oraz prowadzić listę zadań zawodowych w jednym miejscu.

> Projekt portfolio w Pythonie. Interfejs i instrukcje są po polsku. LearnLoop można uruchomić lokalnie albo wdrożyć na Railway; w obu przypadkach używa bazy SQLite.

Repozytorium: [github.com/kubamarczak000/learnloop](https://github.com/kubamarczak000/learnloop)

## Co potrafi

- Tworzy, edytuje i usuwa cele z opisem, kategorią i opcjonalnym terminem.
- Oznacza cel jako aktywny, wstrzymany lub ukończony.
- Zapisuje sesje nauki: datę, liczbę minut i krótką notatkę.
- Pokazuje podsumowanie czasu, liczbę sesji i statystyki celów.
- Śledzi tygodniowy cel nauki, domyślnie 3 godziny od poniedziałku do niedzieli; cel można zmienić.
- Wyświetla miesięczny kalendarz egzaminów, kolokwiów i innych ważnych terminów.
- Układa przed wydarzeniem plan maksymalnie 30 sesji trwających po 30 minut, na dni robocze w okresie do sześciu tygodni przed terminem.
- Prowadzi osobny planer pracy z priorytetami, terminami, szacowanym czasem i statusami zadań.
- Pokazuje terminy zadań zawodowych bezpośrednio w kalendarzu.
- Udostępnia rejestrację i logowanie; cele, zadania, wydarzenia i ustawienia są przypisane do konta.
- Udostępnia osobne konto `root` z panelem administracyjnym i podglądem danych wszystkich kont.
- Filtruje listę po statusie, a także wyszukuje tytuły i kategorie.
- Chroni formularze tokenem CSRF i waliduje dane po stronie serwera.
- Zachowuje dane po zamknięciu aplikacji w bazie SQLite.

## Wymagania

- Python 3.11 lub nowszy
- pip
- Przeglądarka internetowa

Nie potrzebujesz konta, zewnętrznej bazy danych ani klucza API. Aplikacja może działać bez połączenia z internetem.

## Uruchomienie lokalne

### macOS

```bash
git clone https://github.com/kubamarczak000/learnloop.git
cd learnloop
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
cp .env.example .env
```

Wygeneruj klucz poleceniem `python -c 'import secrets; print(secrets.token_hex(32))'`, otwórz `.env` i wstaw go po `SECRET_KEY=`. Następnie uruchom:

```bash
flask --app learnloop:create_app run --debug
```

Wejdź na [http://127.0.0.1:5000](http://127.0.0.1:5000).

Przy pierwszym uruchomieniu wybierz **Załóż konto**. Konto `root` tworzy administrator z Terminala:

```bash
flask --app learnloop create-root
```

Polecenie poprosi o e-mail i dwukrotne, niewidoczne wpisanie hasła. Hasło zostanie zapisane jako skrót w bazie, nie w pliku projektu. Jeśli podany e-mail należy już do zwykłego konta, polecenie zmieni je na `root` i ustawi nowe hasło. Z jednego e-maila może korzystać tylko jedno konto `root` w bazie. Z panelu root można przejść do własnego planera i wrócić do panelu przyciskiem w menu.

### Windows PowerShell

```powershell
git clone https://github.com/kubamarczak000/learnloop.git
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

## Wdrożenie na Railway

Konfiguracja wdrożeniowa znajduje się w `railway.toml`. Usługa uruchamia aplikację przez Gunicorn. Bazę SQLite należy przechowywać na trwałym wolumenie Railway, aby dane przetrwały ponowne uruchomienie i nowe wdrożenie.

1. Zaloguj się w [Railway](https://railway.com/) i utwórz projekt wdrażany z repozytorium GitHub `kubamarczak000/learnloop`.
2. W ustawieniach usługi dodaj wolumen i ustaw ścieżkę montowania `/data`.
3. W zakładce zmiennych usługi ustaw `SECRET_KEY` na długi, losowy i prywatny ciąg znaków oraz `SESSION_COOKIE_SECURE=true`. Nie dodawaj tych wartości do repozytorium.
4. Wygeneruj domenę publiczną dopiero po ustawieniu wolumenu, sekretu i konta root.
5. Po wdrożeniu utwórz konto administratora z Terminala. Zainstaluj Railway CLI z oficjalnej instrukcji, zaloguj je do właściwego konta i połącz z projektem. Następnie uruchom polecenie w kontekście usługi:

   ```bash
   railway ssh -- flask --app learnloop:create_app create-root
   ```

   Terminal poprosi o e-mail i hasło. Hasło nie jest wyświetlane podczas wpisywania. Zapisz je w menedżerze haseł. Konto root daje podgląd danych użytkowników, więc użyj unikalnego hasła i nie udostępniaj go.

6. Otwórz wygenerowany adres Railway, załóż zwykłe konto i sprawdź logowanie, planer, kalendarz oraz zadania.

Railway Hobby ma minimalną opłatę 5 USD miesięcznie i obejmuje 5 USD kredytów na zużycie zasobów; koszt może wzrosnąć po ich przekroczeniu. Sprawdź aktualny cennik przed aktywowaniem usługi. Szczegóły znajdują się w [cenniku Railway](https://docs.railway.com/pricing/plans), [dokumentacji wolumenów](https://docs.railway.com/volumes/reference) i [instrukcji Railway SSH](https://docs.railway.com/cli/ssh).

**Ważne:** nie uruchamiaj aplikacji publicznie bez trwałego wolumenu i własnego `SECRET_KEY`. Zmiana lub brak wolumenu może spowodować utratę bazy, a domyślny klucz deweloperski nie nadaje się do hostingu.

## Uruchamianie testów

Testy korzystają z osobnej, tymczasowej bazy danych, więc nie zmieniają lokalnych celów. Po instalacji zależności deweloperskich uruchom w katalogu projektu:

```bash
python -m pytest
```

Zestaw zawiera dziesięć testów sprawdzających cele, sesje nauki, tygodniowy cel, kalendarz, generator planu i zadania zawodowe. Testy korzystają z osobnego konta w tymczasowej bazie.

Przy pierwszej rejestracji istniejące dane z lokalnej bazy zostaną przypisane do tego konta. Każde kolejne konto zaczyna z własnym, pustym planerem.

## Gdzie są dane?

Przy pierwszym uruchomieniu aplikacja utworzy katalog `instance/` i plik `naukaplan.sqlite3`. Katalog jest pomijany przez Git, więc prywatne cele i sesje pozostają na Twoim komputerze. Możesz wskazać inny plik, ustawiając `DATABASE_PATH` w `.env`.

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
- **Ustawienie (`app_settings`)** przechowuje tygodniowy cel czasu nauki. Postęp jest liczony dla bieżącego tygodnia, od poniedziałku do niedzieli.
- **Wydarzenie (`calendar_events`)** zapisuje egzamin, kolokwium lub inny termin i może być połączone z celem nauki.
- **Planowana sesja (`planned_sessions`)** przechowuje sesję wygenerowaną dla wydarzenia. Generator tworzy maksymalnie 30 sesji po 30 minut na dni robocze w okresie do sześciu tygodni przed wydarzeniem.
- **Zadanie pracy (`work_tasks`)** przechowuje opis, termin, priorytet, status i szacowany czas. Zadania z terminem pojawiają się również w widoku kalendarza.
- **Konto (`users`)** przechowuje adres e-mail i skrót hasła. Każde konto widzi wyłącznie własne dane; hasła nie są zapisywane w zwykłym tekście. Dostęp do widoków planera wymaga zalogowania.
- **Konto root** ma osobną rolę i może przeglądać użytkowników, cele, zadania, wydarzenia oraz sesje ze wszystkich kont. Zwykłe konta nie mają dostępu do panelu administratora.
- Usunięcie celu usuwa jego sesje dzięki relacji `ON DELETE CASCADE`.

## Jak uczyć się na tym projekcie

Kod pozwala ćwiczyć kolejne zagadnienia Pythona i tworzenia aplikacji webowych:

1. Przeczytaj `learnloop/routes.py` i prześledź drogę formularza od URL do zapisu w bazie.
2. Zmień pole celu (np. dodaj „poziom trudności”) w formularzu, walidacji i schemacie.
3. Przejrzyj zapytania z `JOIN`, agregatami `SUM` i `COUNT` w widoku przeglądu.
4. Zobacz, jak szablony Jinja dziedziczą wspólny układ z `base.html`.
5. Sprawdź testy w `tests/test_app.py` i rozbuduj je, gdy dodasz nową funkcję.

Przed większymi zmianami zrób commit. Jeśli przypadkowo usuniesz lokalną bazę, SQLite utworzy pustą przy kolejnym uruchomieniu — dlatego przed eksperymentami skopiuj plik `instance/naukaplan.sqlite3`.

## Rozwój projektu

Aktualna wersja zawiera cele, sesje nauki, wyszukiwanie, statystyki oraz podstawowy zestaw testów. Kolejne pomysły na rozwój i zagadnienia do nauki opisuje [docs/ROADMAP.md](docs/ROADMAP.md).

## Licencja

Projekt udostępniony na licencji MIT — szczegóły w pliku [LICENSE](LICENSE).
