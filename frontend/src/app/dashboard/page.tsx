"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import {
  Megaphone,
  Building2,
  Users,
  Mail,
  Download,
  ArrowRight,
  Plus,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { StatusBadge, NodeLabel } from "@/components/shared/StatusBadge";
import { campaignsApi } from "@/lib/api";
import { format } from "date-fns";

function StatCard({
  label,
  value,
  icon: Icon,
  loading,
}: {
  label: string;
  value: number;
  icon: React.ComponentType<{ className?: string }>;
  loading: boolean;
}) {
  return (
    <Card className="bg-card border-border">
      <CardContent className="p-5">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-muted-foreground font-medium uppercase tracking-wider">
              {label}
            </p>
            {loading ? (
              <Skeleton className="mt-2 h-7 w-16" />
            ) : (
              <p className="mt-1 text-2xl font-semibold tabular-nums">{value}</p>
            )}
          </div>
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
            <Icon className="h-5 w-5 text-primary" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default function DashboardPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["dashboard"],
    queryFn: campaignsApi.dashboard,
    refetchInterval: 5000,
  });

  return (
    <div className="flex flex-col gap-8 p-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Dashboard</h1>
          <p className="mt-0.5 text-sm text-muted-foreground">
            Overview of your outbound campaign pipeline
          </p>
        </div>
        <Button asChild size="sm">
          <Link href="/campaigns/new">
            <Plus className="mr-1.5 h-4 w-4" />
            New Campaign
          </Link>
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-3 xl:grid-cols-5">
        <StatCard
          label="Campaigns"
          value={data?.total_campaigns ?? 0}
          icon={Megaphone}
          loading={isLoading}
        />
        <StatCard
          label="Companies"
          value={data?.total_companies ?? 0}
          icon={Building2}
          loading={isLoading}
        />
        <StatCard
          label="Contacts"
          value={data?.total_contacts ?? 0}
          icon={Users}
          loading={isLoading}
        />
        <StatCard
          label="Emails"
          value={data?.total_emails ?? 0}
          icon={Mail}
          loading={isLoading}
        />
        <StatCard
          label="Exports"
          value={data?.export_count ?? 0}
          icon={Download}
          loading={isLoading}
        />
      </div>

      {/* Recent Campaigns */}
      <div>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-foreground">
            Recent Campaigns
          </h2>
          <Button asChild variant="ghost" size="sm" className="text-xs text-muted-foreground">
            <Link href="/campaigns">
              View all <ArrowRight className="ml-1 h-3 w-3" />
            </Link>
          </Button>
        </div>

        {isLoading ? (
          <div className="space-y-2">
            {[...Array(3)].map((_, i) => (
              <Skeleton key={i} className="h-16 w-full" />
            ))}
          </div>
        ) : data?.recent_campaigns.length === 0 ? (
          <Card className="border-dashed">
            <CardContent className="flex flex-col items-center justify-center py-12 text-center">
              <Megaphone className="h-8 w-8 text-muted-foreground/40" />
              <p className="mt-3 text-sm font-medium">No campaigns yet</p>
              <p className="mt-1 text-xs text-muted-foreground">
                Create your first campaign to start the workflow
              </p>
              <Button asChild size="sm" className="mt-4">
                <Link href="/campaigns/new">
                  <Plus className="mr-1.5 h-4 w-4" />
                  New Campaign
                </Link>
              </Button>
            </CardContent>
          </Card>
        ) : (
          <Card className="border-border">
            <div className="divide-y divide-border">
              {data?.recent_campaigns.map((campaign) => (
                <Link
                  key={campaign.id}
                  href={`/campaigns/${campaign.id}`}
                  className="flex items-center justify-between p-4 hover:bg-accent/50 transition-colors"
                >
                  <div className="flex flex-col gap-0.5">
                    <span className="text-sm font-medium">{campaign.name}</span>
                    <div className="flex items-center gap-2">
                      <NodeLabel node={campaign.current_node} />
                      {campaign.industry && (
                        <span className="text-xs text-muted-foreground">
                          · {campaign.industry}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <StatusBadge status={campaign.status} />
                    <span className="text-xs text-muted-foreground">
                      {format(new Date(campaign.created_at), "MMM d")}
                    </span>
                    <ArrowRight className="h-3.5 w-3.5 text-muted-foreground" />
                  </div>
                </Link>
              ))}
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}
