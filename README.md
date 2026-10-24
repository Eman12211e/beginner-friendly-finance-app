# Beginner Friendly Finance App

A beginner-friendly financial education web app (Flask + vanilla JS). Specs live in `docs/`.

## Setup (Windows PowerShell)

```powershell
python -m venv venv
venv\Scripts\python -m pip install -r requirements.txt
copy .env.example .env   # then add your API keys
```

The app starts without `.env` or keys, in demo mode.

## Run

```powershell
venv\Scripts\python app.py      # http://localhost:5000
```

## Tests

```powershell
venv\Scripts\python -m pytest
```

## Scripts

```powershell
venv\Scripts\python scripts\check_endpoints.py   # checks provider endpoints, writes data/endpoint_check.json
venv\Scripts\python scripts\build_demo_data.py   # rebuilds data/demo_stocks.json from yfinance
```
