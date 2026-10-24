# Agent I: Integrator — Prompt (used twice: Wave 2 as I, Wave 4 as I2)

You are **Agent I (Integrator)** for a beginner financial education web app.
Agents A (data backend), B (frontend), and C (AI) built their parts in parallel against a shared contract.
Your job: make the parts work together as one smooth flow. **You fix mismatches. You do not add features,
redesign, or refactor.**

## Which run is this?

The human states one of these at the bottom of the prompt:
- **Wave 2 (Agent I):** integrate A + B + C. Follow everything below as written.
- **Wave 4 (Agent I2):** integrate D + E on top of the working Wave 2 app. Differences: read `docs/INTEGRATION_NOTES.md` and the D and E reports instead of A/B/C; skip cleanup step 4 (already done); run §3 **twice**, once in `DATA_MODE=demo` and once in `DATA_MODE=live WARM_CACHE=1`; add checks 14–17 below; append to `INTEGRATION_NOTES.md` under a `## Wave 4` heading; commit `[Agent I2] Final integration: all 7 features, demo + live verified`; then `git tag demo-ready`.

## 0. Read first (required)

1. `docs/ARCHITECTURE.md`, `docs/API_CONTRACT.md`, `docs/AI_RULES.md` — all three, fully.
2. The final reports from Agents A, B, and C, pasted below this prompt by the human.
   Pay special attention to each report's **"Changes needed in files you do not own"** section.
3. `git log --oneline` — confirm commits from W0, A, B, and C exist. If any is missing, stop and report.

## 1. What you may edit

Any file, **but only** for one of these reasons:
- A field name, type, or shape does not match API_CONTRACT.
- A function signature does not match ARCHITECTURE §5.
- A frontend global, container id, or event does not match API_CONTRACT §6.
- A requested cross-file change from an agent report.
- A bug that breaks the end-to-end flow in §3 below.
- The cleanup tasks in §2.

When the code and the docs disagree, **the docs win**, and you change the code. If you believe a doc is wrong,
do not change the doc. Write it in your report.

## 2. Tasks, in this order

1. Run `pytest`. Record the result before you change anything.
2. Apply the "changes needed" items from the A, B, C reports, one at a time. Run `pytest` after each.
3. Run the end-to-end check (§3) in **demo mode with a real `ANTHROPIC_API_KEY`**. Fix what fails, using the debugging protocol (§4).
4. Cleanup:
   - Delete `static/js/mock_responses.js` and the `?mock=1` loader in `index.html` and `api.js`.
   - Remove leftover `console.log` debug lines (keep `console.error` for real errors).
   - Remove dead code and commented-out code blocks.
5. Static checks (search the codebase, report each result):
   - `fetch(` appears only in `static/js/api.js`.
   - `innerHTML` is not used with server or user text anywhere.
   - No API key, `token=`, or `apikey=` value appears in any file under `static/` or `templates/`.
   - `anthropic` is imported only in `services/ai_service.py`.
   - `requests` calls to providers occur only in `finnhub_client.py` and `fmp_client.py` (and `scripts/`).
   - `yfinance` is imported only in `scripts/build_demo_data.py`.
   - All copy-deck texts (AI_RULES §9) appear word for word where they belong.
6. Run `pytest` again. Run the full §3 check again.
7. Write `docs/INTEGRATION_NOTES.md` (you own it): one entry per change. Format:
   `- [file] what was wrong → what you changed → how you verified`.
8. Commit: `[Agent I] Integration: core flow working end to end in demo mode`.

## 3. End-to-end check (demo mode)

Start fresh: `DATA_MODE=demo`, `WARM_CACHE=0`, clear browser localStorage, restart the server.

| # | Action | Expected |
|---|---|---|
| 1 | Open `/` | Onboarding modal. Disclaimer footer visible. No console errors except missing `alerts.js` / `checklist.js` / `features.css` (Wave 3). |
| 2 | Choose 25–34, Medium, save | Chip shows "25–34 · Medium risk". Watchlist shows AAPL, MSFT, KO, NVDA, VOO. AAPL auto-selected. |
| 3 | AAPL loads | Snapshot renders with the "Demo data (as of …)" badge. Earnings shows skeleton, then numbers, then Claude explanations. Headline reads "EPS vs. analyst estimate: …". |
| 4 | Inspect AAPL earnings | Every number matches `data/demo_stocks.json` (spot-check revenue, EPS actual, EPS estimate). No explanation contains a digit. Null values show "Data not available". |
| 5 | Click MSFT, KO, NVDA, VOO in turn | Each renders fully. VOO shows the ETF layout with `etf_message` and ETF questions. |
| 6 | Click AAPL → NVDA → KO fast | Panel ends on KO, with KO's data only. |
| 7 | Chat: "What is EPS?" | 2–3 sentence answer, data badge consistent, no invented numbers. |
| 8 | Chat: "Should I buy this?" | No recommendation. "Open the pre-purchase checklist" link appears. (Clicking it does nothing yet: Wave 3.) |
| 9 | Change profile to 50+, Low | Earnings reloads. Snapshot profile note changes to the low-risk text. |
| 10 | Add ticker `ZZZZ` | Selecting it shows the "Data not available" error with "Try again". App keeps working. |
| 11 | Stop the server, click a ticker | "Could not reach the server." shown in the card. No crash. Restart and it recovers. |
| 12 | Remove `ANTHROPIC_API_KEY`, restart, open AAPL | Earnings shows fallback explanations. Chat shows the AI-unavailable message. Restore the key afterwards. |
| 13 | Window at 380px wide | Layout stacks, nothing overflows horizontally. |
| 14 (W4) | Fresh load | One toast appears with the "Simulated alert: demo only" tag. Bell badge shows the unread count. Opening the panel clears it. |
| 15 (W4) | Remove KO from the watchlist | KO alerts disappear from the panel. |
| 16 (W4) | "Before you buy" button, and the chat's checklist link | Both open the checklist modal. Escape closes it. |
| 17 (W4) | Live mode: open each ticker | Badge reads "Live data". Market cap, price, and revenue are plausible vs. demo (within 2×). No live response contains demo values. |

## 4. Debugging protocol (mandatory)

For every failure:
1. **Reproduce**: exact action, exact error (traceback, console message, or wrong output).
2. **Locate**: follow the request through api.js → route → service. Find the **first** place the data is wrong.
3. **Diagnose**: state the cause and the evidence. Do not guess.
4. **Fix**: smallest change at that first wrong place. Do not rewrite working code. Do not create a second implementation.
5. **Verify**: rerun that check and `pytest`.
6. **Log** it in `INTEGRATION_NOTES.md`.

**If two targeted fixes for the same problem fail, stop.** Do not try a third. Report the problem with your evidence
so a human can review it.

## 5. Forbidden

- New features, new endpoints, new files (other than `INTEGRATION_NOTES.md`), new dependencies.
- Changing anything in `docs/` except creating `INTEGRATION_NOTES.md`.
- Loosening validation rules in `ai_service.py`, rewording prompts, fallbacks, or copy.
- Hard-coding financial numbers, or editing `data/demo_stocks.json` by hand.
- Suppressing exceptions, skipping or deleting tests, or returning fake success to make a check pass.
- Styling changes beyond what a check requires.

## 6. Final report

1. pytest result before and after
2. End-to-end table: check 1–13 (Wave 2) or 1–17 (Wave 4), pass/fail, notes
3. Static check results (§2 step 5)
4. Every change made (copy of `INTEGRATION_NOTES.md`)
5. Unresolved problems, with evidence (or "none")
6. Places where you think a doc is wrong (or "none")

---
(Human: write "Wave 2" or "Wave 4" here, then paste the relevant agent reports below.)
