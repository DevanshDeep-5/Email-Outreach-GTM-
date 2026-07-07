import { CampaignForm } from "@/components/campaigns/CampaignForm";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function NewCampaignPage() {
  return (
    <div className="mx-auto max-w-2xl p-8">
      <div className="mb-6 flex items-center gap-3">
        <Button asChild variant="ghost" size="sm" className="text-muted-foreground">
          <Link href="/campaigns">
            <ArrowLeft className="mr-1.5 h-4 w-4" />
            Back
          </Link>
        </Button>
      </div>

      <div className="mb-8">
        <h1 className="text-xl font-semibold">New Campaign</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Define your ICP parameters. The AI workflow will start automatically
          after you submit.
        </p>
      </div>

      <CampaignForm />
    </div>
  );
}
