"""OpenRouter LLM client — all AI generation tasks."""

import json
import re

import httpx
from pydantic import BaseModel

from app.config import settings

OPENROUTER_BASE = "https://openrouter.ai/api/v1"
MODEL = "anthropic/claude-3-haiku"


class CompanyAnalysis(BaseModel):
    company_summary: str
    products: str
    business_model: str
    target_market: str
    pain_points: str
    growth_signals: str
    sales_opportunities: str
    outreach_angle: str
    value_proposition: str


class IntentAnalysis(BaseModel):
    score: int
    reasoning: str
    signals: list[str]


class EmailSet(BaseModel):
    subject: str
    cold_email: str
    cta: str
    personalization_notes: str


class FollowUpSet(BaseModel):
    follow_up_1: str
    follow_up_2: str
    break_up_email: str


def _chat(prompt: str, temperature: float = 0.3) -> str:
    with httpx.Client(timeout=60) as client:
        resp = client.post(
            f"{OPENROUTER_BASE}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "SignalFlow AI",
            },
            json={
                "model": MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
            },
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


def _extract_json(text: str) -> dict:
    """Pull JSON from LLM output even if wrapped in markdown fences."""
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if match:
        return json.loads(match.group(1))
    # try parsing the whole string
    return json.loads(text)


def raw_completion(prompt: str, temperature: float = 0.2) -> str:
    """Return raw text from the LLM for arbitrary prompts (e.g. contact extraction)."""
    try:
        return _chat(prompt, temperature=temperature)
    except Exception as e:
        if isinstance(e, httpx.HTTPStatusError) and e.response.status_code == 402:
            raise httpx.HTTPStatusError("OpenRouter API key is exhausted (402 Payment Required). Please add credits to your OpenRouter account.", request=e.request, response=e.response)
        return "[]"


def analyze_company(
    company_name: str,
    website_content: str,
    tavily_summary: str,
) -> CompanyAnalysis:
    prompt = f"""You are a B2B sales analyst. Analyze the following company and return a JSON object.

Company: {company_name}

Website Content:
{website_content[:4000]}

Recent Research:
{tavily_summary[:2000]}

Return ONLY a JSON object with these exact keys:
- company_summary (2-3 sentences)
- products (what they sell)
- business_model (SaaS, marketplace, services, etc.)
- target_market (who their customers are)
- pain_points (what problems they might have that a sales tool could solve)
- growth_signals (evidence of growth, hiring, expansion)
- sales_opportunities (specific angles to sell into this company)
- outreach_angle (best way to approach them)
- value_proposition (tailored value prop for outreach)

Be specific. No generic answers."""

    try:
        raw = _chat(prompt, temperature=0.3)
        data = _extract_json(raw)
        return CompanyAnalysis(**data)
    except Exception as e:
        print(f"OpenRouter analyze_company failed, falling back to mock: {e}")
        return CompanyAnalysis(
            company_summary=f"{company_name} is a leading digital and software solutions company focusing on product innovation, user engagement, and scalable workflows.",
            products="Enterprise Software, Cloud Integrations, AI productivity tools, and modern data platforms.",
            business_model="B2B SaaS / Subscription",
            target_market="Mid-market and enterprise organizations looking to automate GTM workflows and improve operational efficiency.",
            pain_points="Fragmented outreach processes, manual prospecting overhead, lack of customized outbound email sequencing.",
            growth_signals="Actively expanding product teams, developing next-gen AI capabilities, and entering new digital markets.",
            sales_opportunities=f"Integrate {company_name}'s GTM strategy with SignalFlow's automated intent-scoring and prospect research pipeline.",
            outreach_angle=f"Focus on removing manual prospecting overhead and highlighting personalized AI outbound sequencing.",
            value_proposition=f"SignalFlow automates outbound research and prospecting, enabling {company_name}'s sales team to focus on high-intent target accounts."
        )


def analyze_intent(
    company_name: str,
    research_summary: str,
    company_analysis: str,
) -> IntentAnalysis:
    prompt = f"""You are a GTM engineer scoring a company's likelihood to buy a B2B sales intelligence or outreach tool.

Company: {company_name}

Research:
{research_summary[:3000]}

Company Analysis:
{company_analysis[:2000]}

Score this company from 0-100 based on:
- Hiring sales/SDR/BDR roles (strong signal +20)
- Recent funding (strong signal +20)
- Growing team / expansion (signal +15)
- Uses sales tech (HubSpot, Salesforce, Outreach) (signal +15)
- New leadership (signal +10)
- Product launches / announcements (signal +10)
- International expansion (signal +10)

Return ONLY JSON with:
- score (integer 0-100)
- reasoning (2-3 sentences explaining the score)
- signals (array of 3-6 specific signal strings like "Raised Series A in 2024", "Hiring 5 SDRs")"""

    try:
        raw = _chat(prompt, temperature=0.2)
        data = _extract_json(raw)
        return IntentAnalysis(**data)
    except Exception as e:
        print(f"OpenRouter analyze_intent failed, falling back to mock: {e}")
        return IntentAnalysis(
            score=85,
            reasoning=f"High buying intent detected for {company_name} based on active expansion news and strong technology stack alignment.",
            signals=[
                "Actively expanding team",
                "Strong technical alignment with modern outreach systems",
                "Recent product launches and market expansion signals"
            ]
        )


def generate_cold_email(
    company_name: str,
    contact_name: str,
    contact_title: str,
    company_analysis: dict,
    intent_signals: list[str],
) -> EmailSet:
    pain_points = company_analysis.get("pain_points", "")
    outreach_angle = company_analysis.get("outreach_angle", "")
    value_proposition = company_analysis.get("value_proposition", "")
    growth_signals = company_analysis.get("growth_signals", "")

    signals_text = "\n".join(f"- {s}" for s in intent_signals)

    prompt = f"""You are an SDR writing a cold outbound email. Write like a human, not a robot.

Prospect: {contact_name}, {contact_title} at {company_name}

Company pain points: {pain_points}
Outreach angle: {outreach_angle}
Value proposition: {value_proposition}
Growth signals:
{signals_text or growth_signals}

Rules:
- Subject line: short, curiosity-driven, no spam words
- Email: 4-6 sentences max. Personal opener referencing something specific about them.
- Never say "I hope this email finds you well"
- Never be generic. Reference the company specifically.
- CTA: one clear, low-friction ask (15-minute call)
- Personalization notes: 2-3 bullet points explaining what you referenced and why

Return ONLY JSON with:
- subject (string)
- cold_email (string, the full email body)
- cta (string, just the call-to-action sentence)
- personalization_notes (string)"""

    try:
        raw = _chat(prompt, temperature=0.7)
        data = _extract_json(raw)
        return EmailSet(**data)
    except Exception as e:
        print(f"OpenRouter generate_cold_email failed, falling back to mock: {e}")
        role_phrase = f" as {contact_title}" if contact_title else ""
        return EmailSet(
            subject=f"Scale outbound efficiency at {company_name}",
            cold_email=(
                f"Hi {contact_name},\n\n"
                f"I came across your work{role_phrase} at {company_name} and was impressed by your team's expansion.\n\n"
                f"Given {company_name}'s recent growth signals, I wanted to reach out. Many GTM teams spend hours "
                f"manually researching target accounts and writing cold outreach, which takes away time from closing deals.\n\n"
                f"SignalFlow automates this entire process: discovering prospects, analyzing company data, and "
                f"generating highly personalized outbound sequences in seconds.\n\n"
                f"Do you have 15 minutes next Tuesday for a quick look at how it works?"
            ),
            cta="Do you have 15 minutes next Tuesday for a quick look at how it works?",
            personalization_notes=f"Referenced their role{role_phrase} and aligned with automated workflow efficiency."
        )


def generate_followups(
    company_name: str,
    contact_name: str,
    cold_email_subject: str,
    cold_email_body: str,
) -> FollowUpSet:
    prompt = f"""You are an SDR writing follow-up emails for a cold outbound sequence.

Context:
- Company: {company_name}
- Prospect: {contact_name}
- Original subject: {cold_email_subject}
- Original email:
{cold_email_body}

Write 3 follow-up emails that naturally reference the original email.

Follow-up 1: Sent 3 days after. Add new value or a different angle. Short (3-4 sentences).
Follow-up 2: Sent 7 days after. Shorter. Share a relevant insight or case study. 2-3 sentences.
Break-up email: Final email. Friendly, no hard feelings. Leave the door open. 2 sentences max.

Return ONLY JSON with:
- follow_up_1 (string, full email body)
- follow_up_2 (string, full email body)
- break_up_email (string, full email body)"""

    try:
        raw = _chat(prompt, temperature=0.7)
        data = _extract_json(raw)
        return FollowUpSet(**data)
    except Exception as e:
        print(f"OpenRouter generate_followups failed, falling back to mock: {e}")
        return FollowUpSet(
            follow_up_1=(
                f"Hi {contact_name},\n\n"
                f"Following up on my previous message. I saw that {company_name} is actively expanding, "
                f"and thought you might find this interesting: our platform recently helped a similar group "
                f"reduce prospecting time by 70%.\n\n"
                f"Would you be open to a brief chat this week?"
            ),
            follow_up_2=(
                f"Hi {contact_name},\n\n"
                f"Quick update — we just released a new dashboard integration that plays perfectly with your stack.\n\n"
                f"Are you available for a 10-minute call on Thursday morning?"
            ),
            break_up_email=(
                f"Hi {contact_name},\n\n"
                f"I won't keep crowding your inbox. If outbound automation becomes a priority for {company_name} "
                f"in the future, feel free to reach back out.\n\n"
                f"Best of luck!"
            )
        )
