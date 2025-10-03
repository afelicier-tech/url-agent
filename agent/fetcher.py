# fetcher.py
import asyncio
import aiohttp
import time
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from typing import Dict, Any
from config import settings

class URLChecker:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    async def check(self, url: str, max_redirects=10, timeout=None) -> Dict[str, Any]:
        timeout = timeout or settings.request_timeout_seconds
        start = time.time()
        try:
            async with self.session.get(url, allow_redirects=True, timeout=timeout) as resp:
                body = await resp.text()
                latency_ms = int((time.time() - start) * 1000)
                return {
                    "url": url,
                    "final_url": str(resp.url),
                    "status_code": resp.status,
                    "ok": 200 <= resp.status < 400,
                    "redirects_count": len(resp.history) if getattr(resp, "history", None) else 0,
                    "latency_ms": latency_ms,
                    "content_type": resp.headers.get("Content-Type"),
                    "headers": dict(resp.headers),
                    "body": body[:2000],
                    "error": None
                }
        except Exception as e:
            latency_ms = int((time.time() - start) * 1000)
            return {
                "url": url,
                "final_url": None,
                "status_code": None,
                "ok": False,
                "redirects_count": None,
                "latency_ms": latency_ms,
                "content_type": None,
                "headers": {},
                "body": None,
                "error": repr(e)
            }

# Pool-runner helper
async def run_checks(urls, concurrency=20):
    connector = aiohttp.TCPConnector(limit=concurrency, ssl=False)
    timeout = aiohttp.ClientTimeout(total=settings.request_timeout_seconds + 5)
    async with aiohttp.ClientSession(connector=connector, timeout=timeout, headers={"User-Agent": settings.user_agent}) as session:
        checker = URLChecker(session)
        sem = asyncio.Semaphore(concurrency)
        results = []

        async def _run(url):
            async with sem:
                # simple retry wrapper
                res = await checker.check(url)
                # if transient network errors, naive retry
                if res["error"] and ("Timeout" in res["error"] or "ClientConnectorError" in res["error"]):
                    # try one more time
                    res2 = await checker.check(url)
                    if res2["error"] is None:
                        return res2
                return res

        tasks = [asyncio.create_task(_run(u)) for u in urls]
        for t in asyncio.as_completed(tasks):
            r = await t
            results.append(r)
        return results
