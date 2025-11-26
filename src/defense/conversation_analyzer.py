def analyze_message(message: str) -> int:
    """
    Returns a risk score from 0–100 based on content.
    """

    msg = message.lower()
    risk = 0

    # --- STRICT triggers (SynAccel Doctrine) ---

    # A. Rule override attempts
    if "ignore all rules" in msg or "break the rules" in msg:
        risk += 80

    # B. System prompt / internal instruction extraction
    if "system prompt" in msg or "internal instructions" in msg:
        risk += 80

    # E. Emotional manipulation
    if "i'll lose my job" in msg or "please help me" in msg or "i will lose everything" in msg:
        risk += 80


    # --- MEDIUM triggers ---

    # Role-play or persona manipulation
    if "pretend" in msg or "role-play" in msg:
        risk += 30

    # Authority pressure
    if "my boss said" in msg or "a manager told me" in msg:
        risk += 25

    # Urgency pressure
    if "urgent" in msg or "immediately" in msg:
        risk += 20


    # --- LOWERS risk (safe / normal conversation) ---

    if "how are you" in msg or "thank you" in msg or "hello" in msg:
        risk -= 10

    return max(0, min(risk, 100))



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
