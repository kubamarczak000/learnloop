# Plan rozwoju LearnLoop

To propozycja pracy rozłożonej na 8 tygodni. Etapy są przyszłym planem nauki, a nie historią rzekomych wcześniejszych prac. Każdy etap można opisać w osobnym issue lub pull requeście na GitHubie.

## Etap 1 — solidne podstawy

- [ ] Poznaj strukturę Flask i fabrykę `create_app`.
- [x] Dodaj automatyczne testy dla podstawowych formularzy i zachowań.
- [ ] Naucz się uruchamiać testy i sprawdzać pokrycie kodu.
- **Tematy:** funkcje, importy, wyjątki, pytest, klient testowy Flask.

## Etap 2 — jakość danych

- [ ] Dodaj migracje bazy danych zamiast ręcznej zmiany `schema.sql`.
- [ ] Dodaj edycję i usuwanie notatek bezpośrednio z historii.
- [ ] Rozważ archiwizację celu zamiast jego trwałego usunięcia.
- **Tematy:** relacyjne bazy danych, migracje, integralność danych.

## Etap 3 — lepszy postęp

- [ ] Pozwól ustawić docelową liczbę minut albo sesji dla celu.
- [ ] Pokaż wykres czasu nauki z ostatnich 7 i 30 dni.
- [x] Dodaj tygodniowy cel minut i informację o jego realizacji.
- **Tematy:** agregowanie danych, daty, dostępność wykresów.

## Etap 4 — wygodniejsze użycie

- [ ] Dodaj paginację historii długich celów.
- [ ] Dodaj sortowanie po terminie, nazwie i ostatniej sesji.
- [ ] Zadbaj o pełną obsługę klawiaturą i komunikaty dla czytników ekranu.
- **Tematy:** UX, semantyczny HTML, dostępność.

## Etap 5 — użytkownicy i prywatność

- [ ] Dodaj rejestrację, logowanie i osobne dane dla każdego konta.
- [ ] Zabezpiecz hasła przez bezpieczne hashowanie, nigdy zwykły tekst.
- [ ] Dodaj eksport i import danych w formacie JSON lub CSV.
- **Tematy:** uwierzytelnianie, autoryzacja, prywatność danych.

## Etap 6 — API

- [ ] Wydziel wersjonowane API JSON dla celów i sesji.
- [ ] Opisz odpowiedzi, błędy i przykładowe żądania.
- [ ] Dodaj mały klient JavaScript albo aplikację mobilną.
- **Tematy:** REST, statusy HTTP, serializacja, OpenAPI.

## Etap 7 — uruchamianie poza komputerem lokalnym

- [ ] Dodaj konfigurację produkcyjną i serwer WSGI.
- [ ] Skonfiguruj Docker oraz trwały wolumen na bazę.
- [ ] Dodaj pipeline CI do sprawdzania formatowania i uruchamiania testów.
- **Tematy:** środowiska, kontenery, CI/CD, sekrety.

## Etap 8 — dopracowane portfolio

- [ ] Dodaj autentyczne zrzuty ekranu i krótki pokaz działania.
- [ ] Uzupełnij README o decyzje projektowe i znane ograniczenia.
- [ ] Poproś kogoś o code review i opisz, czego nauczyła Cię poprawka.
- **Tematy:** GitHub, code review, komunikacja techniczna.

## Proponowane kamienie milowe

1. `v1.0.0` — lokalne cele i sesje.
2. `v1.1.0` — testy i tygodniowy cel nauki (obecna wersja projektu).
3. `v1.2.0` — migracje, ulepszona historia i dostępność.
4. `v2.0.0` — użytkownicy, API i wdrożenie.

Warto opisywać każdą zmianę zgodnie z tym, co naprawdę zostało zrobione: commitami, issue i krótkimi notatkami z nauki.
