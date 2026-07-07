// Shared TypeScript types matching backend Pydantic schemas

export type CampaignStatus = "pending" | "running" | "completed" | "failed";

export interface Campaign {
  id: string;
  name: string;
  industry: string | null;
  country: string | null;
  employee_min: number | null;
  employee_max: number | null;
  funding_stage: string | null;
  hiring_keywords: string[];
  technology_keywords: string[];
  company_keywords: string[];
  exclude_keywords: string[];
  target_personas: string[];
  num_leads: number;
  status: CampaignStatus;
  current_node: string | null;
  error_message: string | null;
  created_at: string;
}

export interface CampaignStats {
  campaign: Campaign;
  companies_found: number;
  companies_processed: number;
  contacts_found: number;
  emails_generated: number;
  export_ready: boolean;
}

export interface Company {
  id: string;
  campaign_id: string;
  name: string;
  website: string | null;
  industry: string | null;
  employee_count: number | null;
  funding_stage: string | null;
  provider_id: string | null;
  created_at: string;
}

export interface Research {
  id: string;
  company_id: string;
  website_content: string | null;
  tavily_summary: string | null;
  recent_news: string | null;
  company_summary: string | null;
  products: string | null;
  business_model: string | null;
  target_market: string | null;
  pain_points: string | null;
  growth_signals: string | null;
  sales_opportunities: string | null;
  outreach_angle: string | null;
  value_proposition: string | null;
  created_at: string;
}

export interface IntentScore {
  id: string;
  company_id: string;
  score: number;
  reasoning: string | null;
  signals: string[];
  created_at: string;
}

export interface Contact {
  id: string;
  company_id: string;
  name: string | null;
  title: string | null;
  department: string | null;
  seniority: string | null;
  email: string | null;
  email_verified: boolean | null;
  verification_source: string | null;
  confidence_score: number | null;
  data_source: string | null;
  linkedin_url: string | null;
  created_at: string;
}

export interface Email {
  id: string;
  company_id: string;
  contact_id: string | null;
  subject: string | null;
  cold_email: string | null;
  cta: string | null;
  follow_up_1: string | null;
  follow_up_2: string | null;
  break_up_email: string | null;
  personalization_notes: string | null;
  created_at: string;
}

export interface Export {
  id: string;
  campaign_id: string;
  file_path: string | null;
  row_count: number | null;
  created_at: string;
}

export interface CompanyDetail {
  company: Company;
  research: Research | null;
  intent_score: IntentScore | null;
  contacts: Contact[];
  emails: Email[];
}

export interface DashboardStats {
  total_campaigns: number;
  total_companies: number;
  total_contacts: number;
  total_emails: number;
  export_count: number;
  recent_campaigns: Campaign[];
}

export interface CampaignFormData {
  name: string;
  industry: string;
  country: string;
  employee_min: number | null;
  employee_max: number | null;
  funding_stage: string;
  hiring_keywords: string;
  technology_keywords: string;
  company_keywords: string;
  exclude_keywords: string;
  target_personas: string[];
  num_leads: number;
}
