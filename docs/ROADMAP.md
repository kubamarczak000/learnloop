# Plan rozwoju LearnLoop

Roadmapa opisuje obecny stan projektu i możliwe następne kroki. To plan, nie lista funkcji, które już istnieją. Kolejność może się zmieniać; aktualne zadania można śledzić w [GitHub Issues](https://github.com/kubamarczak000/learnloop/issues).

## Obecnie dostępne

- Cele nauki, sesje, statystyki i tygodniowy cel czasu.
- Kalendarz wydarzeń z generowaniem planu nauki.
- Planer zadań zawodowych.
- Rejestracja, logowanie, role użytkowników i panel administratora.
- Podstawowy zestaw testów automatycznych.
- Wdrożenie na Railway z SQLite i trwałym wolumenem.

## Następne kroki

- [ ] Rozszerzyć testy o rejestrację, logowanie, izolację danych kont i uprawnienia administratora.
- [ ] Dodać eksport danych użytkownika do JSON lub CSV.
- [ ] Dodać edycję i archiwizację celów oraz edycję notatek z sesji.
- [ ] Wprowadzić migracje bazy, aby bezpiecznie zmieniać schemat przy kolejnych wersjach.
- [ ] Ułatwić pracę z długimi listami przez sortowanie i paginację.

## Dalsze pomysły

- Reset hasła i e-mailowe przypomnienia. Wymagają konfiguracji dostawcy poczty oraz bezpiecznego przechowywania jego sekretów.
- Opcjonalne sugestie AI do planu nauki, z możliwością działania aplikacji bez tej integracji.
- Wersjonowane API JSON i opis OpenAPI.
- Wykres aktywności z ostatnich 7 i 30 dni oraz bardziej elastyczna dostępność sesji.
- Dalsza poprawa dostępności, w tym obsługa klawiaturą i czytnikami ekranu.

## Co można poćwiczyć

1. Prześledź formularz od szablonu HTML do widoku Flask i zapytania SQLite.
2. Wybierz małe zadanie z roadmapy i otwórz dla niego issue.
3. Utwórz osobny branch, opisz zmianę w commitach i dodaj lub popraw test.
4. Uzupełnij README, jeśli zmieni się sposób uruchomienia albo zachowanie aplikacji.
5. W pull requeście opisz, czego się nauczyłeś i jak sprawdziłeś zmianę.

## Znane ograniczenia

- Aplikacja nie wysyła obecnie e-maili, nie resetuje haseł i nie integruje się z AI.
- Plan nauki przed wydarzeniem jest prostą regułą opartą na sesjach po 30 minut w dni robocze, a nie spersonalizowanym algorytmem.
- SQLite na hostingu wymaga trwałego wolumenu. Bez niego baza może zniknąć przy ponownym wdrożeniu.
- Panel `root` może przeglądać dane wszystkich kont; należy ograniczyć dostęp do tego konta.
