import axios from "axios";
import type {
  Campaign,
  CampaignStats,
  CampaignFormData,
  Company,
  CompanyDetail,
  Contact,
  Email,
  Export,
  DashboardStats,
} from "@/types";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  headers: { "Content-Type": "application/json" },
});

// ─── Campaigns ───────────────────────────────────────────────────────────────

export const campaignsApi = {
  list: () => api.get<Campaign[]>("/api/campaigns/").then((r) => r.data),

  get: (id: string) =>
    api.get<CampaignStats>(`/api/campaigns/${id}`).then((r) => r.data),

  create: (data: {
    name: string;
    industry?: string;
    country?: string;
    employee_min?: number | null;
    employee_max?: number | null;
    funding_stage?: string;
    hiring_keywords: string[];
    technology_keywords: string[];
    company_keywords: string[];
    exclude_keywords: string[];
    target_personas: string[];
    num_leads: number;
  }) => api.post<Campaign>("/api/campaigns/", data).then((r) => r.data),

  delete: (id: string) => api.delete(`/api/campaigns/${id}`).then((r) => r.data),

  dashboard: () =>
    api.get<DashboardStats>("/api/campaigns/dashboard").then((r) => r.data),
};

// ─── Companies ───────────────────────────────────────────────────────────────

export const companiesApi = {
  list: (campaignId?: string) =>
    api
      .get<Company[]>("/api/companies/", {
        params: campaignId ? { campaign_id: campaignId } : undefined,
      })
      .then((r) => r.data),

  get: (id: string) =>
    api.get<CompanyDetail>(`/api/companies/${id}`).then((r) => r.data),
};

// ─── Emails ──────────────────────────────────────────────────────────────────

export const emailsApi = {
  list: (params?: { campaign_id?: string; company_id?: string }) =>
    api.get<Email[]>("/api/emails/", { params }).then((r) => r.data),

  get: (id: string) => api.get<Email>(`/api/emails/${id}`).then((r) => r.data),

  update: (id: string, data: Partial<Email>) =>
    api.put<Email>(`/api/emails/${id}`, data).then((r) => r.data),

  regenerate: (id: string) =>
    api.post<Email>(`/api/emails/${id}/regenerate`).then((r) => r.data),
};

// ─── Exports ─────────────────────────────────────────────────────────────────

export const exportsApi = {
  list: () => api.get<Export[]>("/api/exports/").then((r) => r.data),

  byCampaign: (campaignId: string) =>
    api
      .get<Export[]>(`/api/exports/campaign/${campaignId}`)
      .then((r) => r.data),

  downloadUrl: (exportId: string) =>
    `${api.defaults.baseURL}/api/exports/${exportId}/download`,
};
