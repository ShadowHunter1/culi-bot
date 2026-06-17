import httpx
from pathlib import Path

SYSTEM_PROMPT_PATH = Path("playbooks/AI_PROMPT_SPEC.md")

class GrokClient:
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
        self.base_url = "https://api.x.ai/v1"

    async def analyze_alert(
        self,
        alert_text: str,
        playbook_content: str | None,
        category_name: str | None,
    ) -> str:
        """
        Gửi alert + playbook tới Grok, trả về phân tích.
        """
        # Build user message
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

        user_message = "\n".join(user_parts)

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user",   "content": user_message},
                    ],
                    "max_tokens": 2048,
                    "temperature": 0.2,  # Thấp để giảm sáng tạo, tăng chính xác
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]