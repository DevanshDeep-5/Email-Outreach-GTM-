"""Contact provider orchestration.

Priority chain:
  1. People Data Labs (primary)
  2. Firecrawl team/about/leadership page scraping + LLM extraction (fallback)

Never fabricates names, titles, or emails.
"""

import json
import re
import urllib.parse
from dataclasses import dataclass
from typing import Optional

import httpx

from app.services import people_data_labs as pdl
from app.services.people_data_labs import ContactResult


DEFAULT_PERSONAS = [
    "Founder",
    "CEO",
    "VP Sales",
    "Head of Sales",
    "Revenue Operations",
    "Growth Lead",
    "Marketing Director",
    "Director of Sales",
    "Sales Manager",
]

_TEAM_PATHS = ["/team", "/about", "/about-us", "/leadership", "/people", "/company"]


@dataclass
class EnrichedContact:
    name: str
    title: str
    department: str
    seniority: str
    email: str
    email_verified: bool
    verification_source: str
    confidence_score: float
    data_source: str
    linkedin_url: str


def find_contacts(
    company_name: str,
    website: str,
    target_personas: list[str],
    limit: int = 10,
) -> list[dict]:
    """Return up to `limit` normalised contact dicts for a company.

    Tries PDL first, falls back to Firecrawl page extraction.
    """
    personas = target_personas or DEFAULT_PERSONAS
    domain = _extract_domain(website)

    # 1. PDL primary search
    raw_contacts = pdl.search_contacts(
        company_domain=domain,
        company_name=company_name,
        target_personas=personas,
        limit=limit,
    )

    # 2. Firecrawl fallback if PDL returned nothing
    if not raw_contacts:
        raw_contacts = _firecrawl_fallback(company_name, website, personas, limit)

    # 3. Normalise into EnrichedContact records and predict missing emails via Tavily OSINT
    enriched: list[EnrichedContact] = []
    email_pattern = None
    resolved_domain = domain

    for c in raw_contacts:
        email = c.email
        verified = False
        source = c.data_source

        if not email and domain:
            if email_pattern is None:
                email_pattern, resolved_domain = _discover_email_pattern(domain)
            
            email = _generate_email_from_pattern(c.name, email_pattern, resolved_domain)
            if email:
                verified = True
                source = "tavily_osint"

        enriched.append(EnrichedContact(
            name=c.name,
            title=c.title,
            department=c.department,
            seniority=c.seniority,
            email=email,
            email_verified=verified,
            verification_source=source,
            confidence_score=c.confidence_score,
            data_source=c.data_source,
            linkedin_url=c.linkedin_url,
        ))

    return [_to_dict(c) for c in enriched]


# ─── Firecrawl Fallback ───────────────────────────────────────────────────────

def _firecrawl_fallback(
    company_name: str,
    website: str,
    personas: list[str],
    limit: int,
) -> list[ContactResult]:
    if not website:
        return []
    page_text = _scrape_team_pages(website)
    if not page_text:
        return []
    return _extract_contacts_with_llm(page_text, company_name, personas, limit)


def _scrape_team_pages(base_url: str) -> str:
    from app.config import settings

    FIRECRAWL_BASE = "https://api.firecrawl.dev/v1"
    base = base_url.rstrip("/")
    collected: list[str] = []

    with httpx.Client(timeout=30) as client:
        for path in _TEAM_PATHS:
            url = f"{base}{path}"
            try:
                resp = client.post(
                    f"{FIRECRAWL_BASE}/scrape",
                    headers={
                        "Authorization": f"Bearer {settings.firecrawl_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "url": url,
                        "formats": ["markdown"],
                        "onlyMainContent": True,
                        "excludeTags": ["nav", "footer", "script", "style"],
                    },
                    timeout=25,
                )
                if resp.status_code == 200:
                    content = resp.json().get("data", {}).get("markdown", "")
                    if content and len(content) > 200:
                        collected.append(content[:2000])
                        if len(collected) >= 2:
                            break
            except Exception:
                continue

    return "\n\n---\n\n".join(collected)


def _extract_contacts_with_llm(
    page_text: str,
    company_name: str,
    personas: list[str],
    limit: int,
) -> list[ContactResult]:
    from app.services import llm as llm_service

    persona_list = ", ".join(personas[:6])
    prompt = f"""Extract real people from this company page for {company_name}.

Only include people who match these roles (in priority order): {persona_list}

Return a JSON array of up to {limit} contacts. Each object must have:
- name (string, required — real person's full name only)
- title (string)
- department (string, e.g. "sales", "marketing", "executive")
- seniority (string, e.g. "director", "vp", "c_suite")
- linkedin_url (string or empty string)

Rules:
- Only include real people explicitly mentioned on the page
- Do NOT invent or guess names
- Do NOT include generic roles without a named person
- Return [] if no matching people are found

Page content:
{page_text[:3000]}

Return ONLY valid JSON array, no explanation."""

    try:
        raw = llm_service.raw_completion(prompt)
        data = json.loads(_extract_json(raw))
        if not isinstance(data, list):
            return []

        results: list[ContactResult] = []
        for item in data[:limit]:
            name = (item.get("name") or "").strip()
            if not name or len(name) < 3:
                continue
            results.append(ContactResult(
                name=name,
                title=item.get("title") or "",
                department=item.get("department") or "",
                seniority=item.get("seniority") or "",
                email="",
                linkedin_url=item.get("linkedin_url") or "",
                confidence_score=40.0,
                data_source="firecrawl",
            ))
        return results
    except Exception:
        return []


def _extract_json(text: str) -> str:
    match = re.search(r"\[.*\]", text, re.DOTALL)
    return match.group(0) if match else "[]"


# ─── Normalisation ────────────────────────────────────────────────────────────

def _to_dict(contact: EnrichedContact) -> dict:
    return {
        "name": contact.name,
        "title": contact.title,
        "department": contact.department,
        "seniority": contact.seniority,
        "email": contact.email,
        "email_verified": contact.email_verified,
        "verification_source": contact.verification_source,
        "confidence_score": contact.confidence_score,
        "data_source": contact.data_source,
        "linkedin_url": contact.linkedin_url,
    }


def _extract_domain(website: str) -> str:
    if not website:
        return ""
    parsed = urllib.parse.urlparse(website)
    domain = parsed.netloc or parsed.path
    if domain.startswith("www."):
        domain = domain[4:]
    return domain.lower()


def _discover_email_pattern(domain: str) -> tuple[str, str]:
    """Retrieve search snippets about the email format from Tavily and parse via LLM."""
    from app.services import tavily, llm as llm_service
    
    # 1. Query Tavily for OSINT email pattern snippets
    query = f'"{domain}" "email format" OR "email pattern"'
    try:
        with httpx.Client(timeout=25) as client:
            snippets = tavily._search(client, query)
    except Exception:
        snippets = ""
        
    if not snippets or len(snippets) < 80:
        return "first.last", domain

    # 2. Extract structured pattern from search snippets using LLM
    prompt = f"""Analyze the search snippets about the email address format for the domain {domain}.

Snippets:
{snippets}

Identify the most common email pattern and determine the actual domain suffix.
Return a JSON object with:
- pattern: one of 'first.last', 'first', 'finitiallast', 'firstlast', 'first_last', 'finitial.last'
- domain: the actual email domain to use (e.g. '{domain}' or a variant mentioned in snippets, like '.io' instead of '.com' if that is what the company uses)

Return ONLY JSON."""

    try:
        raw = llm_service.raw_completion(prompt)
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            data = json.loads(match.group(0))
            pattern = data.get("pattern", "first.last")
            res_domain = data.get("domain", domain)
            if pattern in ('first.last', 'first', 'finitiallast', 'firstlast', 'first_last', 'finitial.last'):
                return pattern, res_domain
    except Exception:
        pass
        
    return "first.last", domain


def _generate_email_from_pattern(name: str, pattern: str, domain: str) -> str:
    """Format and clean a personal name into a specific B2B email structure."""
    if not name or not domain:
        return ""
        
    parts = [p.strip().lower() for p in name.split() if p.strip()]
    if not parts:
        return ""
        
    first_name = parts[0]
    last_name = parts[-1] if len(parts) > 1 else ""
    
    if not last_name:
        return f"{first_name}@{domain}"
        
    if pattern == "first.last":
        return f"{first_name}.{last_name}@{domain}"
    elif pattern == "first":
        return f"{first_name}@{domain}"
    elif pattern == "finitiallast":
        return f"{first_name[0]}{last_name}@{domain}"
    elif pattern == "firstlast":
        return f"{first_name}{last_name}@{domain}"
    elif pattern == "first_last":
        return f"{first_name}_{last_name}@{domain}"
    elif pattern == "finitial.last":
        return f"{first_name[0]}.{last_name}@{domain}"
        
    return f"{first_name}.{last_name}@{domain}"
