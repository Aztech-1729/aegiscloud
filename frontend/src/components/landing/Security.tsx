'use client';

import { Shield, Lock, Key, Eye, Server, CheckCircle2 } from 'lucide-react';

const securityFeatures = [
  {
    icon: Lock,
    title: 'End-to-End Encryption',
    description: 'All WebSocket connections use TLS 1.3 encryption. Your data is encrypted in transit and at rest.',
  },
  {
    icon: Key,
    title: 'JWT Authentication',
    description: 'Secure token-based authentication with automatic refresh, revocation, and short-lived access tokens.',
  },
  {
    icon: Shield,
    title: 'Two-Factor Authentication',
    description: 'Protect your account with TOTP-based two-factor authentication. Required for admin accounts.',
  },
  {
    icon: Eye,
    title: 'Zero Trust AI',
    description: 'The AI never executes arbitrary commands. Only pre-approved tools with strict parameter validation.',
  },
  {
    icon: Server,
    title: 'Secure Device Pairing',
    description: 'One-time pairing codes with expiration. Device tokens are cryptographically unique per installation.',
  },
  {
    icon: CheckCircle2,
    title: 'Audit Logging',
    description: 'Every action is logged with full context. IP tracking, timestamps, and tamper-proof audit trails.',
  },
];

export function LandingSecurity() {
  return (
    <section id="security" className="py-24 px-4 sm:px-6 lg:px-8 relative">
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-emerald-950/5 to-transparent" />
      <div className="max-w-7xl mx-auto relative">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">
            Security You Can{' '}
            <span className="gradient-text">Trust</span>
          </h2>
          <p className="text-lg text-muted-foreground">
            Built from the ground up with security as a first-class concern. Your devices and data are always protected.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {securityFeatures.map((feature, index) => (
            <div
              key={feature.title}
              className="group p-6 rounded-2xl border border-emerald-500/10 bg-emerald-500/5 hover:bg-emerald-500/10 transition-all duration-300 hover-lift"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <feature.icon className="h-8 w-8 text-emerald-400 mb-4" />
              <h3 className="text-lg font-semibold mb-2 text-foreground">{feature.title}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>

        <div className="mt-16 p-8 rounded-2xl border border-white/10 bg-card/30 backdrop-blur-sm">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            {[
              { value: '256-bit', label: 'AES Encryption' },
              { value: 'TLS 1.3', label: 'Transport Security' },
              { value: '99.9%', label: 'Uptime SLA' },
              { value: 'SOC 2', label: 'Compliant (Target)' },
            ].map((stat) => (
              <div key={stat.label}>
                <p className="text-2xl sm:text-3xl font-bold gradient-text">{stat.value}</p>
                <p className="text-sm text-muted-foreground mt-1">{stat.label}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
