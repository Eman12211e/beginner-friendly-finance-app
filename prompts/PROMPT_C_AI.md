# Agent C: AI — Prompt

You are **Agent C (AI)** for a beginner financial education web app.
Your job: make Claude explain financial facts in plain, safe, educational language, and build the chat.
The AI is a **teacher, not an advisor**. Python code must enforce that, not just the prompt.

Agents A (backend) and B (frontend) work **in parallel**. You never edit their files.

## 0. Read first (required)

1. `docs/AI_RULES.md` — **all of it. This is your core spec.** System prompts, fallbacks, and copy are to be used word for word.
2. `docs/API_CONTRACT.md` — §1, §3.3 (earnings `data` shape you receive as `facts` and the explanation key mapping), §3.4 (chat), §6 (frontend module contract).
3. `docs/ARCHITECTURE.md` — §2, §5 (your function signatures are fixed), §7, §8.
4. W0's code: `config.py`, `services/errors.py`, `services/cache.py`, `services/validation.py`, `routes/envelope.py`, the `services/ai_service.py` stub.

## 1. Files you own

`services/ai_service.py` (replace stub body, keep signatures), `services/prompts.py`, `routes/chat.py` (replace stub body, keep `bp`),
`static/js/chat.js`, `tests/test_chat.py`.

## 2. What to build

### 2.1 `services/prompts.py`
- `EARNINGS_SYSTEM_PROMPT`, `CHAT_SYSTEM_PROMPT` — word for word from AI_RULES §5.2 and §6.1.
- `ETF_KEYS_INSTRUCTION` — the ETF key replacement from §5.2.
- `FALLBACKS` — every sentence from AI_RULES §7, word for word, as a dict keyed by section and variant (e.g. `FALLBACKS["revenue"]["up"]`).
- `CHAT_FALLBACK_NUMBERS` and `CHAT_FALLBACK_ADVICE` — the C2 and C3 replacement texts from §6.3.
- `BANNED_EARNINGS_PATTERNS` (V4) and `BANNED_CHAT_PATTERNS` (C3) as compiled regexes with word boundaries.
- `CHECKLIST_TRIGGER` regex (C1).

### 2.2 `services/ai_service.py`
- One private function `_call_claude(system, messages, max_tokens) -> str` that is the **only** place the `anthropic` client is used. Model and timeout from `config`. This makes mocking easy in tests.
- If `config.ANTHROPIC_API_KEY` is empty: `explain_earnings` returns full fallback; `chat` raises `AIUnavailable`.

**`explain_earnings(facts, profile)`** (facts = the `data` object A built, API_CONTRACT §3.3):
1. Build the payload of AI_RULES §5.1 from `facts` (directions and comparisons only, **no numbers**). A section is `available` if its main `value.value` is not `None` (for `eps`: `actual.value`; for `headline`: `comparison`; for `dividend`: `pays_dividend`).
2. Check the cache (`ai:earnings:{ticker}:{period_end}:{age_range}:{risk}`; ETFs use `etf` instead of `period_end`).
3. Call Claude. Run validation V1–V7 from AI_RULES §5.4 per field. Replace failing fields with the matching fallback variant (picked by `direction` / `comparison` / `pays_dividend`). Log each replacement at WARNING with the check id.
4. V6: force `None` for unavailable sections, always.
5. Return `(explanations, "ai" | "fallback")`. Cache the result. **Never raise.** Any exception → full fallback.

**`chat(message, history, profile, context_facts)`**:
1. Build the system prompt with `{profile}` and `{context}`. `{context}` = the reduced context (only `display` strings, labels, titles, directions, comparisons, `explain` texts, `etf_message`) as compact JSON. Empty → `"none"`.
2. Messages = last `CHAT_HISTORY_LIMIT` history items (roles `user`/`assistant` only, other roles dropped) + the new user message.
3. Call Claude. On failure raise `AIUnavailable`.
4. Apply C2 and C3 (AI_RULES §6.3). Return the reply string.

### 2.3 `routes/chat.py` — `POST /api/chat`
- Parse JSON body. Validate per API_CONTRACT §3.4: `message` 1–500 chars after trim else `INVALID_REQUEST`; `profile` via `validate_profile`; `history` must be a list (else treat as empty); `context` may be `null`.
- `show_checklist_link` = C1 on the user message, OR true if C3 replaced the reply.
- Return `ok({"reply", "show_checklist_link"}, context.source or None, context.as_of or None)`.
- `AppError` → `fail`. Other exceptions → log traceback → INTERNAL_ERROR.

### 2.4 `static/js/chat.js` → `window.Chat`
Fill `#chat-root`:
- Title "Ask a question", message list, `<textarea maxlength="500">`, Send button (Enter sends, Shift+Enter new line), and the chat note from AI_RULES §9 under the input.
- Starter prompt chips shown when empty: "What is EPS?", "What does revenue mean?", "What is an ETF?". Clicking one sends it.
- Keep history in memory only (last 6 messages). Send `profile` from `window.Profile.get()` and `context` from the latest `app:company-loaded` detail (`{ticker, source, as_of, snapshot, earnings}`), or `null`.
- Show "Thinking..." while waiting. Disable Send while a request is in flight.
- If `show_checklist_link` is true, show a link-style button "Open the pre-purchase checklist" under that reply. Click → dispatch `app:open-checklist`.
- `ok: false` → show `error.message` as a system message. Never throw.
- When the ticker changes, show a small divider "Now looking at: TICKER" in the message list (history is kept).
- All text via `textContent`. Never `innerHTML`.
- Styles: put minimal chat styles in a `<style>` block injected by `chat.js` with selectors scoped under `#chat-root` (you do not own any CSS file).
- Calls the backend only through `window.Api.postChat`.

## 3. Tests — `tests/test_chat.py`

Patch `services.ai_service._call_claude`. Never call the real API in tests.
Implement all tests T1–T11 and T15–T16 from AI_RULES §8. Also:
- T12: payload sent to Claude contains no digits from the facts' financial values (assert on the `messages` passed to the mock).
- T13: cache — second identical `explain_earnings` call does not call Claude again.
- T14: a revenue explanation containing "selling its products" passes V4 (whole-word matching).

Build synthetic `facts` with ticker `EXMPL` in the API_CONTRACT §3.3 shape.

## 4. Manual check with a real key (after tests pass)

Run the app with `ANTHROPIC_API_KEY` set:
- Call `explain_earnings` on synthetic facts once from a Python shell and paste the output into your report. Check: 2–3 sentences, no digits, no banned words.
- Ask the chat "What is EPS?" and "Should I buy Apple?" with `curl`. Paste both replies.

## 5. Done criteria

All tests pass; manual check outputs look correct; one commit: `[Agent C] AI: earnings explanations, validation, chat`.

## 6. Forbidden

- Editing any file you do not own.
- Sending numbers to Claude for earnings explanations.
- Raising from `explain_earnings`.
- Loosening any validation rule or rewording any prompt/fallback/copy from AI_RULES.
- Giving Claude any data the browser did not send (no extra fetching for chat).
- Calling the real Claude API in automated tests.

## 7. Final report

1. Files changed
2. pytest summary line
3. Real-key outputs from §4
4. Validation replacements observed during the manual check (field + check id), if any
5. Anything unfinished
6. Changes needed in files you do not own (or "none")
