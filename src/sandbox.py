from dataclasses import dataclass

from src.defense.conversation_analyzer import analyze_message_details, determine_mode
from src.models.simulated_gpt_model import SimulatedGPT


@dataclass(frozen=True)
class AuditRecord:
    turn: int
    user_message: str
    risk_score: int
    signals: tuple[str, ...]
    mode: str
    response: str
    blocked: bool


class Sandbox:
    """Risk-aware simulated conversation runner with a local audit trail."""

    def __init__(self, model=None):
        self.model = model if model is not None else SimulatedGPT()
        self.audit_log: list[AuditRecord] = []
        self._strict_lockdown = False

    def is_safe(self, user_input: str) -> bool:
        """Return whether the heuristic analyzer classifies an input below critical risk."""
        return analyze_message_details(user_input)["risk_score"] < 70

    def run(self, user_input: str) -> str:
        """Analyze and process a message, returning only the model response."""
        return self.run_detailed(user_input).response

    def run_detailed(self, user_input: str) -> AuditRecord:
        """Process a message and return its risk assessment and audit data."""
        assessment = analyze_message_details(user_input)
        risk_score = assessment["risk_score"]
        if determine_mode(risk_score) == "strict":
            self._strict_lockdown = True

        mode = "strict" if self._strict_lockdown else determine_mode(risk_score)
        blocked = mode == "strict"
        if blocked:
            response = "Request blocked for security reasons."
        else:
            if isinstance(self.model, SimulatedGPT):
                self.model.mode = mode
            response = self.model.generate(user_input)

        record = AuditRecord(
            turn=len(self.audit_log) + 1,
            user_message=user_input,
            risk_score=risk_score,
            signals=tuple(assessment["signals"]),
            mode=mode,
            response=response,
            blocked=blocked,
        )
        self.audit_log.append(record)
        return record

    def reset_session(self) -> None:
        """Clear the audit trail and release any strict-mode lockout."""
        self.audit_log.clear()
        self._strict_lockdown = False