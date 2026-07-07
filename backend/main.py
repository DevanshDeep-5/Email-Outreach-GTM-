from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import Base, engine
from app.routers import campaigns, companies, emails, exports

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SignalFlow AI",
    description="AI-powered GTM Campaign Builder API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(campaigns.router)
app.include_router(companies.router)
app.include_router(emails.router)
app.include_router(exports.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "SignalFlow AI"}
