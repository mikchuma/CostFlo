# CostFlo

Aplikacja webowa do śledzenia wydatków, zbudowana w Django. Startuje jako prosty, osobisty tracker, a docelowo zyskuje funkcję grup ze wspólnym rozliczaniem kosztów.



## Funkcje 

- Rejestracja i logowanie użytkowników
- Dodawanie, edycja i usuwanie wydatków (kwota, kategoria, opis, data)
- Pełna izolacja danych między użytkownikami - każdy widzi i edytuje wyłącznie własne wydatki
- Podsumowanie miesięczne oraz suma wydatków w podziale na kategorie
- Zestaw testów automatycznych (pytest) pokrywających kontrolę dostępu i logikę agregacji
- Pełna konteneryzacja: Docker + docker-compose (Django + PostgreSQL)

## Stack technologiczny

- **Backend:** Python, Django
- **Baza danych:** PostgreSQL (Docker), SQLite (fallback lokalny)
- **Testy:** pytest, pytest-django
- **Konteneryzacja:** Docker, docker-compose

## Uruchomienie projektu

Wymagany jest zainstalowany i uruchomiony [Docker Desktop](https://www.docker.com/products/docker-desktop/).

```bash
git clone <adres-repo>
cd CostFlo
docker compose up
```

Migracje bazy danych uruchamiają się automatycznie przy starcie kontenera. Aplikacja będzie dostępna pod adresem:

```
http://localhost:8000/expenses/
```

### Utworzenie konta administratora

```bash
docker compose exec web python manage.py createsuperuser
```

Panel admina: `http://localhost:8000/admin/`

### Zatrzymanie i reset środowiska

```bash
docker compose down       # zatrzymuje kontenery, zachowuje dane
docker compose down -v    # zatrzymuje kontenery i usuwa dane
```

## Testy

```bash
pytest
```

(Wymaga lokalnie skonfigurowanego środowiska Python — patrz `requirements.txt` — lub odpalenia wewnątrz kontenera: `docker compose exec web pytest`.)
