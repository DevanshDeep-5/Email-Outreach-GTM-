"""Tavily API client — web research for company signals."""

import httpx

from app.config import settings

TAVILY_BASE = "https://api.tavily.com"


def research_company(company_name: str, website: str) -> dict:
    """Run multiple Tavily searches to gather company signals."""
    queries = [
        f"{company_name} recent funding round 2024 2025",
        f"{company_name} hiring sales team expansion",
        f"{company_name} recent news announcements product launch",
        f"{company_name} leadership team CEO founder",
    ]

    results: list[str] = []

    with httpx.Client(timeout=30) as client:
        for query in queries:
            try:
                snippet = _search(client, query)
                if snippet:
                    results.append(snippet)
            except Exception:
                continue

    return {
        "tavily_summary": "\n\n".join(results),
        "recent_news": results[2] if len(results) > 2 else "",
    }


def _search(client: httpx.Client, query: str) -> str:
    payload = {
        "api_key": settings.tavily_api_key,
        "query": query,
        "search_depth": "basic",
        "max_results": 3,
        "include_answer": True,
    }

    resp = client.post(f"{TAVILY_BASE}/search", json=payload, timeout=20)
    if resp.status_code != 200:
        return ""

    data = resp.json()
    answer = data.get("answer", "")
    results = data.get("results", [])

    parts = []
    if answer:
        parts.append(f"Summary: {answer}")
    for r in results[:2]:
        content = r.get("content", "")
        if content:
            parts.append(content[:500])

    return "\n".join(parts)
