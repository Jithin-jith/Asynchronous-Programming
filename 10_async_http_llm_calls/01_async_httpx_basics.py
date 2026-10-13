"""
===============================================================================
Module 10: Async HTTP Requests with httpx.AsyncClient
===============================================================================

CONCEPTS DEMONSTRATED:
1. `httpx.AsyncClient` context manager.
2. HTTP connection pooling and keep-alive.
3. Concurrent HTTP requests with `asyncio.gather()`.

HOW THIS CODE WORKS:
- `httpx.AsyncClient()` creates an asynchronous HTTP client.
- `async with` ensures connection pool is closed cleanly upon exit.
- 3 HTTP requests taking 1.0s latency each complete concurrently in ~1.0s total.
===============================================================================
"""

import asyncio
import time
import httpx

TARGET_URLS = [
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/1",
]


async def fetch_url(client: httpx.AsyncClient, url: str, request_id: int) -> int:
    """Sends an asynchronous HTTP GET request."""
    print(f"  [Req #{request_id}] Sending async GET request to {url}...")
    response = await client.get(url)
    print(f"  [Req #{request_id}] Received response code {response.status_code}")
    return response.status_code


async def main():
    print("=== Fetching 3 HTTP Endpoints Concurrently via httpx ===")
    start_time = time.perf_counter()
    
    # Reuse single AsyncClient for connection pooling & TCP keep-alive
    async with httpx.AsyncClient(timeout=10.0) as client:
        tasks = [fetch_url(client, url, idx + 1) for idx, url in enumerate(TARGET_URLS)]
        results = await asyncio.gather(*tasks)
        
    elapsed = time.perf_counter() - start_time
    print(f"\n[SUMMARY] All {len(results)} HTTP requests completed in {elapsed:.2f} seconds!")
    print(f"[SUMMARY] Response status codes: {results}")


if __name__ == "__main__":
    asyncio.run(main())
