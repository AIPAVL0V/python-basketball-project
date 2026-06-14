# Прогресс проекта

## Сделано

- **`api.py`** — FastAPI-сервер с эндпоинтом `GET /team?name=...` (поиск по аббревиатуре или названию)
- **`app.py`** — главная страница Streamlit (описание проекта, навигация)
- **`pages/2_Hypothesis_2.py`** — Гипотеза 2 (3PT% vs Win%): корреляция Pearson/Spearman, scatter plot, trend chart
- **`pages/3_Player_Search.py`** — заглушка «in progress»
- **`pages/4_Team_Search.py`** — поиск команды через FastAPI, адаптивный вывод метрик
- **`data/app/team_season_stats.csv`** — агрегат по командам за сезон (1 194 строки)
- **`data/app/team_stats.csv`** — агрегат по командам за всю историю (45 строк)
- **`requirements.txt`** — добавлены streamlit, fastapi, uvicorn, requests
- **`notebooks/hypothesis_3pt-wins.ipynb`** — ячейки экспорта CSV в `data/app/`
- **`README.md`** — секция «How to run», обновлённая структура проекта

## Осталось сделать

- **`pages/1_Hypothesis_1.py`** — перенести файл в `pages/`
- **`data/app/player_stats.csv`** — запустить соответствующий ноутбук, чтобы файл появился (Hypothesis 1 зависит от него)
- **`pages/3_Player_Search.py`** — реализовать поиск игрока вместе с эндпоинтом `/player`
- **`api.py`** — добавить эндпоинт `GET /player?name=...` (зависит от наличия player_stats.csv)
- **`reports/final_report.md`** — итоговый отчёт по проекту
