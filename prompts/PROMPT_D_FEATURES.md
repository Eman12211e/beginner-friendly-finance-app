# Agent D: Features — Prompt

You are **Agent D (Features)** for a beginner financial education web app.
The core flow (watchlist → snapshot → earnings → chat) already works. Your job: add the
**simulated alerts** and the **pre-purchase checklist**, without touching anyone else's files.

Agent E works **in parallel** with you on live data. You never edit E's files, and E never edits yours.

## 0. Read first (required)

1. `docs/ARCHITECTURE.md` — §2, §3, §5 (`build_alerts` signature), §7 (decision 9), §8.
2. `docs/API_CONTRACT.md` — §1, §2, **§3.5 (your endpoint spec)**, §4 (demo data schema), §5, **§6 (frontend module contract)**.
3. `docs/AI_RULES.md` — §9 copy deck (simulated label, checklist text). **Use that text word for word.**
4. `docs/INTEGRATION_NOTES.md` — what changed during integration.
5. Existing code you will **use but not edit**: `services/market_data.py` (its demo-data loader), `services/formatting.py`,
   `services/validation.py`, `routes/envelope.py`, `static/js/api.js` (`Api.getAlerts`), `static/js/watchlist.js` (`Watchlist.get()`).

## 1. Files you own

`services/alerts_service.py`, `routes/alerts.py` (replace W0 stub body, keep `bp`), `static/js/alerts.js`,
`static/js/checklist.js`, `static/css/features.css`, `tests/test_alerts.py`.

## 2. What to build

### 2.1 `services/alerts_service.py` — `build_alerts(tickers) -> list[dict]`
- Get demo data through the **existing** demo loader in `market_data.py` (read that file to find it). **Do not write a second JSON loader.** If the loader is private (e.g. `_load_demo()`), calling it is acceptable; mention it in your report.
- Data source is **always** `demo_stocks.json`, in every `DATA_MODE`. (Contract §3.5: `source` is always `"demo"`.)
- For each ticker present in demo data (others are skipped):
  - **Dividend alert** only if `pays_dividend` is `true` and both `last_amount` and `last_ex_date` are not null.
    `title`: `"Dividend paid"`. `body`: `"<name> paid a dividend of <money_per_share(last_amount)> per share. The ex-dividend date was <date_display(last_ex_date)>."` `event_date`: `last_ex_date`.
  - **Earnings alert** only if `next_earnings_date` is not null.
    `title`: `"Earnings report expected"`. `body`: `"<name> is expected to report earnings on <date_display(next_earnings_date)>."` `event_date`: `next_earnings_date`.
  - `id`: `"<TICKER>-<type>-<event_date>"`. `simulated: true`. `label`: exactly `"Simulated alert: demo only"`.
- Use `formatting.py` for every number and date. **No number or date may be typed into code.**
- Sort by `event_date`, newest first.

### 2.2 `routes/alerts.py` — `GET /api/alerts?tickers=AAPL,KO`
- `tickers` missing or empty → `INVALID_REQUEST`.
- Split on commas, trim, validate each with `validate_ticker` (bad format → `INVALID_TICKER`). Tickers not in demo data are skipped silently (logged at INFO).
- Return `ok({"alerts": [...]}, "demo", <demo generated_at>)`.
- `AppError` → `fail`. Other exceptions → log traceback → INTERNAL_ERROR.

### 2.3 `static/js/alerts.js` → `window.Alerts`
Fill `#alerts-root` (in the header):
- A bell button with an accessible label "Alerts" and a badge with the **unread** count (hidden when 0).
- Click → dropdown panel listing each alert: the `label` as a visible tag, `title`, `body`, and `event_date` shown as the body already formats it. Panel closes on outside click and Escape.
- Read state: store read ids in localStorage key `fe_alerts_read` (array). Opening the panel marks visible alerts read. Wrap storage in `try/catch`.
- **Simulated in-app notification:** on `init()`, if there is an unread alert, show one toast for 6 seconds with the newest unread alert's `title`, `body`, and the `label` tag. One toast per page load maximum.
- On `app:watchlist-changed`, refetch with the new tickers. On `init()`, fetch with `Watchlist.get()`.
- Calls the backend only through `window.Api.getAlerts`. All text via `textContent`.
- `ok: false` → panel shows "Alerts are not available right now." Never throw.

### 2.4 `static/js/checklist.js` → `window.Checklist`
Fill `#checklist-root` as a modal:
- Title and the 7 questions from AI_RULES §9, word for word, each with a checkbox.
- One extra line under the list, exactly: `"These questions help you think. They are not advice."`
- Close button, Escape key, and backdrop click all close it. Move focus into the modal on open and back to the opener on close.
- Checkbox state lasts only while the page is open (not stored).
- `open()` opens it. Listen for `app:open-checklist` and call `open()`.
- Questions only. No scoring, no "you are ready to buy" message, no AI.

### 2.5 `static/css/features.css`
Styles for the bell, badge, dropdown, toast, and checklist modal only. Scope every selector under `#alerts-root`, `#checklist-root`, or a `.fe-toast` class. Match the calm look of `style.css` (read it, reuse its colors and spacing, do not edit it). The simulated label tag must be clearly visible (for example, an outlined pill). Works at 380px wide.

## 3. Tests — `tests/test_alerts.py` (demo mode)

- `GET /api/alerts?tickers=AAPL,KO` → `ok: true`, `source: "demo"`, every alert has `simulated: true` and the exact label.
- KO dividend alert body contains the amount and date formatted from `demo_stocks.json` (compute the expected string from the JSON with `formatting.py` in the test; do not hard-code it).
- Missing `tickers` → 400 `INVALID_REQUEST`. `tickers=AA1` → 400 `INVALID_TICKER`. `tickers=AAPL,ZZZZ` → AAPL alerts only.
- Patch the demo loader with a synthetic `EXMPL` entry where `last_ex_date` is null and `next_earnings_date` is null → no alerts for EXMPL.
- Alerts sorted newest `event_date` first.

## 4. Manual checks (report results)

1. Fresh localStorage → toast appears once with the simulated label → bell badge shows unread count.
2. Open panel → badge clears → reload → no toast (all read).
3. Remove KO from the watchlist → its alerts disappear.
4. "Before you buy" header button opens the checklist. Chat's "Open the pre-purchase checklist" link opens it too.
5. Escape, close button, and backdrop all close it. Keyboard focus returns to the opener.
6. Layout at 380px wide.

## 5. Done criteria

Tests and manual checks pass. One commit: `[Agent D] Simulated alerts and pre-purchase checklist`.

## 6. Forbidden

- Editing any file you do not own (including `index.html`, `style.css`, `market_data.py`, `formatting.py`).
- Typing any financial number or date into code, tests excepted for synthetic `EXMPL` data.
- Alert wording that implies an event happened in real time, or an earnings alert without "expected".
- Any advice, scoring, or conclusion in the checklist.
- `innerHTML` with server text. `fetch` outside `api.js`.

## 7. Final report

1. Files changed
2. pytest summary line
3. Manual check results (1–6)
4. Which demo loader function you used
5. Anything unfinished
6. Changes needed in files you do not own (or "none")
