import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    api_key: str
    model: str
    max_steps: int
    timeout: int

    @classmethod
    def from_env(cls):
        key = os.getenv("GEMINI_API_KEY", "").strip()
        if not key or key == "your_gemini_api_key_here":
            raise RuntimeError("GEMINI_API_KEY is missing. Copy .env.example to .env and add your Google AI Studio key.")
        return cls(
            api_key=key,
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip(),
            max_steps=max(1, int(os.getenv("AGENT_MAX_STEPS", "6"))),
            timeout=max(5, int(os.getenv("HTTP_TIMEOUT", "20"))),
        )
