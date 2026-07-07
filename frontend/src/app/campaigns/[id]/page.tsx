"use client";

import { use } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import {
  ArrowLeft,
  ExternalLink,
  Download,
  Trash2,
  Building2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { WorkflowStatus } from "@/components/campaigns/WorkflowStatus";
import { IntentScoreBadge } from "@/components/shared/StatusBadge";
import { campaignsApi, companiesApi, exportsApi } from "@/lib/api";
import { useRouter } from "next/navigation";
import { format } from "date-fns";

export default function CampaignDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const router = useRouter();
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["campaign", id],
    queryFn: () => campaignsApi.get(id),
    refetchInterval: (query) => {
      const status = query.state.data?.campaign.status;
      return status === "running" || status === "pending" ? 3000 : false;
    },
  });

  const { data: companies, isLoading: companiesLoading } = useQuery({
    queryKey: ["companies", id],
    queryFn: () => companiesApi.list(id),
    refetchInterval: 5000,
  });

  const { data: exports } = useQuery({
    queryKey: ["exports", id],
    queryFn: () => exportsApi.byCampaign(id),
  });

  const deleteMutation = useMutation({
    mutationFn: () => campaignsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["campaigns"] });
      router.push("/campaigns");
    },
  });

  const campaign = data?.campaign;

  return (
    <div className="flex flex-col gap-6 p-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Button asChild variant="ghost" size="sm" className="text-muted-foreground">
            <Link href="/campaigns">
              <ArrowLeft className="mr-1.5 h-4 w-4" />
              Campaigns
            </Link>
          </Button>
          <span className="text-muted-foreground">/</span>
          {isLoading ? (
            <Skeleton className="h-5 w-40" />
          ) : (
            <span className="text-sm font-medium">{campaign?.name}</span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {exports && exports.length > 0 && (
            <Button asChild size="sm" variant="outline">
              <a
                href={exportsApi.downloadUrl(exports[0].id)}
                download
              >
                <Download className="mr-1.5 h-4 w-4" />
                Download CSV
              </a>
            </Button>
          )}
          <Button
            size="sm"
            variant="ghost"
            className="text-muted-foreground hover:text-red-400"
            onClick={() => {
              if (confirm("Delete this campaign?")) deleteMutation.mutate();
            }}
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Left: Workflow Status */}
        <div className="col-span-1">
          <Card className="border-border">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-semibold">Workflow</CardTitle>
            </CardHeader>
            <CardContent>
              {campaign && <WorkflowStatus campaignId={id} />}
            </CardContent>
          </Card>

          {/* Campaign Config */}
          {campaign && (
            <Card className="border-border mt-4">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-semibold">Campaign Config</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                {[
                  ["Industry", campaign.industry],
                  ["Country", campaign.country],
                  ["Funding Stage", campaign.funding_stage],
                  [
                    "Employees",
                    campaign.employee_min
                      ? `${campaign.employee_min}–${campaign.employee_max}`
                      : null,
                  ],
                  ["Leads Target", campaign.num_leads],
                ].map(([label, value]) =>
                  value ? (
                    <div key={label as string} className="flex justify-between">
                      <span className="text-muted-foreground text-xs">{label}</span>
                      <span className="text-xs font-medium">{value}</span>
                    </div>
                  ) : null
                )}

                {campaign.hiring_keywords.length > 0 && (
                  <div>
                    <p className="text-xs text-muted-foreground mb-1">
                      Keywords
                    </p>
                    <div className="flex flex-wrap gap-1">
                      {campaign.hiring_keywords.map((k) => (
                        <span
                          key={k}
                          className="rounded bg-secondary px-1.5 py-0.5 text-xs"
                        >
                          {k}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>

        {/* Right: Companies */}
        <div className="col-span-2">
          <Tabs defaultValue="companies">
            <TabsList className="mb-4">
              <TabsTrigger value="companies">
                Companies ({companies?.length ?? 0})
              </TabsTrigger>
            </TabsList>

            <TabsContent value="companies">
              {companiesLoading ? (
                <div className="space-y-2">
                  {[...Array(5)].map((_, i) => (
                    <Skeleton key={i} className="h-16 w-full" />
                  ))}
                </div>
              ) : companies?.length === 0 ? (
                <Card className="border-dashed">
                  <CardContent className="flex flex-col items-center py-12 text-center">
                    <Building2 className="h-7 w-7 text-muted-foreground/40" />
                    <p className="mt-3 text-sm text-muted-foreground">
                      Companies will appear as the workflow progresses
                    </p>
                  </CardContent>
                </Card>
              ) : (
                <Card className="border-border overflow-hidden">
                  <div className="divide-y divide-border">
                    {companies?.map((company) => (
                      <Link
                        key={company.id}
                        href={`/companies/${company.id}`}
                        className="flex items-center justify-between p-4 hover:bg-accent/40 transition-colors group"
                      >
                        <div className="flex flex-col gap-0.5 min-w-0">
                          <span className="text-sm font-medium truncate">
                            {company.name}
                          </span>
                          <div className="flex items-center gap-2 text-xs text-muted-foreground">
                            {company.industry && (
                              <span>{company.industry}</span>
                            )}
                            {company.employee_count && (
                              <span>· {company.employee_count} employees</span>
                            )}
                            {company.funding_stage && (
                              <span>· {company.funding_stage}</span>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center gap-2 shrink-0 pl-4">
                          {company.website && (
                            <button
                              type="button"
                              onClick={(e) => {
                                e.preventDefault();
                                window.open(company.website || undefined, "_blank", "noopener,noreferrer");
                              }}
                              className="text-muted-foreground hover:text-foreground transition-colors"
                            >
                              <ExternalLink className="h-3.5 w-3.5" />
                            </button>
                          )}
                        </div>
                      </Link>
                    ))}
                  </div>
                </Card>
              )}
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}
