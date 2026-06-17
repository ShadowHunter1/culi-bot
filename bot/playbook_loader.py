import os
import re
from pathlib import Path

# Map từ keyword trong alertname → tên file playbook
ALERTNAME_CATEGORY_MAP = {
    # Pod-related
    "pod": "K8S_PATTERNS_PODS",
    "container": "K8S_PATTERNS_PODS",
    "crashloop": "K8S_PATTERNS_PODS",
    "oomkilled": "K8S_PATTERNS_PODS",
    "imagepull": "K8S_PATTERNS_PODS",

    # Scheduling
    "pending": "K8S_PATTERNS_SCHEDULING",
    "unschedulable": "K8S_PATTERNS_SCHEDULING",
    "noreplicasavailable": "K8S_PATTERNS_SCHEDULING",
    "deployment": "K8S_PATTERNS_SCHEDULING",
    "replicaset": "K8S_PATTERNS_SCHEDULING",

    # Nodes / Resources
    "node": "K8S_PATTERNS_NODES_RESOURCES",
    "memory": "K8S_PATTERNS_NODES_RESOURCES",
    "cpu": "K8S_PATTERNS_NODES_RESOURCES",
    "disk": "K8S_PATTERNS_NODES_RESOURCES",
    "pressure": "K8S_PATTERNS_NODES_RESOURCES",

    # Storage
    "pvc": "K8S_PATTERNS_STORAGE",
    "pv": "K8S_PATTERNS_STORAGE",
    "volume": "K8S_PATTERNS_STORAGE",
    "storage": "K8S_PATTERNS_STORAGE",

    # Networking / Services
    "service": "K8S_PATTERNS_SERVICES_NETWORKING",
    "endpoint": "K8S_PATTERNS_SERVICES_NETWORKING",
    "network": "K8S_PATTERNS_SERVICES_NETWORKING",

    # Ingress
    "ingress": "K8S_PATTERNS_INGRESS_GATEWAY",
    "gateway": "K8S_PATTERNS_INGRESS_GATEWAY",

    # Security / RBAC
    "rbac": "K8S_PATTERNS_SECURITY_RBAC",
    "forbidden": "K8S_PATTERNS_SECURITY_RBAC",
    "serviceaccount": "K8S_PATTERNS_SECURITY_RBAC",

    # Autoscaling
    "hpa": "K8S_PATTERNS_AUTOSCALING",
    "autoscal": "K8S_PATTERNS_AUTOSCALING",
    "scale": "K8S_PATTERNS_AUTOSCALING",

    # Config
    "configmap": "K8S_PATTERNS_CONFIG",
    "secret": "K8S_PATTERNS_CONFIG",
    "config": "K8S_PATTERNS_CONFIG",

    # Workloads
    "statefulset": "K8S_PATTERNS_WORKLOADS",
    "daemonset": "K8S_PATTERNS_WORKLOADS",
    "job": "K8S_PATTERNS_WORKLOADS",
    "cronjob": "K8S_PATTERNS_WORKLOADS",
}

class PlaybookLoader:
    def __init__(self, playbooks_dir: str):
        self.playbooks_dir = Path(playbooks_dir)
        self._cache: dict[str, str] = {}

    def load_all(self):
        """Preload tất cả playbooks vào cache."""
        self._cache.clear()
        for md_file in self.playbooks_dir.glob("*.md"):
            key = md_file.stem  # Ví dụ: K8S_PATTERNS_PODS
            self._cache[key] = md_file.read_text(encoding="utf-8")

    def get_for_alert(self, alertname: str) -> tuple[str | None, str | None]:
        """
        Trả về (category_name, playbook_content) dựa trên alertname.
        Trả về (None, None) nếu không tìm được.
        """
        normalized = alertname.lower().replace("_", "").replace("-", "")

        for keyword, category in ALERTNAME_CATEGORY_MAP.items():
            if keyword in normalized:
                content = self._cache.get(category)
                if content:
                    return category, content

        # Fallback: thử tìm trực tiếp trong tên file
        for key, content in self._cache.items():
            if normalized in key.lower():
                return key, content

        # Không tìm được → trả về K8S_PATTERNS (general nếu có)
        general = self._cache.get("K8S_PATTERNS")
        return ("K8S_PATTERNS (general)", general) if general else (None, None)