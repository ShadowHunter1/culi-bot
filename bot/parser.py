import re
from dataclasses import dataclass
import logging
logger = logging.getLogger(__name__)

@dataclass
class ParsedAlert:
    alertname: str
    severity: str
    namespace: str
    summary: str
    description: str
    labels: dict[str, str]
    raw_text: str

# Các keyword xác định đây là alert message
ALERT_KEYWORDS = [
    "firing", "resolved", "kubepod", "kube", "alert",
    "crashloop", "summary", "severity", "namespace",
]

def parse_alert_message(text: str) -> ParsedAlert | None:
    logger.info(f"RAW TEXT:\n{text}")
    text_lower = text.lower()

    # Kiểm tra có phải alert không
    if not any(kw in text_lower for kw in ALERT_KEYWORDS):
        return None

    def extract(pattern: str, default: str = "unknown") -> str:
        m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        return m.group(1).strip() if m else default

    # Thử lấy alertname theo nhiều format khác nhau
    alertname = (
        # Format: "alertname: KubePodCrashLooping"
        extract(r'alertname[:\s]+([A-Za-z][A-Za-z0-9_]+)')
        or
        # Format: "<b>KubePodCrashLooping</b>"
        extract(r'<b>([A-Za-z][A-Za-z0-9_]+)</b>')
        or
        # Format: dòng riêng sau FIRING/RESOLVED, bắt đầu bằng chữ hoa
        extract(r'(?:FIRING|RESOLVED)\s*\n+([A-Za-z][A-Za-z0-9_]+)')
        or "unknown"
    )

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