"""Firecrawl API client — website scraping."""

import httpx
from typing import Optional

from app.config import settings

FIRECRAWL_BASE = "https://api.firecrawl.dev/v1"

TARGET_PATHS = ["/", "/about", "/pricing", "/features", "/customers", "/products"]


def scrape_website(url: str) -> str:
    """Scrape a company website and return cleaned text content."""
    if not url:
        return ""

    base = url.rstrip("/")
    collected: list[str] = []

    with httpx.Client(timeout=45) as client:
        for path in TARGET_PATHS:
            target = f"{base}{path}" if path != "/" else base
            try:
                result = _scrape_page(client, target)
                if result:
                    collected.append(result)
            except Exception:
                continue

    return "\n\n---\n\n".join(collected[:5])  # cap at 5 pages


def _scrape_page(client: httpx.Client, url: str) -> Optional[str]:
    payload = {
        "url": url,
        "formats": ["markdown"],
        "excludeTags": ["nav", "footer", "header", "script", "style", "cookie"],
        "onlyMainContent": True,
    }

    resp = client.post(
        f"{FIRECRAWL_BASE}/scrape",
        headers={
            "Authorization": f"Bearer {settings.firecrawl_api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=30,
    )

    if resp.status_code != 200:
        return None

    data = resp.json()
    content = data.get("data", {}).get("markdown", "")
    return content[:3000] if content else None  # truncate per page
