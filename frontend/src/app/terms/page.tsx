import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";

export default function TermsOfServicePage() {
  return (
    <div className="min-h-screen bg-background pt-24 pb-12 px-6">
      <div className="max-w-3xl mx-auto">
        <Link href="/">
          <Button variant="ghost" className="mb-8 -ml-4 text-muted-foreground">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Home
          </Button>
        </Link>
        
        <h1 className="text-4xl font-extrabold tracking-tight mb-2">Terms of Service</h1>
        <p className="text-muted-foreground mb-8">Last updated: {new Date().toLocaleDateString()}</p>
        
        <div className="prose prose-invert prose-a:text-aegis-400 max-w-none">
          <p>
            By accessing or using Aegis Cloud and the Aegis OS Optimizer agent, you agree to be bound by these Terms of Service.
          </p>
          
          <h2 className="text-2xl font-bold mt-8 mb-4">1. License and Usage</h2>
          <p>
            Aegis Cloud grants you a limited, non-exclusive, non-transferable license to use our services in accordance with your subscription plan. You may not reverse engineer, decompile, or attempt to extract the source code of the Aegis Agent.
          </p>

          <h2 className="text-2xl font-bold mt-8 mb-4">2. Account Responsibilities</h2>
          <p>
            You are entirely responsible for maintaining the security of your account credentials and API keys. Aegis Cloud allows you to execute remote commands on your devices; you are solely responsible for any damage caused by tasks or scripts you execute through our platform.
          </p>

          <h2 className="text-2xl font-bold mt-8 mb-4">3. Acceptable Use</h2>
          <p>
            You agree not to use Aegis Cloud to:
          </p>
          <ul className="list-disc pl-6 space-y-2 my-4">
            <li>Deploy malware, ransomware, or unauthorized software</li>
            <li>Manage devices you do not own or have explicit permission to manage</li>
            <li>Attempt to bypass our rate limits or infrastructure security</li>
          </ul>

          <h2 className="text-2xl font-bold mt-8 mb-4">4. Limitation of Liability</h2>
          <p>
            Aegis Cloud is provided "as is" without warranties of any kind. In no event shall we be liable for any indirect, incidental, special, or consequential damages arising out of or in connection with your use of the service.
          </p>
        </div>
      </div>
    </div>
  );
}
