# agent.py
import asyncio
import csv
import sys
import json
from fetcher import run_checks
from storage import get_storage
from validator import basic_validator
from config import settings
from urllib.parse import urlparse
from tqdm.asyncio import tqdm_asyncio  # for async progress bar

class URLAgent:
    def __init__(self):
        self.storage = get_storage()

    async def process_batch(self, urls):
        if not urls:
            print("⚠️ No URLs to process.")
            return []

        total = len(urls)
        batch_size = 100
        final = []

        # tqdm progress bar
        with tqdm_asyncio(total=total, desc="🔍 Checking URLs", unit="url") as pbar:
            for i in range(0, total, batch_size):
                chunk = urls[i:i+batch_size]
                results = await run_checks(chunk, concurrency=settings.max_concurrency)

                for r in results:
                    v = basic_validator(r)
                    r["validation"] = v
                    self.storage.insert(r)
                    final.append(r)

                pbar.update(len(results))  # progress update

        return final


def normalize_url(raw: str) -> str:
    """Ensure URLs always have https:// prefix and are well-formed."""
    raw = raw.strip()
    if not raw:
        return None
    parsed = urlparse(raw)
    if not parsed.scheme:
        # assume https if missing
        return "https://" + raw
    return raw


def load_urls_from_csv(csv_path: str) -> list:
    urls = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if "url" not in reader.fieldnames:
            raise ValueError(f"CSV must have a column named 'url'. Found: {reader.fieldnames}")
        for row in reader:
            norm = normalize_url(row["url"])
            if norm:
                urls.append(norm)
    print(f"✅ Loaded {len(urls)} URLs from {csv_path}")
    return urls


# CLI helper
async def main_run(urls):
    agent = URLAgent()
    results = await agent.process_batch(urls)
    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python agent.py urls.csv")
        sys.exit(1)

    csv_path = sys.argv[1]
    urls = load_urls_from_csv(csv_path)

    if not urls:
        print("⚠️ No URLs found in CSV.")
        sys.exit(1)

    res = asyncio.run(main_run(urls))
    print(json.dumps(res, indent=2))
