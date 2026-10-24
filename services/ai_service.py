# Owner: Agent C. W0 created this stub.
from services.errors import AIUnavailable


def explain_earnings(facts: dict, profile: dict) -> tuple[dict, str]:
    if facts.get("is_etf"):
        return {"etf": None, "questions": []}, "fallback"
    return {
        "headline": None,
        "revenue": None,
        "profit": None,
        "eps": None,
        "cash": None,
        "dividend": None,
        "questions": [],
    }, "fallback"


def chat(message: str, history: list, profile: dict, context_facts: dict | None) -> str:
    raise AIUnavailable("Chat is not built yet.")
