# Agent E: Live Data — Prompt

You are **Agent E (Live Data)** for a beginner financial education web app.
The app works end to end on demo data. Your job: **switch on real data from Finnhub and FMP safely**,
prove that every failure falls back cleanly, and make the demo fast with a pre-warmed cache.

Agent D works **in parallel** with you on alerts and the checklist. You never edit D's files.

## 0. Read first (required)

1. `docs/ARCHITECTURE.md` — all of it, especially §4 (fallback order, TTLs) and §7 (decisions 2, 4, 7).
2. `docs/API_CONTRACT.md` — §1, §2, §3.2, §3.3, **§4 (internal shape + live mapping table)**.
3. `docs/INTEGRATION_NOTES.md` — what changed during integration.
4. Agent A's code: `finnhub_client.py`, `fmp_client.py`, `market_data.py`, `earnings_service.py`, `formatting.py`.
5. `data/endpoint_check.json`.

## 1. Files you own

`services/finnhub_client.py`, `services/fmp_client.py`, `services/market_data.py` (ownership moved from A to you),
`services/warmup.py` (replace W0 stub body, keep the signature), `tests/test_live_fallback.py`.

You may **run** (not edit) `scripts/check_endpoints.py`.

## 2. Tasks, in this order

### 2.1 Re-check endpoints
Run `python scripts/check_endpoints.py`. Compare with the committed `data/endpoint_check.json`.
Any endpoint marked FAIL must not be called at runtime. Its fields are `null` in live mode.

### 2.2 Verify live data, field by field
Set `DATA_MODE=live`, `WARM_CACHE=0`, restart. For each of the 5 demo tickers, `curl` the snapshot and earnings endpoints.
Then compare the live response against the demo response for the same ticker:

| Field | Sanity rule | If it fails |
|---|---|---|
| `market_cap` | Live ÷ demo between 0.5 and 2 | Almost always a **unit bug** (Finnhub `marketCapitalization` is in **millions**). Fix the conversion. |
| `price` | Live ÷ demo between 0.5 and 2 | Wrong field mapped |
| `revenue`, `net_income` (same `period_end` in both) | Within 1% | Wrong field or wrong statement |
| `eps.actual`, `eps.estimate` | Both from the **same** Finnhub record | Fix the record selection. Never mix providers. |
| `dividend_yield`, `expense_ratio` | Percent level (0.5 means 0.5%) | Unit conversion |
| `change_percent` | Percent, not fraction | Unit conversion |

**Never "fix" a mismatch by adjusting or substituting a number.** Find the field or unit bug.
If a live field has no reliable provider field on the free tier, it is `null` in live mode. **Do not fill it from demo data.**
A response tagged `source: "live"` must contain live values only.

Write each finding in your report: ticker, field, live value, demo value, verdict.

### 2.2b Dividend yield in live mode
Call Finnhub `https://finnhub.io/api/v1/stock/metric?symbol=KO&metric=all&token=KEY` once. If it returns `metric.dividendYieldIndicatedAnnual` on the free tier, add `get_metrics(t)` to `finnhub_client.py` and map it to `dividend_yield` (verify the unit: it must be a percent level, 3.1 means 3.1%). If the endpoint is not free, `dividend_yield` is `null` in live mode; report it. `expense_ratio` is always `null` in live mode (API_CONTRACT §4).

### 2.3 Prove the fallbacks — `tests/test_live_fallback.py`
Mock the provider clients. **No real network calls in tests.** Cover:
- Finnhub quote raises `ProviderError` → snapshot comes from demo, `source: "demo"`, `ok: true`.
- FMP income statement raises → financials come from demo, `source: "demo"`.
- A single non-critical call fails (e.g. FMP dividends) → that field is `null`, everything else live, `source: "live"`.
- Ticker not in demo data and the live quote fails → 404 `DATA_NOT_AVAILABLE`.
- Live success then second call → `source: "cache"`, same `as_of`, and EPS `source_label` still names Finnhub.
- Live quote fails → demo served → second call still `source: "demo"` (never `"cache"`), per the ARCHITECTURE §4 provenance rule.
- Live provider returns market cap `2500` (millions) → snapshot `market_cap.value == 2.5e9`.
- An endpoint marked `ok: false` in `endpoint_check.json` is never called (assert the mock was not called).

Also do one manual check: put a wrong `FINNHUB_API_KEY` in `.env`, restart in live mode, load AAPL. It must show demo data with no crash and no key in the logs. Restore the key.

### 2.4 Protect the FMP quota (250 calls/day)
- Log every provider call at INFO with a running per-process count: `[services.market_data] fmp call #12 endpoint=income_statement_q ticker=AAPL`.
- Confirm one full load of all 5 tickers uses at most 4 FMP calls per stock ticker, and a reload within the TTL uses **zero**.
- Report the measured counts.

### 2.5 Pre-warm the cache — `services/warmup.py`
`run_if_enabled(app)`:
- If `config.WARM_CACHE` is false: log `"warmup disabled"` and return.
- Otherwise start **one background thread** (so server start is not blocked) that, for each ticker in `config.DEMO_TICKERS`:
  `market_data.get_snapshot` → `market_data.get_financials` → `earnings_service.build_facts` → `ai_service.explain_earnings(facts, config.DEFAULT_PROFILE)`.
- Any exception for one ticker is logged and the loop continues with the next.
- Log at the end: `"warmup done: 5/5 tickers in 14.2s"` (real counts and time).
- Works in both `DATA_MODE=demo` and `DATA_MODE=live`.

Verify: start with `WARM_CACHE=1`, wait for "warmup done", then open the app with the default profile (25–34, Medium). Every ticker's snapshot and earnings, including AI text, must load in under 1 second. Report the times.

## 3. Done criteria

1. All 5 tickers return contract-exact JSON in live mode, and the §2.2 table is filled in your report.
2. `pytest` passes (all agents' tests plus yours).
3. Wrong-key manual check passes.
4. Warm-cache timing check passes.
5. One commit: `[Agent E] Live data verified, fallbacks tested, cache warmup`.

## 4. Forbidden

- Editing any file you do not own (including `earnings_service.py`, routes, frontend, `config.py`, `docs/`).
- Changing any response shape or field name.
- Mixing demo values into a `source: "live"` response.
- Calling endpoints marked failed, or calling any provider endpoint not in the live mapping table.
- Real network calls in automated tests.
- New dependencies.
- Logging or printing key values.

## 5. Final report

1. Files changed
2. Endpoint check result (all 9 lines)
3. Live vs. demo comparison table (§2.2)
4. pytest summary line
5. FMP call counts (§2.4) and warm-cache timings (§2.5)
6. Fields that are `null` in live mode, and why
7. Anything unfinished
8. Changes needed in files you do not own (or "none")
