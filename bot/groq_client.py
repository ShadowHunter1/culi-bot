from pathlib import Path
from groq import AsyncGroq

SYSTEM_PROMPT_PATH = Path("playbooks/AI_PROMPT_SPEC.md")

class GroqClient:
    def __init__(self, api_key: str, model: str):
        self.model = model
        self.system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
        self.client = AsyncGroq(api_key=api_key)

    async def analyze_alert(
        self,
        alert_text: str,
        playbook_content: str | None,
        category_name: str | None,
    ) -> str:
        user_parts = ["## Alert nhận được\n", alert_text]

        if playbook_content:
            user_parts += [
                f"\n\n## Playbook nội bộ: {category_name}\n",
                playbook_content,
            ]
        else:
            user_parts.append(
                "\n\n## Playbook\nKhông tìm thấy playbook phù hợp. "
                "Sử dụng kiến thức nền Kubernetes."
            )

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user",   "content": "\n".join(user_parts)},
            ],
            max_tokens=2048,
            temperature=0.2,
        )
        return response.choices[0].message.content