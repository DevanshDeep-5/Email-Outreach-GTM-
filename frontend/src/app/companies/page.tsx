"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { Building2, ExternalLink, ArrowRight } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Input } from "@/components/ui/input";
import { companiesApi } from "@/lib/api";
import { useState } from "react";

export default function CompaniesPage() {
  const [search, setSearch] = useState("");

  const { data: companies, isLoading } = useQuery({
    queryKey: ["companies"],
    queryFn: () => companiesApi.list(),
    refetchInterval: 10000,
  });

  const filtered = companies?.filter((c) =>
    c.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="flex flex-col gap-6 p-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Companies</h1>
          <p className="mt-0.5 text-sm text-muted-foreground">
            All discovered companies across campaigns
          </p>
        </div>
        <Input
          placeholder="Search companies…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-56 bg-card"
        />
      </div>

      {isLoading ? (
        <div className="space-y-2">
          {[...Array(8)].map((_, i) => (
            <Skeleton key={i} className="h-16 w-full" />
          ))}
        </div>
      ) : filtered?.length === 0 ? (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center py-16 text-center">
            <Building2 className="h-8 w-8 text-muted-foreground/40" />
            <p className="mt-3 text-sm text-muted-foreground">
              {search ? "No companies match your search" : "No companies discovered yet"}
            </p>
          </CardContent>
        </Card>
      ) : (
        <Card className="border-border overflow-hidden">
          <div className="divide-y divide-border">
            {filtered?.map((company) => (
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
                    {company.industry && <span>{company.industry}</span>}
                    {company.employee_count && (
                      <span>· {company.employee_count} emp.</span>
                    )}
                    {company.funding_stage && (
                      <span>· {company.funding_stage}</span>
                    )}
                    {company.website && (
                      <button
                        type="button"
                        onClick={(e) => {
                          e.preventDefault();
                          window.open(company.website || undefined, "_blank", "noopener,noreferrer");
                        }}
                        className="hover:text-foreground transition-colors"
                      >
                        <ExternalLink className="h-3 w-3" />
                      </button>
                    )}
                  </div>
                </div>
                <ArrowRight className="h-3.5 w-3.5 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity shrink-0" />
              </Link>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
