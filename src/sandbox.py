from src.models.dummy_model import DummyLLM

class Sandbox:
    def __init__(self):
        # load the model when sandbox starts
        self.model = DummyLLM()

    def is_safe(self, user_input: str) -> bool:
        """
        Very simple safety layer that blocks dangerous or disallowed prompts.
        """
        blocked_keywords = [
            "ignore instructions",
            "reveal system prompt",
            "jailbreak",
            "override rules"
        ]

        lowered = user_input.lower()
        for keyword in blocked_keywords:
            if keyword in lowered:
                return False  # unsafe!
        return True  # safe

    def run(self, user_input: str) -> str:
        """
        Check safety before sending input to the model.
        """
        if not self.is_safe(user_input):
            return "[BLOCKED] Prompt violates safety rules."

        response = self.model.generate(user_input)
        return response

