import DocsLayout from '@/components/docs/DocsLayout';

export default function DocsPage() {
  return (
    <DocsLayout title="Aegis Cloud Documentation">
      <section className="mb-10">
        <h2 className="text-2xl font-bold mb-4">Welcome to Aegis Cloud</h2>
        <p className="text-muted-foreground leading-relaxed mb-4">
          Aegis Cloud is the centralized command center for the Aegis OS Optimizer. It allows enterprise IT administrators and power users to monitor, manage, and execute automated tasks across thousands of Windows devices simultaneously.
        </p>
        <div className="bg-aegis-500/10 border border-aegis-500/20 rounded-lg p-6 my-6">
          <h3 className="font-semibold text-aegis-400 mb-2">Core Philosophy</h3>
          <p className="text-sm text-muted-foreground">
            Aegis is built on the principle of maximum performance with minimum overhead. Our Rust-based agent uses less than 15MB of RAM while providing deep OS-level integration for telemetry, task execution, and automated remediation.
          </p>
        </div>
      </section>

      <section className="mb-10">
        <h2 className="text-2xl font-bold mb-4">Getting Started</h2>
        <h3 className="text-xl font-semibold mb-3 mt-6">1. Download the Agent</h3>
        <p className="text-muted-foreground leading-relaxed mb-4">
          The Aegis OS Optimizer must be installed on every Windows endpoint you wish to manage. You can download the latest <code>AegisSetup.exe</code> from the dashboard or the landing page.
        </p>
        
        <h3 className="text-xl font-semibold mb-3 mt-6">2. Installation & Enrollment</h3>
        <p className="text-muted-foreground leading-relaxed mb-4">
          Run the installer on the target machine. During installation, you will be prompted for your <strong>Organization ID</strong> and <strong>Enrollment Token</strong>. These can be generated from the <a href="/dashboard/organizations" className="text-aegis-400 hover:underline">Organizations Dashboard</a>.
        </p>
        
        <div className="bg-secondary/50 rounded-lg p-4 font-mono text-sm my-4 border border-border">
          C:\&gt; AegisSetup.exe /SILENT /ORG="org_123" /TOKEN="tok_abc"
        </div>
      </section>

      <section className="mb-10">
        <h2 className="text-2xl font-bold mb-4">Core Capabilities</h2>
        <ul className="space-y-4 text-muted-foreground">
          <li>
            <strong className="text-foreground">Live Telemetry:</strong> View real-time CPU, RAM, Disk, and Network utilization across your entire fleet with sub-second latency via WebSockets.
          </li>
          <li>
            <strong className="text-foreground">Task Automation:</strong> Deploy batch scripts, PowerShell commands, and predefined optimization routines to single devices or entire device groups.
          </li>
          <li>
            <strong className="text-foreground">Security Policies:</strong> Enforce baseline configurations, monitor for unauthorized changes, and automatically remediate drift.
          </li>
        </ul>
      </section>
    </DocsLayout>
  );
}
