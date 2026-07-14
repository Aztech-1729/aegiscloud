import Link from 'next/link';
import { 
  Monitor, Shield, Brain, Zap, HardDrive, Activity,
  Terminal, FolderOpen, ListTodo, Bell, Lock, Cloud,
  CheckCircle2, ArrowRight, Users, Globe, Cpu, Wifi
} from 'lucide-react';

export const metadata = {
  title: 'Features - AI-Powered Windows Endpoint Management',
  description: 'Discover powerful features for remote Windows management. AI assistant, real-time monitoring, automation, file management, and enterprise-grade security.',
  keywords: 'windows management features, remote pc management tools, endpoint management capabilities',
};

export default function FeaturesPage() {
  const features = [
    {
      icon: Brain,
      title: 'AI-Powered Assistant',
      description: 'Natural language commands to manage your Windows PCs. The AI uses only pre-approved tools for safety and reliability.',
      benefits: [
        'Natural language interface',
        'Smart task suggestions',
        'Context-aware responses',
        'Continuous learning',
      ],
      color: 'from-purple-500 to-pink-500',
    },
    {
      icon: Monitor,
      title: 'Real-Time Monitoring',
      description: 'Live CPU, RAM, GPU, disk, network, and battery stats with auto-refresh. See everything at a glance.',
      benefits: [
        'Live system metrics',
        'Performance graphs',
        'Custom dashboards',
        'Historical data',
      ],
      color: 'from-blue-500 to-cyan-500',
    },
    {
      icon: Shield,
      title: 'Enterprise Security',
      description: 'End-to-end encryption, JWT auth, 2FA, RBAC, and secure device pairing. Your data is always protected.',
      benefits: [
        'TLS 1.3 encryption',
        'Two-factor authentication',
        'Role-based access control',
        'Complete audit logs',
      ],
      color: 'from-emerald-500 to-teal-500',
    },
    {
      icon: FolderOpen,
      title: 'File Management',
      description: 'Browse, upload, download, rename, and organize files on your remote Windows PCs from the browser.',
      benefits: [
        'Remote file browser',
        'Drag-and-drop upload',
        'File preview',
        'Bulk operations',
      ],
      color: 'from-orange-500 to-red-500',
    },
    {
      icon: Zap,
      title: 'Instant Tasks',
      description: 'Run approved operations like cleanup, process management, service control, and system maintenance instantly.',
      benefits: [
        'One-click execution',
        'Task progress tracking',
        'Automatic retry',
        'Detailed logs',
      ],
      color: 'from-yellow-500 to-orange-500',
    },
    {
      icon: Cloud,
      title: 'Auto-Connect',
      description: 'Pair once, connect forever. The lightweight Windows agent starts with your system and reconnects automatically.',
      benefits: [
        'Zero configuration',
        'Auto-reconnect',
        'Offline support',
        'Seamless updates',
      ],
      color: 'from-indigo-500 to-purple-500',
    },
    {
      icon: ListTodo,
      title: 'Complete History',
      description: 'Full audit trail of every action, task, and connection. Search, filter, and export for compliance needs.',
      benefits: [
        'Detailed activity logs',
        'Advanced search',
        'Export capabilities',
        'Compliance ready',
      ],
      color: 'from-pink-500 to-rose-500',
    },
    {
      icon: Lock,
      title: 'Zero Trust Architecture',
      description: 'The AI never executes arbitrary commands. Only pre-approved tools exposed by the agent can run on your system.',
      benefits: [
        'Pre-approved tools only',
        'No arbitrary commands',
        'Sandboxed execution',
        'Security by design',
      ],
      color: 'from-red-500 to-pink-500',
    },
    {
      icon: Cpu,
      title: 'Lightweight Agent',
      description: 'Built in Rust for minimal resource usage. Runs as a Windows service with auto-updates and crash recovery.',
      benefits: [
        '< 20MB RAM usage',
        '< 1% CPU usage',
        'Auto-updates',
        'Crash recovery',
      ],
      color: 'from-violet-500 to-purple-500',
    },
    {
      icon: Terminal,
      title: 'Remote Terminal',
      description: 'Secure browser-based terminal with PTY support. Execute commands with full audit logging.',
      benefits: [
        'Browser-based access',
        'Full terminal emulation',
        'Session recording',
        'Access control',
      ],
      color: 'from-slate-500 to-gray-500',
    },
    {
      icon: Activity,
      title: 'Automation',
      description: 'Schedule tasks, create workflows, and automate routine maintenance. Set it and forget it.',
      benefits: [
        'Task scheduling',
        'Workflow automation',
        'Event triggers',
        'Custom scripts',
      ],
      color: 'from-cyan-500 to-blue-500',
    },
    {
      icon: Bell,
      title: 'Smart Notifications',
      description: 'Get alerted about important events. Customizable notifications via email, browser, and mobile.',
      benefits: [
        'Custom alerts',
        'Multiple channels',
        'Smart filtering',
        'Escalation rules',
      ],
      color: 'from-amber-500 to-yellow-500',
    },
  ];

  const stats = [
    { icon: Users, value: '10,000+', label: 'Active Users' },
    { icon: Monitor, value: '50,000+', label: 'Devices Managed' },
    { icon: Globe, value: '150+', label: 'Countries' },
    { icon: CheckCircle2, value: '99.99%', label: 'Uptime' },
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-16">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-4xl sm:text-5xl font-bold mb-4">
              Powerful Features for{' '}
              <span className="gradient-text">Remote Management</span>
            </h1>
            <p className="text-xl text-muted-foreground">
              Everything you need to manage Windows PCs from anywhere. Secure, fast, and intelligent.
            </p>
          </div>
        </div>
      </header>

      {/* Stats */}
      <section className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-5xl mx-auto">
          {stats.map((stat, index) => (
            <div key={index} className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-aegis-500/10 mb-4">
                <stat.icon className="h-8 w-8 text-aegis-400" />
              </div>
              <div className="text-3xl font-bold mb-1">{stat.value}</div>
              <div className="text-sm text-muted-foreground">{stat.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features Grid */}
      <section className="container mx-auto px-4 py-12">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className="group bg-card border border-border rounded-xl p-6 hover:shadow-xl transition-all duration-300"
              >
                <div className={`inline-flex items-center justify-center w-14 h-14 rounded-xl bg-gradient-to-br ${feature.color} mb-4`}>
                  <feature.icon className="h-7 w-7 text-white" />
                </div>

                <h3 className="text-xl font-bold mb-3 group-hover:text-aegis-400 transition-colors">
                  {feature.title}
                </h3>

                <p className="text-muted-foreground mb-4">
                  {feature.description}
                </p>

                <ul className="space-y-2">
                  {feature.benefits.map((benefit, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm">
                      <CheckCircle2 className="h-4 w-4 text-green-500 flex-shrink-0 mt-0.5" />
                      <span className="text-muted-foreground">{benefit}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Detailed Feature Sections */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-7xl mx-auto space-y-24">
          {/* AI Assistant */}
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <div className="inline-flex items-center justify-center w-14 h-14 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 mb-4">
                <Brain className="h-7 w-7 text-white" />
              </div>
              <h2 className="text-3xl font-bold mb-4">
                AI Assistant That Understands You
              </h2>
              <p className="text-lg text-muted-foreground mb-6">
                Just tell Aegis Cloud what you want to do in plain English. The AI understands your intent and executes the right commands safely.
              </p>
              <ul className="space-y-3">
                {[
                  'Natural language commands',
                  'Context-aware responses',
                  'Smart task suggestions',
                  'Continuous learning from your usage',
                ].map((item, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <CheckCircle2 className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="bg-card border border-border rounded-xl p-6">
              <div className="space-y-3">
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-full bg-aegis-500/20 flex items-center justify-center flex-shrink-0">
                    <span className="text-sm">👤</span>
                  </div>
                  <div className="flex-1 bg-secondary rounded-lg p-3">
                    <p className="text-sm">My PC is running slow, can you help?</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-full bg-purple-500/20 flex items-center justify-center flex-shrink-0">
                    <Brain className="h-4 w-4 text-purple-400" />
                  </div>
                  <div className="flex-1 bg-purple-500/10 rounded-lg p-3">
                    <p className="text-sm mb-2">I'll help diagnose the issue. Let me check your system performance.</p>
                    <div className="space-y-1 text-xs text-muted-foreground">
                      <div>✓ Checking CPU usage</div>
                      <div>✓ Checking RAM usage</div>
                      <div>✓ Checking disk usage</div>
                      <div>✓ Analyzing running processes</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Security */}
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div className="order-2 md:order-1 bg-card border border-border rounded-xl p-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-emerald-500/10 rounded-lg">
                  <div className="flex items-center gap-2">
                    <Lock className="h-5 w-5 text-emerald-500" />
                    <span className="font-medium">End-to-End Encryption</span>
                  </div>
                  <CheckCircle2 className="h-5 w-5 text-emerald-500" />
                </div>
                <div className="flex items-center justify-between p-3 bg-emerald-500/10 rounded-lg">
                  <div className="flex items-center gap-2">
                    <Shield className="h-5 w-5 text-emerald-500" />
                    <span className="font-medium">Two-Factor Auth</span>
                  </div>
                  <CheckCircle2 className="h-5 w-5 text-emerald-500" />
                </div>
                <div className="flex items-center justify-between p-3 bg-emerald-500/10 rounded-lg">
                  <div className="flex items-center gap-2">
                    <Users className="h-5 w-5 text-emerald-500" />
                    <span className="font-medium">Role-Based Access</span>
                  </div>
                  <CheckCircle2 className="h-5 w-5 text-emerald-500" />
                </div>
                <div className="flex items-center justify-between p-3 bg-emerald-500/10 rounded-lg">
                  <div className="flex items-center gap-2">
                    <Activity className="h-5 w-5 text-emerald-500" />
                    <span className="font-medium">Audit Logging</span>
                  </div>
                  <CheckCircle2 className="h-5 w-5 text-emerald-500" />
                </div>
              </div>
            </div>
            <div className="order-1 md:order-2">
              <div className="inline-flex items-center justify-center w-14 h-14 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-500 mb-4">
                <Shield className="h-7 w-7 text-white" />
              </div>
              <h2 className="text-3xl font-bold mb-4">
                Enterprise-Grade Security
              </h2>
              <p className="text-lg text-muted-foreground mb-6">
                Your data and devices are protected with multiple layers of security. From encryption to access control, we've got you covered.
              </p>
              <ul className="space-y-3">
                {[
                  'TLS 1.3 encryption for all connections',
                  'JWT tokens with automatic refresh',
                  'Two-factor authentication (TOTP)',
                  'Role-based access control (RBAC)',
                  'Complete audit trail',
                  'Secure device pairing',
                ].map((item, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <CheckCircle2 className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Automation */}
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <div className="inline-flex items-center justify-center w-14 h-14 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-500 mb-4">
                <Zap className="h-7 w-7 text-white" />
              </div>
              <h2 className="text-3xl font-bold mb-4">
                Automate Everything
              </h2>
              <p className="text-lg text-muted-foreground mb-6">
                Schedule tasks, create workflows, and let Aegis Cloud handle routine maintenance automatically. Set it once, run it forever.
              </p>
              <ul className="space-y-3">
                {[
                  'Schedule recurring maintenance',
                  'Create custom workflows',
                  'Event-triggered automation',
                  'Batch operations across devices',
                  'Automated reporting',
                  'Smart error handling',
                ].map((item, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <CheckCircle2 className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="bg-card border border-border rounded-xl p-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-border">
                  <span className="font-semibold">Scheduled Tasks</span>
                  <button className="text-sm text-aegis-400 hover:text-aegis-300">+ Add Task</button>
                </div>
                {[
                  { name: 'Weekly Cleanup', schedule: 'Every Sunday 2:00 AM', status: 'Active' },
                  { name: 'Daily Health Check', schedule: 'Every day 6:00 AM', status: 'Active' },
                  { name: 'Monthly Updates', schedule: '1st of month 3:00 AM', status: 'Active' },
                ].map((task, i) => (
                  <div key={i} className="flex items-center justify-between p-3 bg-secondary/50 rounded-lg">
                    <div>
                      <div className="font-medium text-sm">{task.name}</div>
                      <div className="text-xs text-muted-foreground">{task.schedule}</div>
                    </div>
                    <span className="text-xs px-2 py-1 bg-emerald-500/10 text-emerald-400 rounded-full">
                      {task.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto bg-gradient-to-br from-aegis-500/10 to-purple-500/10 rounded-2xl p-12 text-center">
          <h2 className="text-3xl font-bold mb-4">
            Ready to Experience These Features?
          </h2>
          <p className="text-lg text-muted-foreground mb-8">
            Start managing your Windows PCs remotely with Aegis Cloud. Free to get started.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/auth/register"
              className="inline-flex items-center gap-2 px-8 py-3 bg-aegis-600 text-white rounded-lg font-medium hover:bg-aegis-700 transition-colors"
            >
              Get Started Free
              <ArrowRight className="h-5 w-5" />
            </Link>
            <Link
              href="/pricing"
              className="inline-flex items-center gap-2 px-8 py-3 bg-card border border-border rounded-lg font-medium hover:bg-accent transition-colors"
            >
              View Pricing
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border bg-card/50 backdrop-blur-sm mt-16">
        <div className="container mx-auto px-4 py-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-sm text-muted-foreground">
              © 2026 Aegis Cloud. All rights reserved.
            </p>
            <div className="flex items-center gap-6">
              <Link href="/terms" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                Terms
              </Link>
              <Link href="/privacy" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                Privacy
              </Link>
              <Link href="/contact" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                Contact
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
