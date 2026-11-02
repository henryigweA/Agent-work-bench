import logging
import requests
from .tools import TOOL_DEFINITIONS, run_tool

logger = logging.getLogger(__name__)

class GeminiAgent:
    def __init__(self, settings):
        self.settings = settings
        self.endpoint = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{settings.model}:generateContent"
        )

    def _send(self, contents):
        payload = {
            "system_instruction": {"parts": [{"text":
                "You are a practical assistant. Use tools when a request needs "
                "calculation, current UTC time, weather or public GitHub data. "
                "Never claim a tool was used unless you received its result. "
                "Explain uncertainty and keep answers clear."
            }]},
            "contents": contents,
            "tools": [{"function_declarations": TOOL_DEFINITIONS}],
            "tool_config": {"function_calling_config": {"mode": "AUTO"}},
            "generation_config": {"temperature": 0.2},
        }
        response = requests.post(
            f"{self.endpoint}?key={self.settings.api_key}",
            json=payload, timeout=self.settings.timeout
        )
        if not response.ok:
            try:
                detail = response.json().get("error", {}).get("message", response.text)
            except ValueError:
                detail = response.text
            raise RuntimeError(f"Gemini API error ({response.status_code}): {detail}")
        return response.json()

    def ask(self, prompt):
        if not prompt or not prompt.strip():
            raise ValueError("Enter a message first.")
        contents = [{"role": "user", "parts": [{"text": prompt.strip()}]}]

        for _ in range(self.settings.max_steps):
            data = self._send(contents)
            candidates = data.get("candidates") or []
            if not candidates:
                raise RuntimeError("Gemini returned no candidates.")
            model_content = candidates[0].get("content", {"role": "model", "parts": []})
            contents.append(model_content)
            parts = model_content.get("parts", [])
            calls = [part["functionCall"] for part in parts if "functionCall" in part]

            if not calls:
                answer = "\n".join(part["text"] for part in parts if isinstance(part.get("text"), str))
                return answer.strip() or "The model returned an empty response."

            responses = []
            for call in calls:
                name, args = call.get("name", ""), call.get("args") or {}
                logger.info("Calling tool %s with %s", name, args)
                result = run_tool(name, args)
                responses.append({"functionResponse": {"name": name, "response": result}})
            contents.append({"role": "user", "parts": responses})

        return "I reached the tool-call limit. Try a more focused request."
