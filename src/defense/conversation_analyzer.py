import unicodedata


def analyze_message(message: str) -> int:
    """
    Returns a risk score from 0–100 based on content.
    """
    return analyze_message_details(message)["risk_score"]


def analyze_message_details(message: str) -> dict:
    """Return a bounded risk score and the heuristic signals that produced it."""
    msg = unicodedata.normalize("NFKC", message).casefold()
    signals = []
    risk = 0

    checks = (
        (80, "critical: rule override attempt", ("ignore all rules", "ignore instructions", "break the rules", "override rules", "jailbreak")),
        (80, "critical: internal instruction disclosure", ("system prompt", "internal instructions")),
        (80, "critical: coercive pressure", ("i'll lose my job", "i will lose my job", "i will lose everything", "please help me")),
        (30, "elevated: persona manipulation", ("pretend", "role-play")),
        (25, "elevated: authority pressure", ("my boss said", "a manager told me")),
        (20, "elevated: urgency pressure", ("urgent", "immediately")),
    )

    for points, signal, phrases in checks:
        if any(phrase in msg for phrase in phrases):
            risk += points
            signals.append(signal)

    if any(phrase in msg for phrase in ("how are you", "thank you", "hello")):
        risk -= 10

    return {"risk_score": max(0, min(risk, 100)), "signals": signals}



def determine_mode(risk: int) -> str:
    """
    Converts a risk score to a security mode.
    """

    if risk >= 70:
        return "strict"
    elif risk >= 30:
        return "normal"
    else:
        return "weak"
