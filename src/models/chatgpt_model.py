from openai import OpenAI
import os


class ChatGPTLLM:
    """
    Live ChatGPT model accessed via OpenAI API (new SDK format)
    """

    def __init__(self, model="gpt-4.1-mini"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model

        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY not found in environment variables.")

    def generate(self, user_input: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a safe and helpful AI."},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.2,
                max_tokens=120
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"[OpenAI API ERROR] {str(e)}"

