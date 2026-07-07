"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import Link from "next/link";
import { Mail, ArrowRight, Copy, Check } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { emailsApi } from "@/lib/api";
import type { Email } from "@/types";

function EmailPreviewCard({ email }: { email: Email }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = (e: React.MouseEvent) => {
    e.preventDefault();
    const text = [
      `Subject: ${email.subject}`,
      "",
      email.cold_email,
      "",
      "--- Follow-up 1 ---",
      email.follow_up_1,
      "",
      "--- Follow-up 2 ---",
      email.follow_up_2,
      "",
      "--- Break-up ---",
      email.break_up_email,
    ]
      .filter(Boolean)
      .join("\n");

    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Link href={`/companies/${email.company_id}`}>
      <Card className="border-border hover:bg-accent/30 transition-colors group cursor-pointer">
        <CardContent className="p-4">
          <div className="flex items-start justify-between gap-3">
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{email.subject}</p>
              <p className="mt-1 text-xs text-muted-foreground line-clamp-2 leading-relaxed">
                {email.cold_email}
              </p>
              <div className="mt-2 flex gap-1.5">
                {email.follow_up_1 && (
                  <Badge variant="outline" className="text-xs">
                    F/U 1
                  </Badge>
                )}
                {email.follow_up_2 && (
                  <Badge variant="outline" className="text-xs">
                    F/U 2
                  </Badge>
                )}
                {email.break_up_email && (
                  <Badge variant="outline" className="text-xs">
                    Break-up
                  </Badge>
                )}
              </div>
            </div>
            <button
              onClick={handleCopy}
              className="text-muted-foreground hover:text-foreground mt-0.5 transition-colors shrink-0"
            >
              {copied ? (
                <Check className="h-3.5 w-3.5 text-green-400" />
              ) : (
                <Copy className="h-3.5 w-3.5" />
              )}
            </button>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}

export default function EmailsPage() {
  const [search, setSearch] = useState("");

  const { data: emails, isLoading } = useQuery({
    queryKey: ["emails"],
    queryFn: () => emailsApi.list(),
    refetchInterval: 10000,
  });

  const filtered = emails?.filter(
    (e) =>
      e.subject?.toLowerCase().includes(search.toLowerCase()) ||
      e.cold_email?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="flex flex-col gap-6 p-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Emails</h1>
          <p className="mt-0.5 text-sm text-muted-foreground">
            All generated cold email sequences
          </p>
        </div>
        <Input
          placeholder="Search emails…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-56 bg-card"
        />
      </div>

      {isLoading ? (
        <div className="grid grid-cols-2 gap-3">
          {[...Array(6)].map((_, i) => (
            <Skeleton key={i} className="h-32 w-full" />
          ))}
        </div>
      ) : filtered?.length === 0 ? (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center py-16 text-center">
            <Mail className="h-8 w-8 text-muted-foreground/40" />
            <p className="mt-3 text-sm text-muted-foreground">
              {search
                ? "No emails match your search"
                : "No emails generated yet — run a campaign first"}
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-2 gap-3">
          {filtered?.map((email) => (
            <EmailPreviewCard key={email.id} email={email} />
          ))}
        </div>
      )}
    </div>
  );
}
