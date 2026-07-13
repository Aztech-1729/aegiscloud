import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";

export default function PrivacyPolicyPage() {
  return (
    <div className="min-h-screen bg-background pt-24 pb-12 px-6">
      <div className="max-w-3xl mx-auto">
        <Link href="/">
          <Button variant="ghost" className="mb-8 -ml-4 text-muted-foreground">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Home
          </Button>
        </Link>
        
        <h1 className="text-4xl font-extrabold tracking-tight mb-2">Privacy Policy</h1>
        <p className="text-muted-foreground mb-8">Last updated: {new Date().toLocaleDateString()}</p>
        
        <div className="prose prose-invert prose-a:text-aegis-400 max-w-none">
          <p>
            At Aegis Cloud, we take your privacy and the security of your fleet data very seriously. 
            This Privacy Policy explains how we collect, use, and protect your information.
          </p>
          
          <h2 className="text-2xl font-bold mt-8 mb-4">1. Data Collection</h2>
          <p>
            When you install the Aegis OS Optimizer agent on your devices, we collect necessary telemetry data to provide our services. This includes:
          </p>
          <ul className="list-disc pl-6 space-y-2 my-4">
            <li>Hardware specifications (CPU, RAM, Disk)</li>
            <li>Operating system versions and configurations</li>
            <li>Real-time performance metrics</li>
            <li>Task execution logs and results</li>
          </ul>

          <h2 className="text-2xl font-bold mt-8 mb-4">2. Data Usage</h2>
          <p>
            We use the collected telemetry data strictly to power your Aegis Cloud dashboard and enable automated optimization tasks. We do not sell your data to third parties or use it for advertising purposes.
          </p>

          <h2 className="text-2xl font-bold mt-8 mb-4">3. Data Security</h2>
          <p>
            All data transmitted between the Aegis Agent and Aegis Cloud is secured using industry-standard TLS 1.3 encryption. Data at rest is encrypted using AES-256. 
          </p>

          <h2 className="text-2xl font-bold mt-8 mb-4">4. Your Rights</h2>
          <p>
            You have the right to request the deletion of your organization's data at any time. When an organization is deleted, all associated telemetry and device data is permanently purged from our systems within 30 days.
          </p>
        </div>
      </div>
    </div>
  );
}
