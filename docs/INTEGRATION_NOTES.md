# INTEGRATION_NOTES.md

Owner: Agent I (Integrator). One entry per change: `- [file] what was wrong → what changed → how verified`.

## Wave 2 (Agent I)

Baseline before any change: `pytest` 75 passed. Commits present: W0 `607f726`, A `c090391`, C `a949cda`, B `4a3f17e` (plus `d059ebb` test-key isolation).

### Changes requested in agent reports
- [static/js/chat.js] Send button shrank in the narrow chat column and its label wrapped to "Sen / d" (Agent B report) → added `#chat-root .chat-row button{flex:none}` to the injected chat styles → headless Edge: button renders on one line (32 px high), screenshot checked.
- [tests/test_scaffold.py] No regression test guarded the conftest.py key isolation (recommended in the `d059ebb` report) → added `test_tests_never_see_real_api_keys` (all three keys `""`, `DATA_MODE` demo, `WARM_CACHE` off) → `pytest` 76 passed.

### End-to-end fixes
- [static/js/chat.js] Starter chips stayed visible after the first message: the `.chat-starters{display:flex}` rule overrode the `hidden` attribute, contrary to PROMPT_C §2.4 ("shown when empty") → added `#chat-root .chat-starters[hidden]{display:none}` → headless Edge: chips visible before the first message, hidden after.

### Cleanup
- [static/js/mock_responses.js] Dev-only mock data → deleted → `/static/js/mock_responses.js` returns 404.
- [templates/index.html] `?mock=1` inline loader → removed → `/?mock=1` loads no mocks (`window.MOCK_RESPONSES` undefined, no banner).
- [static/js/api.js] `window.MOCK_RESPONSES` branch in `request()` → removed → all calls go through `fetch`; e2e checks 1–13 pass.
- [static/css/style.css] Unused `.mock-banner` rule → removed → no remaining `mock` references in `static/` or `templates/`.
- `console.log` debug lines: none found. Dead or commented-out code: none found beyond the mock path.

### Verification
- `pytest`: 76 passed.
- `node --check`: all 6 files in `static/js/` pass.
- Static checks: `fetch(` only in `api.js` · no `innerHTML` · no key, `token=` or `apikey=` value in `static/` or `templates/` · `anthropic` imported only in `services/ai_service.py` · provider `requests` calls only in `finnhub_client.py`, `fmp_client.py` and `scripts/` · `yfinance` imported only in `scripts/build_demo_data.py` · AI_RULES §9 copy present word for word (Agent D copy pending Wave 3).
- End-to-end §3 in headless Edge (disposable profile, `DATA_MODE=demo`, all API keys blanked for the server process): checks 1–6 and 9–13 PASS; 7 and 8 NOT RUN (need real Claude replies; Anthropic key intentionally absent); 12 verified as the no-key case. Server log shows no Finnhub, FMP or Anthropic calls.

### Open items (not changed)
- Real Claude output (check 3 AI text, checks 7 and 8) is unverified until an Anthropic key is used.
- PROMPT_B_FRONTEND §2.3 names the mock ETF `EXMPLF` (6 letters), which the contract's 1–5 letter ticker rule rejects. The mock is now deleted, so this matters only for the doc.
