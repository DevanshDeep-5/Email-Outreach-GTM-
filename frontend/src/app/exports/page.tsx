"use client";

import { useQuery } from "@tanstack/react-query";
import { Download, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { exportsApi } from "@/lib/api";
import { format } from "date-fns";

export default function ExportsPage() {
  const { data: exports, isLoading } = useQuery({
    queryKey: ["exports"],
    queryFn: exportsApi.list,
    refetchInterval: 10000,
  });

  return (
    <div className="flex flex-col gap-6 p-8">
      <div>
        <h1 className="text-xl font-semibold">Exports</h1>
        <p className="mt-0.5 text-sm text-muted-foreground">
          Download ready-to-launch CSV files for Apollo, Instantly, and Smartlead
        </p>
      </div>

      {isLoading ? (
        <div className="space-y-2">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="h-16 w-full" />
          ))}
        </div>
      ) : exports?.length === 0 ? (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center py-16 text-center">
            <FileText className="h-8 w-8 text-muted-foreground/40" />
            <p className="mt-3 text-sm font-medium">No exports yet</p>
            <p className="mt-1 text-xs text-muted-foreground">
              Complete a campaign workflow to generate a CSV export
            </p>
          </CardContent>
        </Card>
      ) : (
        <Card className="border-border overflow-hidden">
          <div className="divide-y divide-border">
            {exports?.map((exp) => (
              <div
                key={exp.id}
                className="flex items-center justify-between p-4"
              >
                <div className="flex items-center gap-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded bg-primary/10">
                    <FileText className="h-4 w-4 text-primary" />
                  </div>
                  <div>
                    <p className="text-sm font-medium">
                      campaign_export_{exp.id.slice(0, 8)}.csv
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {exp.row_count} rows ·{" "}
                      {format(new Date(exp.created_at), "MMM d, yyyy HH:mm")}
                    </p>
                  </div>
                </div>
                <Button asChild size="sm" variant="outline">
                  <a href={exportsApi.downloadUrl(exp.id)} download>
                    <Download className="mr-1.5 h-3.5 w-3.5" />
                    Download
                  </a>
                </Button>
              </div>
            ))}
          </div>
        </Card>
      )}

      <div className="rounded-lg border border-border bg-muted/20 p-4">
        <p className="text-xs font-medium text-muted-foreground mb-2">
          CSV Column Reference
        </p>
        <div className="grid grid-cols-4 gap-1">
          {[
            "Company", "Website", "Contact Name", "Title",
            "Email", "LinkedIn", "Intent Score", "Intent Reason",
            "Subject", "Cold Email", "Follow-up 1", "Follow-up 2", "Break-up Email",
          ].map((col) => (
            <span
              key={col}
              className="rounded bg-secondary px-2 py-0.5 text-xs text-foreground font-mono"
            >
              {col}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
