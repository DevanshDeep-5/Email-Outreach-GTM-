import type { CampaignStatus } from "@/types";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

const STATUS_CONFIG: Record<
  CampaignStatus,
  { label: string; className: string }
> = {
  pending: { label: "Pending", className: "bg-muted text-muted-foreground" },
  running: {
    label: "Running",
    className: "bg-blue-500/15 text-blue-400 border-blue-500/30",
  },
  completed: {
    label: "Completed",
    className: "bg-green-500/15 text-green-400 border-green-500/30",
  },
  failed: {
    label: "Failed",
    className: "bg-red-500/15 text-red-400 border-red-500/30",
  },
};

const NODE_LABELS: Record<string, string> = {
  campaign_planner: "Initializing",
  company_finder: "Finding Companies",
  website_researcher: "Scraping Websites",
  web_researcher: "Web Research",
  company_analyzer: "Analyzing Companies",
  contact_finder: "Finding Contacts",
  intent_analyzer: "Scoring Intent",
  email_generator: "Generating Emails",
  followup_generator: "Generating Follow-ups",
  csv_exporter: "Exporting CSV",
  completed: "Completed",
};

export function StatusBadge({ status }: { status: CampaignStatus }) {
  const config = STATUS_CONFIG[status];
  return (
    <Badge
      variant="outline"
      className={cn("text-xs font-medium", config.className)}
    >
      {status === "running" && (
        <span className="mr-1.5 inline-block h-1.5 w-1.5 rounded-full bg-blue-400 animate-pulse" />
      )}
      {config.label}
    </Badge>
  );
}

export function NodeLabel({ node }: { node: string | null }) {
  if (!node) return null;
  return (
    <span className="text-xs text-muted-foreground">
      {NODE_LABELS[node] || node}
    </span>
  );
}

export function IntentScoreBadge({ score }: { score: number }) {
  const color =
    score >= 75
      ? "bg-green-500/15 text-green-400 border-green-500/30"
      : score >= 50
      ? "bg-yellow-500/15 text-yellow-400 border-yellow-500/30"
      : "bg-red-500/15 text-red-400 border-red-500/30";

  return (
    <Badge variant="outline" className={cn("font-mono text-xs font-semibold", color)}>
      {score}
    </Badge>
  );
}
