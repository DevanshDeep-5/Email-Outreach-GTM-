# SignalFlow AI

> AI-powered GTM Campaign Builder — discovers prospects, researches companies, enriches contacts, generates personalized cold email sequences, and exports ready-to-launch outbound campaigns.

Built as a portfolio project demonstrating: **Full Stack Engineering · AI Engineering · GTM Engineering · LangGraph · Agentic AI Workflows**

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 15 (App Router) · TypeScript · TailwindCSS v4 · shadcn/ui |
| State | TanStack Query (server) · Zustand (UI) |
| Backend | FastAPI · Python 3.11+ |
| AI Workflow | LangGraph · LangChain |
| LLM | OpenRouter → `anthropic/claude-3-haiku` |
| Database | PostgreSQL · SQLAlchemy 2.0 |
| Data | Apollo.io · Firecrawl · Tavily |

---

## Project Structure

```
NEW_GTM/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── requirements.txt
│   ├── .env.example         # Copy → .env and fill keys
│   └── app/
│       ├── config.py        # Settings
│       ├── db.py            # SQLAlchemy
│       ├── models.py        # ORM models
│       ├── schemas.py       # Pydantic schemas
│       ├── routers/         # API endpoints
│       ├── services/        # Apollo, Firecrawl, Tavily, LLM clients
│       └── graph/           # LangGraph workflow
│           ├── state.py     # TypedDict state
│           ├── nodes.py     # 10 individual nodes
│           └── workflow.py  # Graph assembly
│
└── frontend/
    └── src/
        ├── app/             # Next.js App Router pages
        ├── components/      # UI components
        ├── lib/api.ts       # Typed API client
        ├── store/ui.ts      # Zustand store
        └── types/index.ts   # Shared TypeScript types
```

---

## Setup

### Prerequisites
- PostgreSQL running locally
- Python 3.11+
- Node.js 20+

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your API keys

# Start the server (creates DB tables automatically)
uvicorn main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000**

---

## API Keys Required

| Key | Where to get |
|---|---|
| `OPENROUTER_API_KEY` | https://openrouter.ai/ |
| `APOLLO_API_KEY` | https://www.apollo.io/ |
| `FIRECRAWL_API_KEY` | https://www.firecrawl.dev/ |
| `TAVILY_API_KEY` | https://tavily.com/ |
| `DATABASE_URL` | Your local PostgreSQL connection string |

---

## LangGraph Workflow

```
Campaign Planner      → Initialize campaign
       ↓
Company Finder        → Apollo: search by ICP params, limit=num_leads
       ↓
Website Researcher    → Firecrawl: scrape homepage, about, pricing
       ↓
Web Researcher        → Tavily: funding, hiring, news signals
       ↓
Company Analyzer      → LLM: pain points, value prop, outreach angle
       ↓
Contact Finder        → Apollo: find decision-maker contacts
       ↓
Intent Analyzer       → LLM: 0–100 intent score + reasoning
       ↓
Email Generator       → LLM: personalized cold email + CTA
       ↓
Follow-up Generator   → LLM: follow-up 1, 2, break-up email
       ↓
CSV Exporter          → Pandas: assemble and save CSV
```

The workflow runs in a **background thread** automatically after campaign creation. The UI polls and updates in real-time.

---

## Application Flow

1. Open app → Dashboard
2. Click **New Campaign** → Fill ICP form → Submit
3. Workflow starts automatically (background thread)
4. Watch the **workflow progress** in Campaign Detail view
5. Browse **Companies** → View AI analysis + intent scores
6. Review and edit **Emails** before export
7. Download **CSV** compatible with Apollo, Instantly, Smartlead

---

## API Endpoints

```
GET  /api/campaigns/dashboard
POST /api/campaigns/              → Creates campaign + starts workflow
GET  /api/campaigns/{id}          → Stats + status
DELETE /api/campaigns/{id}

GET  /api/companies/?campaign_id=...
GET  /api/companies/{id}          → Full detail with research + emails

GET  /api/emails/?campaign_id=...
PUT  /api/emails/{id}             → Edit email fields
POST /api/emails/{id}/regenerate  → Regenerate with LLM

GET  /api/exports/
GET  /api/exports/{id}/download   → Stream CSV file
```

---

## CSV Export Columns

`Company · Website · Contact Name · Title · Email · LinkedIn · Intent Score · Intent Reason · Subject · Cold Email · Follow-up 1 · Follow-up 2 · Break-up Email`

Compatible with Apollo, Instantly, and Smartlead import formats.
