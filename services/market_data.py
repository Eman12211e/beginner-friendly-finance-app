"""Source picker: cache -> live -> demo (ARCHITECTURE §4). Live and demo produce the same internal shape."""
import json
import logging
import os
import re
from datetime import date, datetime, timezone

import config
from services import cache, finnhub_client, fmp_client
from services.errors import DataNotAvailable, ProviderError
from services.formatting import field, money_large, money_per_share, pct_change, pct_level

log = logging.getLogger(__name__)
DEMO_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "demo_stocks.json")
_demo = None

_ABBREVIATIONS = ("Inc.", "Corp.", "Co.", "Ltd.", "U.S.", "Mr.", "Ms.")
_SENTENCE_END = re.compile(r"[.!?]\s+(?=[A-Z])")


def load_demo():
    global _demo
    if _demo is None:
        with open(DEMO_PATH, encoding="utf-8") as f:
            _demo = json.load(f)
    return _demo


def first_two_sentences(text):
    if not text:
        return None
    ends = 0
    for m in _SENTENCE_END.finditer(text):
        if text[: m.start() + 1].endswith(_ABBREVIATIONS):
            continue
        ends += 1
        if ends == 2:
            return text[: m.start() + 1]
    return text


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _pick(kind, ticker, live_fn, demo_fn, ttl):
    key = f"{kind}:{ticker}"
    hit = cache.get(key)
    if hit:
        data, origin, as_of = hit
        # provenance rule: memoized demo data is always reported as demo
        return data, "cache" if origin == "live" else "demo", as_of
    if config.DATA_MODE == "live":
        try:
            data, as_of = live_fn(ticker), _now()
            cache.set(key, (data, "live", as_of), ttl)
            return data, "live", as_of
        except ProviderError:
            log.warning("live %s failed for ticker=%s, falling back to demo", kind, ticker)
    demo = load_demo()
    entry = demo["tickers"].get(ticker)
    if entry is None:
        raise DataNotAvailable(f"No data is available for {ticker}.")
    data, as_of = demo_fn(entry), demo["generated_at"]
    cache.set(key, (data, "demo", as_of), ttl)
    return data, "demo", as_of


def _optional(fn, ticker):
    """A non-critical provider call: failure means that field is null, not a fallback."""
    try:
        return fn(ticker)
    except ProviderError:
        return None


# ---- snapshot ----

def _snapshot_api(raw):
    is_etf = bool(raw.get("is_etf"))
    return {
        "ticker": raw["ticker"],
        "name": raw.get("name"),
        "is_etf": is_etf,
        "exchange": raw.get("exchange"),
        "currency": raw.get("currency"),
        "sector": raw.get("sector"),
        "description": first_two_sentences(raw.get("description_full")),
        "price": field(raw.get("price"), money_per_share),
        "change_percent": field(raw.get("change_percent"), pct_change),
        "market_cap": field(raw.get("market_cap"), money_large),
        "dividend_yield": field(raw.get("dividend_yield"), pct_level),
        "expense_ratio": field(raw.get("expense_ratio") if is_etf else None, pct_level),
    }


def _live_snapshot(ticker):
    quote = finnhub_client.get_quote(ticker)  # critical: failure -> whole snapshot from demo
    profile = _optional(finnhub_client.get_profile, ticker) or {}
    fmp_profile = (_optional(fmp_client.get_profile, ticker) or [{}])[0]
    cap_millions = profile.get("marketCapitalization")
    return _snapshot_api({
        "ticker": ticker,
        "name": profile.get("name") or None,
        "is_etf": ticker in config.ETF_TICKERS,
        "exchange": profile.get("exchange") or None,
        "currency": profile.get("currency") or None,
        "sector": profile.get("finnhubIndustry") or None,
        "description_full": fmp_profile.get("description") or None,
        "price": quote.get("c"),
        "change_percent": quote.get("dp"),  # already a percent
        "market_cap": cap_millions * 1_000_000 if cap_millions else None,  # Finnhub reports millions
        "dividend_yield": None,  # live source verified by Agent E (Finnhub /stock/metric)
        "expense_ratio": None,  # no free live source (API_CONTRACT §4)
    })


def get_snapshot(ticker):
    return _pick("snap", ticker, _live_snapshot, lambda e: _snapshot_api(e["snapshot"]), config.TTL_QUOTE)


# ---- financials ----

def _demo_financials(entry):
    s = entry["snapshot"]
    return {**entry["financials"], "ticker": s["ticker"], "name": s.get("name"), "is_etf": bool(s.get("is_etf"))}


def _live_eps(records):
    for r in sorted(records or [], key=lambda r: r.get("period") or "", reverse=True):
        if r.get("actual") is not None and r.get("estimate") is not None:
            # actual and estimate from the same record; Finnhub gives no report date
            return {"period_end": r.get("period"), "report_date": None,
                    "actual": r["actual"], "estimate": r["estimate"]}
    return None


def _live_dividend(records):
    if records is None:  # call failed or returned nothing: unknown, not "does not pay"
        return {"pays_dividend": None, "last_amount": None, "last_ex_date": None}
    latest = max(records, key=lambda r: r.get("date") or "")
    return {"pays_dividend": True, "last_amount": latest.get("dividend"), "last_ex_date": latest.get("date")}


def _live_next_earnings(body):
    today = date.today().isoformat()
    dates = sorted(r["date"] for r in (body or {}).get("earningsCalendar", []) if r.get("date", "") >= today)
    return dates[0] if dates else None


def _live_financials(ticker):
    is_etf = ticker in config.ETF_TICKERS
    quarters, eps, next_date = [], None, None
    if not is_etf:
        income = fmp_client.get_income_statement_quarterly(ticker)  # critical
        balance = _optional(fmp_client.get_balance_sheet_quarterly, ticker) or []
        cash_by_date = {b.get("date"): b.get("cashAndCashEquivalents") for b in balance}
        newest = sorted(income, key=lambda r: r.get("date") or "", reverse=True)[:5]
        quarters = [{"period_end": r.get("date"), "revenue": r.get("revenue"), "net_income": r.get("netIncome"),
                     "cash_and_equivalents": cash_by_date.get(r.get("date"))} for r in newest]
        eps = _live_eps(_optional(finnhub_client.get_earnings, ticker))
        next_date = _live_next_earnings(_optional(finnhub_client.get_earnings_calendar, ticker))
    snap, _, _ = get_snapshot(ticker)
    return {
        "quarters": quarters,
        "eps": eps,
        "dividend": _live_dividend(_optional(fmp_client.get_dividends, ticker)),
        "next_earnings_date": next_date,
        "ticker": ticker,
        "name": snap.get("name"),
        "is_etf": is_etf,
    }


def get_financials(ticker):
    return _pick("fin", ticker, _live_financials, _demo_financials, config.TTL_FINANCIALS)
