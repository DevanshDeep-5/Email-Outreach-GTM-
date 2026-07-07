"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { Plus, ArrowRight, Building2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { StatusBadge, NodeLabel } from "@/components/shared/StatusBadge";
import { campaignsApi } from "@/lib/api";
import { format } from "date-fns";

export default function CampaignsPage() {
  const { data: campaigns, isLoading } = useQuery({
    queryKey: ["campaigns"],
    queryFn: campaignsApi.list,
    refetchInterval: 5000,
  });

  return (
    <div className="flex flex-col gap-6 p-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Campaigns</h1>
          <p className="mt-0.5 text-sm text-muted-foreground">
            All GTM outbound campaigns
          </p>
        </div>
        <Button asChild size="sm">
          <Link href="/campaigns/new">
            <Plus className="mr-1.5 h-4 w-4" />
            New Campaign
          </Link>
        </Button>
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="h-20 w-full" />
          ))}
        </div>
      ) : campaigns?.length === 0 ? (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-16 text-center">
            <Building2 className="h-8 w-8 text-muted-foreground/40" />
            <p className="mt-3 text-sm font-medium">No campaigns yet</p>
            <p className="mt-1 text-xs text-muted-foreground">
              Start by creating a campaign with your ICP parameters
            </p>
            <Button asChild size="sm" className="mt-4">
              <Link href="/campaigns/new">Create Campaign</Link>
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Card className="border-border overflow-hidden">
          <div className="divide-y divide-border">
            {campaigns?.map((campaign) => (
              <Link
                key={campaign.id}
                href={`/campaigns/${campaign.id}`}
                className="flex items-center justify-between p-5 hover:bg-accent/40 transition-colors group"
              >
                <div className="flex flex-col gap-1 min-w-0">
                  <span className="text-sm font-medium truncate">
                    {campaign.name}
                  </span>
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    {campaign.industry && <span>{campaign.industry}</span>}
                    {campaign.country && <span>· {campaign.country}</span>}
                    {campaign.num_leads && (
                      <span>· {campaign.num_leads} leads</span>
                    )}
                  </div>
                  <NodeLabel node={campaign.current_node} />
                </div>
                <div className="flex items-center gap-3 shrink-0 pl-4">
                  <StatusBadge status={campaign.status} />
                  <span className="text-xs text-muted-foreground">
                    {format(new Date(campaign.created_at), "MMM d, yyyy")}
                  </span>
                  <ArrowRight className="h-3.5 w-3.5 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
              </Link>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
