import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";

function EnvVar({ name, description }: { name: string; description: string }) {
  return (
    <div className="space-y-1.5">
      <Label className="font-mono text-xs text-primary">{name}</Label>
      <Input
        readOnly
        value={`Set in backend/.env`}
        className="bg-card font-mono text-xs text-muted-foreground"
      />
      <p className="text-xs text-muted-foreground">{description}</p>
    </div>
  );
}

export default function SettingsPage() {
  return (
    <div className="flex flex-col gap-8 p-8 max-w-2xl">
      <div>
        <h1 className="text-xl font-semibold">Settings</h1>
        <p className="mt-0.5 text-sm text-muted-foreground">
          Configuration reference for SignalFlow AI
        </p>
      </div>

      {/* API Keys */}
      <Card className="border-border">
        <CardHeader>
          <CardTitle className="text-sm font-semibold">API Keys</CardTitle>
          <p className="text-xs text-muted-foreground">
            Configure in{" "}
            <code className="rounded bg-secondary px-1 py-0.5 font-mono">
              backend/.env
            </code>
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          <EnvVar
            name="OPENROUTER_API_KEY"
            description="OpenRouter key for LLM inference (company analysis, email generation). Get at openrouter.ai"
          />
          <Separator />
          <EnvVar
            name="APOLLO_API_KEY"
            description="Apollo.io key for company and contact discovery. Get at apollo.io"
          />
          <Separator />
          <EnvVar
            name="FIRECRAWL_API_KEY"
            description="Firecrawl key for website scraping. Get at firecrawl.dev"
          />
          <Separator />
          <EnvVar
            name="TAVILY_API_KEY"
            description="Tavily key for web research (funding, hiring, news). Get at tavily.com"
          />
          <Separator />
          <EnvVar
            name="DATABASE_URL"
            description="PostgreSQL connection string. Example: postgresql://postgres:pass@localhost:5432/signalflow"
          />
        </CardContent>
      </Card>

      {/* LangGraph Workflow */}
      <Card className="border-border">
        <CardHeader>
          <CardTitle className="text-sm font-semibold">LangGraph Workflow</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-1.5">
            {[
              ["campaign_planner", "Initialize campaign, set status to running"],
              ["company_finder", "Apollo API — search companies by ICP"],
              ["website_researcher", "Firecrawl — scrape homepage, about, pricing"],
              ["web_researcher", "Tavily — funding, hiring, news research"],
              ["company_analyzer", "LLM — extract pain points and value props"],
              ["contact_finder", "Apollo API — find decision-maker contacts"],
              ["intent_analyzer", "LLM — score buying intent 0–100"],
              ["email_generator", "LLM — personalized cold email + CTA"],
              ["followup_generator", "LLM — follow-up 1, 2 and break-up"],
              ["csv_exporter", "Pandas — build and save CSV to disk"],
            ].map(([node, desc]) => (
              <div key={node} className="flex items-start gap-3 py-1.5">
                <code className="rounded bg-secondary px-1.5 py-0.5 text-xs font-mono text-primary shrink-0">
                  {node}
                </code>
                <p className="text-xs text-muted-foreground">{desc}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Tech Stack */}
      <Card className="border-border">
        <CardHeader>
          <CardTitle className="text-sm font-semibold">Tech Stack</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-x-8 gap-y-1">
            {[
              ["Frontend", "Next.js 15 (App Router)"],
              ["Styling", "TailwindCSS v4 + shadcn/ui"],
              ["State", "TanStack Query + Zustand"],
              ["Backend", "FastAPI + Python"],
              ["AI Workflow", "LangGraph + LangChain"],
              ["LLM", "OpenRouter → claude-3-haiku"],
              ["Database", "PostgreSQL + SQLAlchemy"],
              ["Company Data", "Apollo.io API"],
              ["Web Scraping", "Firecrawl API"],
              ["Web Research", "Tavily API"],
            ].map(([label, value]) => (
              <div key={label} className="flex justify-between py-1 text-xs">
                <span className="text-muted-foreground">{label}</span>
                <span className="font-medium">{value}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
