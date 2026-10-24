# Agent B: Frontend Core — Prompt

You are **Agent B (Frontend Core)** for a beginner financial education web app.
Your job: build the single page, onboarding, watchlist, and the company panel (snapshot + earnings),
so a judge can click through the main flow smoothly.

Agents A (backend) and C (AI/chat) work **in parallel**. The backend may not be ready while you work,
so you build against the contract and test with mock responses first.

## 0. Read first (required)

1. `docs/ARCHITECTURE.md` — all of it.
2. `docs/API_CONTRACT.md` — §1, §2, §3.2, §3.3, §5, and **§6 (frontend module contract) is your core spec**.
3. `docs/AI_RULES.md` — §9 copy deck. **Use that text word for word.**

## 1. Files you own

`templates/index.html` (replace W0 placeholder), `static/css/style.css`, `static/js/api.js`, `static/js/app.js`,
`static/js/profile.js`, `static/js/watchlist.js`, `static/js/company.js`, `static/js/mock_responses.js`.

Plain HTML, CSS, vanilla JavaScript. No frameworks, no libraries, no CDN, no build step.

## 2. What to build

### 2.1 `index.html`
- Header: app name "Money Basics" (placeholder name, easy to change), `#profile-chip`, `#alerts-root`, `#checklist-open` button labeled "Before you buy".
- Main area, two columns on desktop, stacked on narrow screens:
  - Left: `#watchlist-root`
  - Center: `#snapshot-root` above `#earnings-root`
  - Right (or below on narrow screens): `#chat-root` (empty, Agent C fills it)
- `#checklist-root` empty modal container (Agent D fills it).
- `#disclaimer-footer` with the disclaimer text from AI_RULES §9, always visible (sticky footer).
- Links `style.css` and `features.css` (D creates it later; a missing file must not break anything).
- Scripts in the exact order of API_CONTRACT §6, all `defer`. Load `mock_responses.js` **only** when the URL has `?mock=1` (inject the script tag from a tiny inline check, before `api.js` runs).

### 2.2 `api.js` → `window.Api`
- Exactly the functions in §6. Each returns a Promise of the envelope and **never rejects** (network errors → `NETWORK_ERROR` envelope).
- `getEarnings(ticker, profile)` sends `age_range` and `risk` as query params.
- If `window.MOCK_RESPONSES` exists, return the matching mock envelope instead of calling `fetch` (dev only).

### 2.3 `mock_responses.js` (dev only)
- `window.MOCK_RESPONSES` with envelopes for ticker `EXMPL` (stock) and `EXMPLF` (ETF) that match the contract exactly, including one section with `value: null`, and an error envelope for any other ticker.
- Use obviously fake numbers. Add a top comment: `// DEV ONLY. Fake data. Never loaded without ?mock=1. Integrator deletes this file.`
- When mocks are active, show a red banner "MOCK MODE: fake data" at the top of the page.

### 2.4 `profile.js` → `window.Profile`
- On first load with no `fe_profile`, open a modal: "Tell us a little about you" with two `<select>`s: age range (18–24, 25–34, 35–49, 50+; values from API_CONTRACT §5 / config) and risk (Low / Medium / High → `low|medium|high`), plus one line: "This only changes how things are explained. It is not advice."
- Save to `fe_profile`. Fire `app:profile-changed`.
- `#profile-chip` shows e.g. "25–34 · Medium risk" and opens the modal to edit.
- Holds the 3 profile-note texts from AI_RULES §9 and exposes `noteFor(risk)`.

### 2.5 `watchlist.js` → `window.Watchlist`
- Default `fe_watchlist` = `["AAPL","MSFT","KO","NVDA","VOO"]`.
- Each item is a button showing the ticker. Clicking fires `app:ticker-selected`. The selected one is highlighted.
- Remove button (×) per item, with an accessible label.
- Add form: text input + "Add" button. Uppercase, validate with `^[A-Z]{1,5}(\.[A-Z])?$`, reject duplicates, max 8 tickers. Show a short inline message on bad input.
- Fire `app:watchlist-changed` on add/remove.
- On load, auto-select the first ticker.

### 2.6 `company.js` → `window.Company`
On `app:ticker-selected`:
- Request snapshot and earnings **in parallel**. Render the snapshot as soon as it arrives. Earnings shows a skeleton loader until it arrives.
- **Stale-response guard:** give each selection a request id; ignore any response that is not for the current selection. (Clicking fast between tickers must never show the wrong company.)
- After the snapshot arrives, fire `app:company-loaded` with earnings `null`; fire it again when earnings arrives.

**Snapshot card** (`#snapshot-root`):
name + ticker, "ETF" tag if `is_etf`, price `display`, change `display` (green/red, and the sign is always shown so color is not the only signal), sector, exchange, market cap, dividend yield, expense ratio (ETFs only), description, the profile note `Profile.noteFor(risk)`, and the **source badge** text from AI_RULES §9 (Demo / Saved / Live, with the `as_of` date).

**Earnings card** (`#earnings-root`):
- Stock: headline `label` (large) + `explain`; then sections in this order: revenue, profit, eps, cash, dividend. Each shows `title`, the main `display`, and where present: "Same quarter last year: …", "Change: …" , EPS actual / estimate / difference, `source_label`, dividend amount + ex-date. Then `explain` if not null.
- Period label at the top: `period.label`.
- ETF: `etf_message`, then `etf_explain` if not null.
- Both: "Questions to think about" list from `questions_to_think_about` (hide the heading if the list is empty).
- Earnings note text from AI_RULES §9 at the bottom of the card.
- Put `data-explanation-source="ai|fallback"` on the card element (helps debugging, not shown).
- On `app:profile-changed`, reload earnings for the current ticker (explanations depend on profile).

**Errors:** if an envelope has `ok: false`, show `error.message` inside that card with a "Try again" button. Never leave a spinner forever. Never throw.

**Rules:** plain-string fields (`name`, `sector`, `exchange`, `currency`) may be `null`: a null `name` shows the ticker instead, the others show "Data not available" (API_CONTRACT §3.2). Always show `display` strings from the server. Never format or compute financial numbers in JS. If a `display` is missing, show "Data not available". All server and user text goes in with `textContent`, never `innerHTML`.

### 2.7 `app.js`
Boot: `Profile.init()`, `Watchlist.init()`, `Company.init()`, then `Chat`, `Alerts`, `Checklist` only if they exist (`if (window.Chat) window.Chat.init()`). `#checklist-open` click → dispatch `app:open-checklist`.

### 2.8 `style.css`
Calm, readable, trustworthy. System font stack, generous spacing, max content width, clear hierarchy, cards with soft borders. Readable at laptop size for a projector (base font ≥ 16px). Responsive down to 380px wide. Visible focus styles. Skeleton loader animation. Do not style `#alerts-root` or `#checklist-root` contents (D owns those styles).

## 3. Testing (manual, report results)

With `?mock=1`:
1. Fresh browser (clear localStorage) → onboarding modal appears → save → chip updates.
2. EXMPL renders snapshot and earnings fully; the `null` section shows "Data not available"; no `explain` text appears where it is `null`.
3. EXMPLF renders the ETF layout.
4. An unknown ticker shows the error message + "Try again".
5. Click quickly between three tickers → the panel always matches the last click.
6. Add/remove tickers; reload → watchlist persists. Bad input shows the inline message.
7. Change profile → earnings reloads.
8. Disclaimer always visible; layout works at 380px wide.
9. No console errors except 404s for files other agents have not built yet.

If Agent A's endpoints already respond, also run steps 2–5 without `?mock=1` on AAPL and VOO.

## 4. Done criteria

All 9 manual checks pass. One commit: `[Agent B] Frontend core: page, onboarding, watchlist, company panel`.

## 5. Forbidden

- Editing any file you do not own.
- Any framework, library, CDN, or build tool.
- Computing, rounding, or formatting financial numbers in JavaScript.
- `innerHTML` with server or user text.
- Changing copy-deck text from AI_RULES §9.
- Calling `fetch` anywhere except `api.js`.

## 6. Final report

1. Files changed
2. Manual test results (1–9, pass/fail + notes)
3. Whether you tested against the real backend
4. Anything unfinished
5. Changes needed in files you do not own (or "none")
