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

## Post-integration verification (2026-10-24)

The Wave 2 results above stand as recorded: the Anthropic key was absent during those integration tests. A key was added to `.env` afterwards, and real Claude output was checked with a hard limit of 2 calls per run (`DATA_MODE=demo`, `WARM_CACHE=0`, Finnhub and FMP disabled, SDK retries off).

- [services/ai_service.py] First live run (2 calls): both replies were cut off. Claude Sonnet 5.5 thinks by default when `thinking` is not set, and thinking spends `max_tokens` (300 chat / 900 earnings). Earnings JSON stopped mid-string (V1 → full fallback); chat returned no text (`AI_UNAVAILABLE`). Safe outcomes, but no Claude text reached the user → `_call_claude` now sends `thinking={"type": "between_tools"}` (thinking off; valid at the default effort, no effort setting is sent) and logs `stop_reason`, `output_tokens` and `max_tokens` only (WARNING when `stop_reason=max_tokens`) → mocked tests `test_call_claude_turns_thinking_off_and_logs_stop_reason` and `test_truncated_replies_stay_safe`; `pytest` 78 passed.
- Second live run (2 calls, after the fix):
  - AAPL earnings, age 25–34, medium risk: HTTP 200, `explanation_source=ai`, `stop_reason=end_turn`, 412 of 900 output tokens. One validation replacement: `V4 banned term in field=dividend` ("guaranteed" matched `guarantee\w*`), so dividend used the fallback sentence. All other fields were Claude text with no digits, no banned terms and no advice.
  - Chat "What is EPS?", same profile, no company context: HTTP 200, `stop_reason=end_turn`, 101 of 300 output tokens. A correct educational definition with no numbers or advice; C2 and C3 made no replacement.

### Open items
- The chat reply had five sentences; CHAT_SYSTEM_PROMPT asks for 2 or 3. Not a safety issue, and no Python check covers chat length (AI_RULES §6.3 has C1–C3 only). The prompt is unchanged for now.
- Two live samples confirm the fix works; they do not measure how often validation replaces Claude text. That is the rehearsal measurement in WORKFLOW.md step 7.
