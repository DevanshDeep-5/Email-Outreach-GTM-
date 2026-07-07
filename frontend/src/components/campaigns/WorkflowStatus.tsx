"use client";

import { useQuery } from "@tanstack/react-query";
import { campaignsApi } from "@/lib/api";
import { StatusBadge, NodeLabel } from "@/components/shared/StatusBadge";
import { Progress } from "@/components/ui/progress";
import { CheckCircle2, Circle, Loader2 } from "lucide-react";

const NODES = [
  { key: "campaign_planner", label: "Campaign Planner" },
  { key: "company_finder", label: "Find Companies" },
  { key: "website_researcher", label: "Website Research" },
  { key: "web_researcher", label: "Web Research" },
  { key: "company_analyzer", label: "Analyze Companies" },
  { key: "contact_finder", label: "Find Contacts" },
  { key: "intent_analyzer", label: "Score Intent" },
  { key: "email_generator", label: "Generate Emails" },
  { key: "followup_generator", label: "Generate Follow-ups" },
  { key: "csv_exporter", label: "Export CSV" },
];

interface WorkflowStatusProps {
  campaignId: string;
}

export function WorkflowStatus({ campaignId }: WorkflowStatusProps) {
  const { data } = useQuery({
    queryKey: ["campaign", campaignId],
    queryFn: () => campaignsApi.get(campaignId),
    refetchInterval: (query) => {
      const status = query.state.data?.campaign.status;
      return status === "running" || status === "pending" ? 3000 : false;
    },
  });

  const campaign = data?.campaign;
  if (!campaign) return null;

  const currentNodeIndex = NODES.findIndex(
    (n) => n.key === campaign.current_node
  );
  const progress =
    campaign.status === "completed"
      ? 100
      : campaign.status === "pending"
      ? 0
      : Math.round(((currentNodeIndex + 1) / NODES.length) * 100);

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <StatusBadge status={campaign.status} />
          <NodeLabel node={campaign.current_node} />
        </div>
        <span className="text-xs font-mono text-muted-foreground">
          {progress}%
        </span>
      </div>

      <Progress value={progress} className="h-1.5" />

      {/* Node steps */}
      <div className="grid grid-cols-2 gap-1.5 pt-1">
        {NODES.map((node, i) => {
          const isCompleted =
            campaign.status === "completed" ||
            (currentNodeIndex > i && campaign.status === "running");
          const isCurrent =
            campaign.current_node === node.key &&
            campaign.status === "running";
          const isPending =
            !isCompleted && !isCurrent;

          return (
            <div
              key={node.key}
              className="flex items-center gap-2 text-xs py-1"
            >
              {isCompleted ? (
                <CheckCircle2 className="h-3.5 w-3.5 shrink-0 text-green-400" />
              ) : isCurrent ? (
                <Loader2 className="h-3.5 w-3.5 shrink-0 text-blue-400 animate-spin" />
              ) : (
                <Circle className="h-3.5 w-3.5 shrink-0 text-muted-foreground/30" />
              )}
              <span
                className={
                  isCompleted
                    ? "text-foreground"
                    : isCurrent
                    ? "text-blue-400"
                    : "text-muted-foreground/50"
                }
              >
                {node.label}
              </span>
            </div>
          );
        })}
      </div>

      {/* Stats */}
      {data && (
        <div className="grid grid-cols-4 gap-2 pt-2 border-t border-border">
          {[
            { label: "Companies", value: data.companies_found },
            { label: "Processed", value: data.companies_processed },
            { label: "Contacts", value: data.contacts_found },
            { label: "Emails", value: data.emails_generated },
          ].map(({ label, value }) => (
            <div key={label} className="text-center">
              <p className="text-lg font-semibold tabular-nums">{value}</p>
              <p className="text-xs text-muted-foreground">{label}</p>
            </div>
          ))}
        </div>
      )}

      {campaign.error_message && (
        <div className="rounded-md border border-red-500/20 bg-red-500/10 p-3">
          <p className="text-xs text-red-400">{campaign.error_message}</p>
        </div>
      )}
    </div>
  );
}
