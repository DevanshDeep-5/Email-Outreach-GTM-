"use client";

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { Loader2, ArrowUp, ArrowDown, Plus, Trash2, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { campaignsApi } from "@/lib/api";

const FUNDING_STAGES = [
  "seed",
  "series_a",
  "series_b",
  "series_c",
  "series_d",
  "ipo",
  "private",
];

const EMPLOYEE_RANGES = [
  { label: "1–10", min: 1, max: 10 },
  { label: "11–50", min: 11, max: 50 },
  { label: "51–200", min: 51, max: 200 },
  { label: "201–500", min: 201, max: 500 },
  { label: "501–1000", min: 501, max: 1000 },
  { label: "1001–5000", min: 1001, max: 5000 },
  { label: "5000+", min: 5000, max: 100000 },
];

function parseKeywords(raw: string): string[] {
  return raw
    .split(",")
    .map((k) => k.trim())
    .filter(Boolean);
}

interface FieldProps {
  label: string;
  error?: string;
  children: React.ReactNode;
  hint?: string;
}

function Field({ label, error, children, hint }: FieldProps) {
  return (
    <div className="flex flex-col gap-1.5">
      <Label className="text-xs font-medium text-foreground">{label}</Label>
      {children}
      {hint && <p className="text-xs text-muted-foreground">{hint}</p>}
      {error && <p className="text-xs text-red-400">{error}</p>}
    </div>
  );
}

export function CampaignForm() {
  const router = useRouter();
  const queryClient = useQueryClient();

  const [name, setName] = useState("");
  const [industry, setIndustry] = useState("");
  const [country, setCountry] = useState("");
  const [employeeRange, setEmployeeRange] = useState<{ min: number; max: number } | null>(null);
  const [fundingStage, setFundingStage] = useState("");
  const [hiringKeywords, setHiringKeywords] = useState("");
  const [techKeywords, setTechKeywords] = useState("");
  const [companyKeywords, setCompanyKeywords] = useState("");
  const [excludeKeywords, setExcludeKeywords] = useState("");
  const [targetPersonas, setTargetPersonas] = useState<string[]>([
    "Founder",
    "CEO",
    "VP Sales",
    "Head of Sales",
    "Revenue Operations",
    "Growth Lead",
    "Marketing Director",
    "Director of Sales",
    "Sales Manager",
  ]);
  const [newPersona, setNewPersona] = useState("");
  const [numLeads, setNumLeads] = useState<number | "">(10);
  const [nameError, setNameError] = useState("");

  const addPersona = () => {
    if (newPersona.trim() && !targetPersonas.includes(newPersona.trim())) {
      setTargetPersonas([...targetPersonas, newPersona.trim()]);
      setNewPersona("");
    }
  };

  const removePersona = (index: number) => {
    setTargetPersonas(targetPersonas.filter((_, i) => i !== index));
  };

  const moveUp = (index: number) => {
    if (index === 0) return;
    const updated = [...targetPersonas];
    const temp = updated[index];
    updated[index] = updated[index - 1];
    updated[index - 1] = temp;
    setTargetPersonas(updated);
  };

  const moveDown = (index: number) => {
    if (index === targetPersonas.length - 1) return;
    const updated = [...targetPersonas];
    const temp = updated[index];
    updated[index] = updated[index + 1];
    updated[index + 1] = temp;
    setTargetPersonas(updated);
  };

  const mutation = useMutation({
    mutationFn: () => {
      if (!name.trim()) {
        setNameError("Campaign name is required");
        throw new Error("Validation failed");
      }
      setNameError("");

      return campaignsApi.create({
        name: name.trim(),
        industry: industry || undefined,
        country: country || undefined,
        employee_min: employeeRange?.min,
        employee_max: employeeRange?.max,
        funding_stage: fundingStage || undefined,
        hiring_keywords: parseKeywords(hiringKeywords),
        technology_keywords: parseKeywords(techKeywords),
        company_keywords: parseKeywords(companyKeywords),
        exclude_keywords: parseKeywords(excludeKeywords),
        target_personas: targetPersonas,
        num_leads: numLeads === "" || numLeads <= 0 ? 10 : numLeads,
      });
    },
    onSuccess: (campaign) => {
      queryClient.invalidateQueries({ queryKey: ["campaigns"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      router.push(`/campaigns/${campaign.id}`);
    },
  });

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        mutation.mutate();
      }}
      className="space-y-6"
    >
      {/* Campaign Name */}
      <Field label="Campaign Name *" error={nameError}>
        <Input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Q3 SaaS Outbound — VP Sales"
          className="bg-card"
        />
      </Field>

      {/* Targeting */}
      <div className="rounded-lg border border-border p-4 space-y-4">
        <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          ICP Targeting
        </p>

        <div className="grid grid-cols-2 gap-4">
          <Field label="Industry">
            <Input
              value={industry}
              onChange={(e) => setIndustry(e.target.value)}
              placeholder="SaaS, Fintech, Healthcare…"
              className="bg-card"
            />
          </Field>

          <Field label="Country">
            <Input
              value={country}
              onChange={(e) => setCountry(e.target.value)}
              placeholder="United States"
              className="bg-card"
            />
          </Field>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <Field label="Employee Range">
            <Select
              onValueChange={(v) => {
                const range = EMPLOYEE_RANGES.find((r) => r.label === v);
                if (range) setEmployeeRange({ min: range.min, max: range.max });
              }}
            >
              <SelectTrigger className="bg-card">
                <SelectValue placeholder="Any size" />
              </SelectTrigger>
              <SelectContent>
                {EMPLOYEE_RANGES.map((r) => (
                  <SelectItem key={r.label} value={r.label}>
                    {r.label} employees
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </Field>

          <Field label="Funding Stage">
            <Select onValueChange={setFundingStage}>
              <SelectTrigger className="bg-card">
                <SelectValue placeholder="Any stage" />
              </SelectTrigger>
              <SelectContent>
                {FUNDING_STAGES.map((s) => (
                  <SelectItem key={s} value={s}>
                    {s.replace("_", " ").replace(/\b\w/g, (c) => c.toUpperCase())}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </Field>
        </div>
      </div>

      {/* Target Personas */}
      <div className="rounded-lg border border-border p-4 space-y-4">
        <div className="flex items-center justify-between">
          <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Target Personas
          </p>
          <span className="text-xs text-muted-foreground">Priority Order (Top to Bottom)</span>
        </div>

        {/* Add Persona Form */}
        <div className="flex gap-2">
          <Input
            value={newPersona}
            onChange={(e) => setNewPersona(e.target.value)}
            placeholder="Add custom persona (e.g., VP Product)..."
            className="bg-card flex-1"
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault();
                addPersona();
              }
            }}
          />
          <Button
            type="button"
            onClick={addPersona}
            size="sm"
            className="shrink-0 bg-primary/10 hover:bg-primary/20 text-primary border border-primary/20 flex gap-1 items-center"
          >
            <Plus className="h-4 w-4" /> Add
          </Button>
        </div>

        {/* List of personas */}
        <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
          {targetPersonas.map((persona, index) => (
            <div
              key={persona}
              className="flex items-center justify-between rounded-md border border-border bg-card/50 px-3 py-1.5 text-sm"
            >
              <span className="font-medium text-foreground">{persona}</span>
              <div className="flex items-center gap-1.5">
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => moveUp(index)}
                  disabled={index === 0}
                  className="h-7 w-7 p-0"
                >
                  <ArrowUp className="h-3.5 w-3.5" />
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => moveDown(index)}
                  disabled={index === targetPersonas.length - 1}
                  className="h-7 w-7 p-0"
                >
                  <ArrowDown className="h-3.5 w-3.5" />
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => removePersona(index)}
                  className="h-7 w-7 p-0 text-red-400 hover:text-red-300 hover:bg-red-950/20"
                >
                  <X className="h-3.5 w-3.5" />
                </Button>
              </div>
            </div>
          ))}
          {targetPersonas.length === 0 && (
            <p className="text-center text-xs text-muted-foreground py-4">
              No target personas specified. Defaulting to all common sales roles.
            </p>
          )}
        </div>
      </div>

      {/* Keywords */}
      <div className="rounded-lg border border-border p-4 space-y-4">
        <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          Keywords
        </p>

        <Field
          label="Hiring Keywords"
          hint="Comma-separated — e.g. sales, SDR, revenue"
        >
          <Textarea
            value={hiringKeywords}
            onChange={(e) => setHiringKeywords(e.target.value)}
            placeholder="sales, SDR, business development, revenue"
            className="bg-card h-16 resize-none"
          />
        </Field>

        <Field
          label="Technology Keywords"
          hint="Technologies your ICP uses — e.g. Salesforce, HubSpot"
        >
          <Textarea
            value={techKeywords}
            onChange={(e) => setTechKeywords(e.target.value)}
            placeholder="HubSpot, Salesforce, Outreach, Apollo"
            className="bg-card h-16 resize-none"
          />
        </Field>

        <Field
          label="Company Keywords"
          hint="Keywords describing the company type"
        >
          <Textarea
            value={companyKeywords}
            onChange={(e) => setCompanyKeywords(e.target.value)}
            placeholder="outbound, growth, pipeline, B2B"
            className="bg-card h-16 resize-none"
          />
        </Field>

        <Field
          label="Exclude Keywords"
          hint="Companies matching these will be skipped"
        >
          <Textarea
            value={excludeKeywords}
            onChange={(e) => setExcludeKeywords(e.target.value)}
            placeholder="agency, consulting, freelance"
            className="bg-card h-16 resize-none"
          />
        </Field>
      </div>

      {/* Number of Leads */}
      <div className="rounded-lg border border-primary/30 bg-primary/5 p-4">
        <Field
          label="Number of Leads *"
          hint="The workflow will stop after collecting exactly this many companies."
        >
          <Input
            type="number"
            min={1}
            max={100}
            value={numLeads}
            onChange={(e) => {
              const val = e.target.value;
              if (val === "") {
                setNumLeads("");
                return;
              }
              const parsed = parseInt(val, 10);
              if (!isNaN(parsed)) {
                setNumLeads(parsed <= 0 ? "" : parsed);
              }
            }}
            className="bg-card w-40"
          />
        </Field>
      </div>

      {mutation.isError && (
        <p className="text-sm text-red-400">
          Failed to create campaign. Check your API connection.
        </p>
      )}

      <Button type="submit" disabled={mutation.isPending} className="w-full">
        {mutation.isPending ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Creating Campaign…
          </>
        ) : (
          "Create Campaign & Start Workflow"
        )}
      </Button>
    </form>
  );
}
