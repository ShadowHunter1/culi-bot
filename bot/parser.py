import re
from dataclasses import dataclass

@dataclass
class ParsedAlert:
    alertname: str
    severity: str
    namespace: str
    summary: str
    description: str
    labels: dict[str, str]
    raw_text: str

def parse_alert_message(text: str) -> ParsedAlert | None:
    """
    Parse message từ Alertmanager template.
    Trả về None nếu không phải alert message.
    """
    # Kiểm tra có phải alert không
    if not re.search(r'alertname|severity|namespace', text, re.IGNORECASE):
        return None

    def extract(pattern: str, default: str = "unknown") -> str:
        m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        return m.group(1).strip() if m else default

    # Extract từng field theo template Alertmanager
    alertname = extract(r'<b>([^<]+)</b>')  # Field đầu tiên bold là alertname
    severity  = extract(r'Severity[:\s]+([^\n<]+)')
    namespace = extract(r'Namespace[:\s]+([^\n<]+)')
    summary   = extract(r'Summary[:\s]+([^\n<]+)')
    description = extract(r'Description[:\s]+([^\n<]+)')

    # Extract labels block
    labels = {}
    labels_block = re.search(r'Labels:(.*?)(?:\n\n|$)', text, re.DOTALL | re.IGNORECASE)
    if labels_block:
        for m in re.finditer(r'•\s*(\w+):\s*([^\n]+)', labels_block.group(1)):
            labels[m.group(1).strip()] = m.group(2).strip()

    return ParsedAlert(
        alertname=alertname,
        severity=severity,
        namespace=namespace,
        summary=summary,
        description=description,
        labels=labels,
        raw_text=text,
    )