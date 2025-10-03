# validator.py
from typing import Dict
from config import settings
from urllib.parse import urlparse

def basic_validator(record: Dict) -> Dict:
    url = record.get("final_url") or record.get("url")
    parsed = urlparse(url) if url else None
    problems = []
    if not url:
        problems.append("NO_URL")
    if parsed:
        hostname = parsed.hostname or ""
        if hostname.endswith(".ru") or hostname.endswith(".xyz"):
            problems.append("SUSPICIOUS_TLD")
    # status code issues
    code = record.get("status_code")
    if code and (code >= 400):
        problems.append(f"STATUS_{code}")
    return {"ok": record.get("ok") and (len(problems) == 0), "problems": problems}
