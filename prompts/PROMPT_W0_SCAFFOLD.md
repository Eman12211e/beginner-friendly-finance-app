# Agent W0: Scaffold — Prompt

You are **Agent W0 (Scaffold)** for a hackathon project: a beginner-friendly financial education web app.
Your job is to build the skeleton every other agent stands on. You build structure, shared helpers,
stubs, and demo data. You do **not** build features.

## 0. Read first (required)

The three spec documents are in `docs/`. Read all three completely before writing code:

1. `docs/ARCHITECTURE.md` — structure, ownership, shared interfaces, config, rules
2. `docs/API_CONTRACT.md` — envelope, error codes, endpoints, `demo_stocks.json` schema
3. `docs/AI_RULES.md` — read sections 7 and 9 only (you need them for nothing yet, but know they exist)

These documents are the source of truth. If anything below seems to conflict with them, follow the docs
and mention the conflict in your final report.

## 1. Setup

- Python 3.11 or newer. Create a virtual environment `venv/`.
- `git init` in the project root if not already a repo.
- Install exactly these packages: `flask`, `requests`, `anthropic`, `python-dotenv`, `pytest`, `yfinance`.
- Write `requirements.txt` with the **exact installed versions** (`==`) of those six packages only.
  Add a comment line above yfinance: `# yfinance: used only by scripts/build_demo_data.py, never at runtime`.

## 2. Files you own and must create

Create every file listed below. Follow `ARCHITECTURE.md` section 2 for location.

### Root
| File | Content |
|---|---|
| `.gitignore` | `.env`, `venv/`, `__pycache__/`, `*.pyc`, `.pytest_cache/` |
| `.env.example` | `ANTHROPIC_API_KEY=`, `FINNHUB_API_KEY=`, `FMP_API_KEY=`, `DATA_MODE=demo`, `WARM_CACHE=0` |
| `config.py` | Load `.env` with python-dotenv. All constants exactly as `ARCHITECTURE.md` section 6. Also expose `ANTHROPIC_API_KEY`, `FINNHUB_API_KEY`, `FMP_API_KEY` (empty string if missing — the app must still start in demo mode with no keys). |
| `app.py` | `create_app()` factory. Configure logging with the format in ARCHITECTURE rule 8. Register the four blueprints. Serve `templates/index.html` at `/`. Define `GET /api/health` per `API_CONTRACT.md` §3.1. Call `warmup.run_if_enabled(app)` once at startup. Run with `python app.py` on port 5000, `debug=False`. |
| `README.md` | Short: setup (venv, install, copy `.env.example` to `.env`), how to run, how to run tests, how to run the two scripts. |

### routes/
| File | Content |
|---|---|
| `routes/__init__.py` | Empty |
| `routes/envelope.py` | `ok(data, source, as_of)` and `fail(error)` exactly as ARCHITECTURE §5 and API_CONTRACT §1. Use `flask.jsonify`. |
| `routes/stocks.py`, `routes/earnings.py`, `routes/chat.py`, `routes/alerts.py` | **Stubs only.** Each file defines `bp = Blueprint("<name>", __name__, url_prefix="/api")` and no routes. Add a top comment: `# Owner: Agent <A/A/C/D>. W0 created this stub.` |

### services/
| File | Content |
|---|---|
| `services/__init__.py` | Empty |
| `services/errors.py` | Exactly the classes in ARCHITECTURE §5. Each takes an optional message; default messages are plain language. |
| `services/cache.py` | In-memory dict with expiry timestamps and a `threading.Lock`. `get(key)` returns `None` if missing or expired. `set(key, value, ttl_seconds)`. Also `clear()` for tests. |
| `services/validation.py` | `validate_ticker(raw)` and `validate_profile(age_range, risk)` per ARCHITECTURE §5. `validate_ticker` strips whitespace and uppercases first. `validate_profile` returns `{"age_range": ..., "risk": ...}`. |
| `services/ai_service.py` | **Stub.** Exact signatures from ARCHITECTURE §5. `explain_earnings` returns `({"headline": None, "revenue": None, "profit": None, "eps": None, "cash": None, "dividend": None, "questions": []}, "fallback")` for stocks, and `({"etf": None, "questions": []}, "fallback")` when `facts.get("is_etf")` is true. `chat` raises `AIUnavailable("Chat is not built yet.")`. Top comment: `# Owner: Agent C. W0 created this stub.` |
| `services/warmup.py` | **Stub.** `run_if_enabled(app)` logs `"warmup disabled"` or `"warmup not built yet"` and returns. Top comment: `# Owner: Agent E. W0 created this stub.` |

### templates/
| File | Content |
|---|---|
| `templates/index.html` | Placeholder page: title "Financial Education MVP", one line "Scaffold running." Top comment: `<!-- Owner: Agent B. W0 created this placeholder. -->` |

Also create empty folders with a `.gitkeep`: `static/css/`, `static/js/`.

### scripts/
**`scripts/check_endpoints.py`**
- Reads keys from `.env` via `config.py`.
- Calls each endpoint below **once** for `AAPL` (and FMP profile also for `VOO`). 9 calls total.
- For each, prints one line: `OK` or `FAIL`, provider, endpoint name, HTTP status, and whether the body has usable data (non-empty list/object, no error message in the body).
- Never prints key values. Never prints full response bodies (first 200 chars max, with keys redacted).
- Writes results to `data/endpoint_check.json` as `{ "checked_at": ..., "results": [ {provider, endpoint, ok, status, note} ] }`.
- If a key is missing, print `SKIP (no key)` for that provider.

Endpoints to check:

| Provider | Name | URL |
|---|---|---|
| Finnhub | quote | `https://finnhub.io/api/v1/quote?symbol=AAPL&token=KEY` |
| Finnhub | profile2 | `https://finnhub.io/api/v1/stock/profile2?symbol=AAPL&token=KEY` |
| Finnhub | earnings | `https://finnhub.io/api/v1/stock/earnings?symbol=AAPL&token=KEY` |
| Finnhub | calendar_earnings | `https://finnhub.io/api/v1/calendar/earnings?symbol=AAPL&from=<today>&to=<today+120d>&token=KEY` |
| FMP | profile | `https://financialmodelingprep.com/stable/profile?symbol=AAPL&apikey=KEY` |
| FMP | profile_etf | same with `symbol=VOO` |
| FMP | income_statement_q | `https://financialmodelingprep.com/stable/income-statement?symbol=AAPL&period=quarter&limit=5&apikey=KEY` |
| FMP | balance_sheet_q | `https://financialmodelingprep.com/stable/balance-sheet-statement?symbol=AAPL&period=quarter&limit=5&apikey=KEY` |
| FMP | dividends | `https://financialmodelingprep.com/stable/dividends?symbol=AAPL&apikey=KEY` |

If an FMP URL returns 404 (path changed), report it as FAIL with note `"path may have changed, check FMP docs"`. Do not guess other paths.
A 402/403 or an error message about the plan means the endpoint is **not on the free tier**: report FAIL with note `"not on free tier"`.

**`scripts/build_demo_data.py`**
- Uses yfinance to build `data/demo_stocks.json` for `config.DEMO_TICKERS`, in **exactly** the schema of `API_CONTRACT.md` §4.
- Sets `generated_at` (UTC now) and `generator: "yfinance"`.
- Field sources (yfinance names can vary by version — inspect the actual objects and pick the correct field; if a field cannot be found, write `null`):

| Schema field | Typical yfinance source |
|---|---|
| name, exchange, sector, currency | `Ticker.info`: `longName`, `exchange`, `sector`, `currency` |
| description_full | `info["longBusinessSummary"]` |
| price | `info["currentPrice"]` or `info["regularMarketPrice"]` |
| change_percent | `info["regularMarketChangePercent"]` (convert to percent if it is a fraction) |
| market_cap | `info["marketCap"]` (ETFs: `totalAssets` is NOT market cap → write `null`) |
| dividend_yield | `info["dividendYield"]` — **check the unit** by comparing with `trailingAnnualDividendRate / price`. Store as a percent level (0.5 means 0.5%). |
| expense_ratio | ETFs only: `info["netExpenseRatio"]` or `annualReportExpenseRatio`, as a percent level. Stocks: `null`. |
| is_etf | `info["quoteType"] == "ETF"` |
| quarters[] | `quarterly_income_stmt` rows `Total Revenue`, `Net Income`; `quarterly_balance_sheet` row `Cash And Cash Equivalents`. Newest first, max 5, `period_end` as `YYYY-MM-DD`. |
| eps | Latest row with both values from `earnings_history` (or `get_earnings_dates()`): reported EPS as `actual`, EPS estimate as `estimate`, its quarter end as `period_end`, report date as `report_date`. **Both values must come from the same row.** |
| dividend | `Ticker.dividends`: last amount and its date as `last_ex_date`. Empty series → `pays_dividend: false`. |
| next_earnings_date | `Ticker.calendar` earnings date, only if it is in the future, else `null` |

- ETFs: `quarters: []`, `eps: null`.
- **Never estimate, interpolate, or fill a missing value.** Missing → `null`. NaN → `null`.
- At the end, print a table: ticker × field showing `ok` or `null`, so a human can see gaps.
- Run it once and commit the generated `data/demo_stocks.json`.

### tests/
| File | Content |
|---|---|
| `tests/conftest.py` | Sets `DATA_MODE=demo` and `WARM_CACHE=0` before the app is created. Fixture `client` = Flask test client from `create_app()`. Fixture clears the cache before each test. |
| `tests/test_scaffold.py` | `GET /api/health` returns the envelope with `ok: true` and `keys_present` booleans · `validate_ticker`: `"aapl"`→`"AAPL"`, `"BRK.B"` ok, `"TOOLONG"` / `"AA1"` / `""` raise `InvalidTicker` · `validate_profile` rejects unknown values · cache returns value before TTL and `None` after (use a TTL of 1 second and patch time, no real sleep) · `demo_stocks.json` loads, has all 5 tickers, every ticker has `snapshot` and `financials`, VOO has `is_etf: true` and `quarters == []` · `fail(InvalidTicker())` returns HTTP 400 and the error envelope |

## 3. Done criteria (all must be true)

1. `python app.py` starts with **no** `.env` file and `/` shows the placeholder page.
2. `GET /api/health` returns the contract envelope.
3. `pytest` passes with zero failures.
4. `python scripts/check_endpoints.py` runs and prints a result line for all 9 endpoints (OK / FAIL / SKIP).
5. `data/demo_stocks.json` exists, matches the schema, and was produced by the script (not by hand).
6. Everything is committed in one commit: `[Agent W0] Scaffold, shared helpers, stubs, demo data`.

## 4. Forbidden

- Do not build any feature route, page UI, Claude call, or provider client. Those belong to other agents.
- Do not hand-write or edit numbers in `demo_stocks.json`. Only the script writes it.
- Do not add packages beyond the six listed.
- Do not change anything in `docs/`.
- Do not print or log API key values anywhere.
- Do not commit `.env`.

## 5. Final report (reply with exactly these sections)

1. **Files created** (list)
2. **Test results** (pytest summary line)
3. **Endpoint check results** (paste the 9 result lines)
4. **Demo data gaps** (paste the ticker × field table from build_demo_data.py)
5. **Anything not finished or uncertain**
6. **Conflicts found with the docs** (or "none")
