"""People Data Labs API client.

Handles BOTH company search (replacing Apollo) and contact/people search.
"""

from dataclasses import dataclass
import time
from typing import Optional
import httpx

from app.config import settings

PDL_BASE = "https://api.peopledatalabs.com/v5"


# ─── Rate-Limit Aware POST Helper ─────────────────────────────────────────────

def _post_pdl(endpoint: str, payload: dict) -> dict:
    """Send a POST request to PDL with rate-limiting retry logic."""
    if not settings.people_data_labs_api_key:
        return {}

    headers = {
        "X-Api-Key": settings.people_data_labs_api_key,
        "Content-Type": "application/json",
    }
    
    url = f"{PDL_BASE}/{endpoint}"
    
    # Enforce a small delay between requests to be gentle on the free tier rate limit
    time.sleep(1.0)
    
    retries = 3
    delay = 1.5
    for attempt in range(retries):
        try:
            with httpx.Client(timeout=25) as client:
                resp = client.post(url, headers=headers, json=payload, timeout=25)
                if resp.status_code == 200:
                    return resp.json()
                elif resp.status_code == 429:
                    # Rate limited: sleep and retry
                    time.sleep(delay)
                    delay *= 2
                    continue
                elif resp.status_code == 402:
                    raise httpx.HTTPStatusError("People Data Labs API key is exhausted (402 Payment Required). Please check your PDL billing or credits.", request=resp.request, response=resp)
                elif resp.status_code == 404:
                    return {}
                else:
                    time.sleep(delay)
                    delay *= 2
                    continue
        except Exception as e:
            if isinstance(e, httpx.HTTPStatusError) and e.response.status_code == 402:
                raise e
            if attempt == retries - 1:
                raise e
            time.sleep(delay)
            delay *= 2
            
    return {}


# ─── Contact Search ──────────────────────────────────────────────────────────

@dataclass
class ContactResult:
    name: str
    title: str
    department: str
    seniority: str
    email: str
    linkedin_url: str
    confidence_score: float
    data_source: str = "people_data_labs"


def search_contacts(
    company_domain: str,
    company_name: str,
    target_personas: list[str],
    limit: int = 3,
) -> list[ContactResult]:
    """Search PDL for decision-maker contacts, prioritised by target_personas order."""
    results: list[ContactResult] = []

    for persona in target_personas:
        if len(results) >= limit:
            break

        query = _build_contact_query(company_domain, company_name, persona)
        data = _post_pdl("person/search", {"query": query, "size": 2, "dataset": "all"})
        
        for person in data.get("data", []):
            contact = _parse_person(person)
            if contact and not _already_found(contact.name, results):
                results.append(contact)
                if len(results) >= limit:
                    break

    return results


def _build_title_query(persona: str) -> dict:
    persona_lower = persona.lower().strip()
    
    abbreviations = {
        "ceo": ["ceo", "chief executive officer"],
        "cfo": ["cfo", "chief financial officer"],
        "cto": ["cto", "chief technology officer"],
        "cro": ["cro", "chief revenue officer"],
        "coo": ["coo", "chief operating officer"],
        "vp": ["vp", "vice president"],
        "vps": ["vp", "vice president"],
        "sdr": ["sdr", "sales development representative"],
        "bdr": ["bdr", "business development representative"],
        "founder": ["founder", "co-founder"]
    }
    
    words = [w for w in persona_lower.split() if w not in ("of", "and", "the", "a", "for", "in", "to", "at")]
    
    must_clauses = []
    for word in words:
        if word in abbreviations:
            phrase_clauses = []
            for phrase in abbreviations[word]:
                phrase_clauses.append({"wildcard": {"job_title": f"*{phrase}*"}})
            must_clauses.append({"bool": {"should": phrase_clauses}})
        else:
            must_clauses.append({"wildcard": {"job_title": f"*{word}*"}})
            
    if len(must_clauses) == 1:
        return must_clauses[0]
    elif len(must_clauses) > 1:
        return {"bool": {"must": must_clauses}}
    else:
        return {"wildcard": {"job_title": f"*{persona_lower}*"}}


def _build_contact_query(domain: str, company_name: str, persona: str) -> dict:
    """Build a PDL Elasticsearch query for a specific persona at a company."""
    title_clause = _build_title_query(persona)
    must: list[dict] = [title_clause]
    if domain:
        must.append({"term": {"job_company_website": domain.lower()}})
    else:
        must.append({"term": {"job_company_name": company_name.lower()}})
    return {"bool": {"must": must}}


def _parse_person(person: dict) -> Optional[ContactResult]:
    name = person.get("full_name") or ""
    if not name:
        return None

    # PDL free plan returns `emails` as boolean True/False instead of a list.
    # Only extract the address when we actually have a list of objects.
    emails_field = person.get("emails") or []
    email = ""
    if isinstance(emails_field, list) and emails_field:
        first = emails_field[0]
        if isinstance(first, dict):
            email = first.get("address", "")

    # PDL returns LinkedIn URLs without the https:// scheme on the free plan.
    raw_linkedin = person.get("linkedin_url") or ""
    linkedin_url = ""
    if raw_linkedin:
        linkedin_url = raw_linkedin if raw_linkedin.startswith("http") else f"https://www.{raw_linkedin}"

    levels = person.get("job_title_levels") or []
    seniority = levels[0] if levels else ""

    # PDL `likelihood` field (0-10); map to 0-100 confidence score.
    likelihood = person.get("likelihood") or 5
    try:
        confidence = round(float(likelihood) * 10, 1)
    except (TypeError, ValueError):
        confidence = 50.0

    return ContactResult(
        name=name,
        title=person.get("job_title") or "",
        department=person.get("job_title_role") or "",
        seniority=seniority,
        email=email,
        linkedin_url=linkedin_url,
        confidence_score=confidence,
        data_source="people_data_labs",
    )


def _already_found(name: str, results: list[ContactResult]) -> bool:
    return any(r.name.lower() == name.lower() for r in results)


# ─── Company Search ───────────────────────────────────────────────────────────

def _normalize_industry(industry: Optional[str]) -> list[dict]:
    if not industry:
        return []
    
    ind_lower = industry.lower().strip()
    
    # Taxonomy mapping with exact matching for keys to avoid substring match issues
    mappings = {
        ("software", "saas", "tech", "technology", "it", "software development", "software engineering"): [
            "computer software", "information technology and services", "internet"
        ],
        ("finance", "fintech", "banking", "payments", "capital", "financial services"): [
            "financial services", "banking", "capital markets"
        ],
        ("health", "healthcare", "medical", "clinical", "biotech", "hospital"): [
            "hospital & health care", "medical devices", "biotechnology", "pharmaceuticals"
        ],
        ("marketing", "advertising", "sales", "pr", "media", "adtech"): [
            "marketing and advertising", "public relations and communications", "media production"
        ],
        ("retail", "ecommerce", "e-commerce", "commerce", "shop", "fashion", "retailer"): [
            "retail", "consumer goods", "apparel & fashion"
        ],
        ("education", "edtech", "school", "university", "learning", "academic"): [
            "education management", "higher education", "e-learning"
        ]
    }
    
    matched_industries = []
    for keys, values in mappings.items():
        for k in keys:
            if k == ind_lower or f" {k} " in f" {ind_lower} " or ind_lower.startswith(f"{k} ") or ind_lower.endswith(f" {k}"):
                matched_industries.extend(values)
                break
        if matched_industries:
            break
            
    clauses = []
    if matched_industries:
        for ind in matched_industries:
            clauses.append({"term": {"industry": ind}})
    else:
        clauses.append({"term": {"industry": ind_lower}})
        clauses.append({"match": {"tags": ind_lower}})
        
    return clauses


def search_companies(
    industry: Optional[str],
    country: Optional[str],
    employee_min: Optional[int],
    employee_max: Optional[int],
    funding_stage: Optional[str],
    keywords: list[str],
    limit: int = 10,
) -> list[dict]:
    """Search PDL for companies matching ICP criteria.

    Returns a list of normalised company dicts.
    """
    query = _build_company_query(industry, country, employee_min, employee_max, funding_stage, keywords)
    data = _post_pdl("company/search", {"query": query, "size": min(limit, 25), "dataset": "all"})
    return [_parse_company(c) for c in data.get("data", []) if c.get("name") or c.get("display_name")]


def _build_company_query(
    industry: Optional[str],
    country: Optional[str],
    employee_min: Optional[int],
    employee_max: Optional[int],
    funding_stage: Optional[str],
    keywords: list[str],
) -> dict:
    must: list[dict] = []
    should: list[dict] = []

    if industry:
        industry_clauses = _normalize_industry(industry)
        if len(industry_clauses) == 1:
            must.append(industry_clauses[0])
        elif len(industry_clauses) > 1:
            must.append({"bool": {"should": industry_clauses}})

    if country:
        must.append({"match": {"location.country": country}})

    if employee_min is not None or employee_max is not None:
        size_filter: dict = {}
        if employee_min is not None:
            size_filter["gte"] = employee_min
        if employee_max is not None:
            size_filter["lte"] = employee_max
        must.append({"range": {"employee_count": size_filter}})

    if funding_stage:
        must.append({"match": {"latest_funding_stage": funding_stage}})

    for kw in keywords[:6]:
        should.append({"match": {"tags": kw}})
        should.append({"match": {"name": kw}})

    query: dict = {}
    if must and should:
        query = {"bool": {"must": must, "should": should}}
    elif must:
        query = {"bool": {"must": must}}
    elif should:
        query = {"bool": {"should": should}}
    else:
        query = {"match": {"industry": "internet"}}

    return query


def _parse_company(company: dict) -> dict:
    website = company.get("website", "") or ""
    if website and not website.startswith("http"):
        website = f"https://{website}"
        
    name = company.get("display_name") or company.get("name") or ""
    return {
        "pdl_id": company.get("id", ""),
        "name": name,
        "website": website,
        "industry": company.get("industry", "") or "",
        "employee_count": company.get("employee_count"),
        "funding_stage": company.get("latest_funding_stage", "") or "",
    }
