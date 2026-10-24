# DEMO_SCRIPT.md — Presentation Runbook

> Owner: Planner. Put this in `docs/`. Practice the click path at least 3 times before 8:15 PM.
> Submission deadline: **8:45 PM PST**. Feature freeze: **7:30 PM**.

---

## 1. Presentation mode

**Primary:** live data with a pre-warmed cache. **Backup:** demo data (real numbers saved earlier by the script).

| | Command (from the project folder, venv active) |
|---|---|
| Primary | `DATA_MODE=live WARM_CACHE=1 python app.py` |
| Backup | `DATA_MODE=demo WARM_CACHE=1 python app.py` |

Windows PowerShell: `$env:DATA_MODE="live"; $env:WARM_CACHE="1"; python app.py`

Wait for the log line `warmup done: 5/5 tickers ...` before you open the browser.
If the live run shows anything odd during rehearsal, present in backup mode. It is still real data.

> **macOS note:** AirPlay Receiver uses port 5000. If the app will not start or the page does not load,
> turn it off: System Settings → General → AirDrop & Handoff → AirPlay Receiver → Off.

---

## 2. Before you present

### At 7:30 PM (feature freeze)
- [ ] All agents' commits are in. `git status` is clean.
- [ ] `pytest` passes.
- [ ] `git tag demo-ready` — this is your safe point. If anything breaks later: `git checkout demo-ready`.
- [ ] Record one full run of the click path (screen recording). This is your last-resort backup.

### 10 minutes before you present
- [ ] Laptop plugged in. Notifications off (Do Not Disturb).
- [ ] `.env` has all 3 keys. `GET /api/health` shows `keys_present` all `true`.
- [ ] Start the app in primary mode. Wait for `warmup done`.
- [ ] Open a **private / incognito** window at `http://localhost:5000` so onboarding appears fresh.
- [ ] Browser zoom 125% so the room can read it.
- [ ] Close every other tab.
- [ ] **Do not onboard yet.** You do it live in step 2 below.

---

## 3. Click path (about 4 minutes)

Choose **25–34** and **Medium** in onboarding. That is the profile the cache was warmed with, so every click is instant.

| # | Do this | Say this (short) |
|---|---|---|
| 1 | Show the empty page with the onboarding modal | "Beginners get advice from social media and AI chats that sound sure of themselves. We built the opposite: an app that teaches, so people can think for themselves." |
| 2 | Pick 25–34, Medium. Save. | "Two questions. They change how things are explained, never what the app recommends. It does not recommend anything." |
| 3 | AAPL opens. Point at the badge and the snapshot. | "Every screen says where the data came from and when. This is live data from Finnhub and FMP." |
| 4 | Scroll to earnings. Point at the headline. | "We say 'EPS vs. analyst estimate: Above', not 'beat'. We name the benchmark: the average analyst forecast. Words like 'beat' hide that." |
| 5 | Point at one number, then its explanation | "Key design rule: Python writes every number. Claude writes only the words, and Claude never even sees the numbers. It cannot misquote what it never received." |
| 6 | Point at "Questions to think about" | "Instead of a conclusion, we give questions. The user does the thinking." |
| 7 | Click **KO**. Point at the dividend section. Open the bell. | "Alerts are simulated for the demo, and the app says so on every one. Their numbers come from real data." |
| 8 | Click **VOO** | "An ETF has no earnings report. Instead of showing empty boxes, the app teaches what an ETF is." |
| 9 | Chat: type **What is EPS?** | "Answers are short on purpose: two or three sentences, plain words, based on a writing standard from aerospace, ASD-STE100." |
| 10 | Chat: type **Should I buy Apple?** | "It will not tell you. It explains what people consider, and points to the checklist." |
| 11 | Click **Open the pre-purchase checklist** | "Seven questions to ask yourself. No score, no 'you are ready'. The decision stays with the person." |
| 12 | Close. Point at the footer. | "The disclaimer is always visible. Safety here is in the code, not only in a prompt: every AI sentence is checked by Python before you see it." |

If a value shows **"Data not available"**, say: "When we don't have a number, we say so. We never estimate or fill gaps."

---

## 4. If something goes wrong on stage

| Problem | What to do |
|---|---|
| Page shows an error card | Click **Try again** once. If it repeats, move to the next ticker and keep talking. |
| Earnings text looks generic | That is the fallback text. It is correct and safe. Keep going. |
| Chat says the AI is unavailable | Say: "If the AI is down, the app tells you honestly instead of guessing." Skip to the checklist (step 11). |
| Whole app is broken | Stop the server (Ctrl+C). Start the **backup** command. Reload. Onboard again with 25–34 / Medium. |
| Laptop or server will not recover | Play the screen recording from 7:30 PM. |

---

## 5. Likely judge questions

| Question | Short answer |
|---|---|
| How do you stop the AI from making up numbers? | Claude never receives the numbers. It only gets "revenue went up" or "EPS was above the estimate". Python then rejects any AI sentence that contains a digit. |
| What stops it from giving advice? | Three layers: the prompt, a Python check for banned words like "buy" and "because", and safe pre-written fallback text. A false alarm only costs a plainer sentence. |
| Why not let the AI explain why revenue changed? | The data does not include the reason. Any reason would be a guess presented as fact. The app says "The data does not show the reason." |
| Where does the data come from? | Live: Finnhub for prices and earnings estimates, FMP for financial statements. Backup: real data saved from Yahoo Finance, labeled with its date. |
| Why "analyst estimate" and not "beat"? | "Beat" hides the benchmark. The estimate is the average analyst forecast, not the company's own target. We name it. |
| What about news? | We left it out on purpose. Many finance articles are auto-generated to push a story. We did not want to feed that into explanations. |
| What happens when an API fails? | Each provider failure falls back to saved real data, labeled as such. One missing field shows "Data not available". It never crashes or guesses. |
| Why the short sentences? | ASD-STE100 is a controlled-English standard for clear technical writing. Two or three sentences per idea keeps beginners from being overloaded. |
| What would you build next? | A custom data pipeline to replace the saved-data script, more tickers, and lessons that link from each explanation. |
