"use client";

import { use, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import {
  ArrowLeft,
  ExternalLink,
  RefreshCw,
  Loader2,
  Copy,
  Check,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { IntentScoreBadge } from "@/components/shared/StatusBadge";
import { companiesApi, emailsApi } from "@/lib/api";
import type { Email } from "@/types";

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Button variant="ghost" size="sm" onClick={handleCopy} className="h-7 px-2">
      {copied ? (
        <Check className="h-3.5 w-3.5 text-green-400" />
      ) : (
        <Copy className="h-3.5 w-3.5" />
      )}
    </Button>
  );
}

function EmailEditor({ email }: { email: Email }) {
  const queryClient = useQueryClient();
  const [fields, setFields] = useState({
    subject: email.subject ?? "",
    cold_email: email.cold_email ?? "",
    follow_up_1: email.follow_up_1 ?? "",
    follow_up_2: email.follow_up_2 ?? "",
    break_up_email: email.break_up_email ?? "",
  });

  const updateMutation = useMutation({
    mutationFn: (data: typeof fields) => emailsApi.update(email.id, data),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["company", email.company_id] }),
  });

  const regenMutation = useMutation({
    mutationFn: () => emailsApi.regenerate(email.id),
    onSuccess: (updated) => {
      setFields({
        subject: updated.subject ?? "",
        cold_email: updated.cold_email ?? "",
        follow_up_1: updated.follow_up_1 ?? "",
        follow_up_2: updated.follow_up_2 ?? "",
        break_up_email: updated.break_up_email ?? "",
      });
      queryClient.invalidateQueries({ queryKey: ["company", email.company_id] });
    },
  });

  const emailFields = [
    { key: "subject", label: "Subject Line" },
    { key: "cold_email", label: "Cold Email" },
    { key: "follow_up_1", label: "Follow-up 1 (Day 3)" },
    { key: "follow_up_2", label: "Follow-up 2 (Day 7)" },
    { key: "break_up_email", label: "Break-up Email" },
  ] as const;

  return (
    <div className="space-y-4">
      <div className="flex justify-end gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => regenMutation.mutate()}
          disabled={regenMutation.isPending}
        >
          {regenMutation.isPending ? (
            <Loader2 className="mr-1.5 h-3.5 w-3.5 animate-spin" />
          ) : (
            <RefreshCw className="mr-1.5 h-3.5 w-3.5" />
          )}
          Regenerate
        </Button>
        <Button
          size="sm"
          onClick={() => updateMutation.mutate(fields)}
          disabled={updateMutation.isPending}
        >
          {updateMutation.isPending ? (
            <Loader2 className="mr-1.5 h-3.5 w-3.5 animate-spin" />
          ) : (
            "Save Changes"
          )}
        </Button>
      </div>

      {emailFields.map(({ key, label }) => (
        <div key={key} className="space-y-1.5">
          <div className="flex items-center justify-between">
            <label className="text-xs font-medium text-muted-foreground">
              {label}
            </label>
            <CopyButton text={fields[key]} />
          </div>
          <Textarea
            value={fields[key]}
            onChange={(e) =>
              setFields((prev) => ({ ...prev, [key]: e.target.value }))
            }
            className="bg-card resize-none text-sm font-mono leading-relaxed"
            rows={key === "subject" ? 1 : 6}
          />
        </div>
      ))}

      {email.personalization_notes && (
        <div className="rounded-lg border border-border bg-muted/30 p-3">
          <p className="text-xs font-medium text-muted-foreground mb-1">
            Personalization Notes
          </p>
          <p className="text-xs text-foreground leading-relaxed">
            {email.personalization_notes}
          </p>
        </div>
      )}
    </div>
  );
}

export default function CompanyDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);

  const { data, isLoading } = useQuery({
    queryKey: ["company", id],
    queryFn: () => companiesApi.get(id),
  });

  if (isLoading) {
    return (
      <div className="p-8 space-y-4">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-48 w-full" />
        <Skeleton className="h-48 w-full" />
      </div>
    );
  }

  const { company, research, intent_score, contacts, emails } = data!;

  return (
    <div className="flex flex-col gap-6 p-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Button asChild variant="ghost" size="sm" className="text-muted-foreground">
            <Link href="/companies">
              <ArrowLeft className="mr-1.5 h-4 w-4" />
              Companies
            </Link>
          </Button>
          <span className="text-muted-foreground">/</span>
          <span className="text-sm font-medium">{company.name}</span>
        </div>
        <div className="flex items-center gap-3">
          {intent_score && <IntentScoreBadge score={intent_score.score} />}
          {company.website && (
            <Button asChild variant="ghost" size="sm" className="text-muted-foreground">
              <a href={company.website} target="_blank" rel="noopener noreferrer">
                <ExternalLink className="h-4 w-4" />
              </a>
            </Button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Left sidebar */}
        <div className="col-span-1 space-y-4">
          {/* Company info */}
          <Card className="border-border">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-semibold">Company</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              {[
                ["Website", company.website],
                ["Industry", company.industry],
                ["Employees", company.employee_count],
                ["Funding", company.funding_stage],
              ].map(([label, val]) =>
                val ? (
                  <div key={label as string} className="flex justify-between items-center">
                    <span className="text-xs text-muted-foreground">{label}</span>
                    {label === "Website" ? (
                      <a
                        href={val as string}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-primary hover:underline truncate max-w-[140px]"
                      >
                        {(val as string).replace(/https?:\/\//, "")}
                      </a>
                    ) : (
                      <span className="text-xs font-medium">{val}</span>
                    )}
                  </div>
                ) : null
              )}
            </CardContent>
          </Card>

          {/* Intent Score */}
          {intent_score && (
            <Card className="border-border">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-semibold flex items-center justify-between">
                  Intent Score
                  <IntentScoreBadge score={intent_score.score} />
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {intent_score.reasoning && (
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    {intent_score.reasoning}
                  </p>
                )}
                {intent_score.signals.length > 0 && (
                  <div className="space-y-1">
                    {intent_score.signals.map((signal, i) => (
                      <div
                        key={i}
                        className="flex items-start gap-1.5 text-xs text-foreground"
                      >
                        <span className="mt-0.5 h-1.5 w-1.5 rounded-full bg-green-400 shrink-0" />
                        {signal}
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Contacts */}
          {contacts.length > 0 && (
            <Card className="border-border">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-semibold">
                  Contacts ({contacts.length})
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {contacts.map((contact) => (
                  <div key={contact.id} className="space-y-2.5 border-b border-border/50 pb-3 last:border-0 last:pb-0">
                    <div className="space-y-0.5">
                      <p className="text-xs font-semibold text-foreground">{contact.name}</p>
                      <p className="text-xs text-muted-foreground leading-tight">
                        {contact.title}
                      </p>
                    </div>

                    {/* Badges for Department and Seniority */}
                    <div className="flex flex-wrap gap-1">
                      {contact.department && (
                        <span className="inline-flex items-center rounded bg-primary/10 px-1.5 py-0.5 text-[9px] font-semibold text-primary uppercase tracking-wider">
                          {contact.department}
                        </span>
                      )}
                      {contact.seniority && (
                        <span className="inline-flex items-center rounded bg-muted px-1.5 py-0.5 text-[9px] font-semibold text-muted-foreground uppercase tracking-wider">
                          {contact.seniority}
                        </span>
                      )}
                    </div>

                    {/* Email with Verification Badge */}
                    {contact.email ? (
                      <div className="space-y-1">
                        <p className="text-xs text-primary font-mono select-all truncate">
                          {contact.email}
                        </p>
                        <div className="flex items-center gap-1.5">
                          {contact.email_verified ? (
                            <span className="inline-flex items-center gap-0.5 rounded bg-green-500/10 px-1.5 py-0.5 text-[9px] font-medium text-green-400">
                              Verified ✓
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-0.5 rounded bg-yellow-500/10 px-1.5 py-0.5 text-[9px] font-medium text-yellow-400">
                              Unverified
                            </span>
                          )}
                          {contact.confidence_score !== null && (
                            <span className="text-[9px] text-muted-foreground">
                              Confidence: {contact.confidence_score}%
                            </span>
                          )}
                        </div>
                      </div>
                    ) : (
                      <p className="text-[10px] text-muted-foreground italic">No email found</p>
                    )}

                    {/* Metadata: Data Source & LinkedIn */}
                    <div className="flex items-center justify-between text-[10px] text-muted-foreground pt-0.5">
                      {contact.data_source && (
                        <span className="capitalize text-[9px] tracking-wide text-muted-foreground/75">
                          Source: {contact.data_source.replace(/_/g, " ")}
                        </span>
                      )}
                      {contact.linkedin_url && (
                        <a
                          href={contact.linkedin_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-primary hover:underline inline-flex items-center gap-0.5 font-medium"
                        >
                          LinkedIn <ExternalLink className="h-2.5 w-2.5" />
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}
        </div>

        {/* Right main content */}
        <div className="col-span-2">
          <Tabs defaultValue="analysis">
            <TabsList className="mb-4">
              <TabsTrigger value="analysis">Analysis</TabsTrigger>
              <TabsTrigger value="research">Research</TabsTrigger>
              <TabsTrigger value="emails">
                Emails ({emails.length})
              </TabsTrigger>
            </TabsList>

            {/* Analysis tab */}
            <TabsContent value="analysis" className="space-y-4">
              {research ? (
                <>
                  {research.company_summary && (
                    <Card className="border-border">
                      <CardHeader className="pb-2">
                        <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                          Summary
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <p className="text-sm leading-relaxed">
                          {research.company_summary}
                        </p>
                      </CardContent>
                    </Card>
                  )}

                  <div className="grid grid-cols-2 gap-3">
                    {[
                      { label: "Products", value: research.products },
                      { label: "Business Model", value: research.business_model },
                      { label: "Target Market", value: research.target_market },
                      { label: "Pain Points", value: research.pain_points },
                      { label: "Growth Signals", value: research.growth_signals },
                      { label: "Sales Opportunities", value: research.sales_opportunities },
                      { label: "Outreach Angle", value: research.outreach_angle },
                      { label: "Value Proposition", value: research.value_proposition },
                    ]
                      .filter(({ value }) => value)
                      .map(({ label, value }) => (
                        <Card key={label} className="border-border">
                          <CardHeader className="pb-2">
                            <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                              {label}
                            </CardTitle>
                          </CardHeader>
                          <CardContent>
                            <p className="text-xs leading-relaxed">{value}</p>
                          </CardContent>
                        </Card>
                      ))}
                  </div>
                </>
              ) : (
                <Card className="border-dashed">
                  <CardContent className="py-12 text-center">
                    <p className="text-sm text-muted-foreground">
                      Analysis will appear after the workflow completes
                    </p>
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            {/* Research tab */}
            <TabsContent value="research">
              {research?.tavily_summary ? (
                <Card className="border-border">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                      Web Research
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm whitespace-pre-wrap leading-relaxed">
                      {research.tavily_summary}
                    </p>
                  </CardContent>
                </Card>
              ) : (
                <Card className="border-dashed">
                  <CardContent className="py-12 text-center">
                    <p className="text-sm text-muted-foreground">
                      Research data not available yet
                    </p>
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            {/* Emails tab */}
            <TabsContent value="emails">
              {emails.length === 0 ? (
                <Card className="border-dashed">
                  <CardContent className="py-12 text-center">
                    <p className="text-sm text-muted-foreground">
                      Emails will appear after the workflow generates them
                    </p>
                  </CardContent>
                </Card>
              ) : (
                <Card className="border-border">
                  <CardContent className="pt-6">
                    <EmailEditor email={emails[0]} />
                  </CardContent>
                </Card>
              )}
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}
