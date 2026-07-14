import Link from 'next/link';
import { Shield, Lock, Key, FileCheck, Server, Eye, Award, AlertTriangle } from 'lucide-react';

export const metadata = {
  title: 'Security - Enterprise-Grade Protection for Your Data',
  description: 'Learn about Aegis Cloud security features, encryption, compliance certifications, and how we protect your Windows endpoint data.',
  keywords: 'windows management security, endpoint security, enterprise data protection',
};

export default function SecurityPage() {
  const securityFeatures = [
    {
      icon: Lock,
      title: 'End-to-End Encryption',
      description: 'All data is encrypted in transit using TLS 1.3 and at rest using AES-256 encryption.',
      details: [
        'TLS 1.3 for all WebSocket connections',
        'AES-256 encryption for data at rest',
        'Perfect forward secrecy',
        'Certificate pinning support',
      ],
    },
    {
      icon: Key,
      title: 'Authentication & Authorization',
      description: 'Multiple layers of authentication with role-based access control.',
      details: [
        'JWT tokens with automatic refresh',
        'Two-factor authentication (TOTP)',
        'Role-based access control (RBAC)',
        'API key authentication',
      ],
    },
    {
      icon: Shield,
      title: 'Zero-Trust Architecture',
      description: 'Never trust, always verify. Every request is authenticated and authorized.',
      details: [
        'Pre-approved tools only',
        'No arbitrary command execution',
        'Sandboxed execution environment',
        'Continuous verification',
      ],
    },
    {
      icon: Eye,
      title: 'Audit & Monitoring',
      description: 'Complete visibility into all actions with detailed audit logging.',
      details: [
        'Comprehensive audit logs',
        'Real-time monitoring',
        'Anomaly detection',
        'Automated alerts',
      ],
    },
    {
      icon: Server,
      title: 'Infrastructure Security',
      description: 'Enterprise-grade infrastructure with multiple security layers.',
      details: [
        'Isolated network segments',
        'DDoS protection',
        'Firewall rules',
        'Regular security audits',
      ],
    },
    {
      icon: FileCheck,
      title: 'Compliance & Certifications',
      description: 'Meeting industry standards and regulatory requirements.',
      details: [
        'SOC 2 Type II (Target)',
        'GDPR compliant',
        'ISO 27001 (Target)',
        'HIPAA ready',
      ],
    },
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-16">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-4xl sm:text-5xl font-bold mb-4">
              Enterprise-Grade Security
            </h1>
            <p className="text-xl text-muted-foreground">
              Your data and devices are protected with multiple layers of security. From encryption to access control, we've got you covered.
            </p>
          </div>
        </div>
      </header>

      {/* Security Overview */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-4 gap-6 mb-16">
            {[
              { value: '256-bit', label: 'AES Encryption' },
              { value: 'TLS 1.3', label: 'Transport Security' },
              { value: '99.99%', label: 'Uptime SLA' },
              { value: '24/7', label: 'Security Monitoring' },
            ].map((stat, index) => (
              <div key={index} className="bg-card border border-border rounded-xl p-6 text-center">
                <div className="text-3xl font-bold text-aegis-400 mb-2">{stat.value}</div>
                <div className="text-sm text-muted-foreground">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Security Features */}
      <section className="container mx-auto px-4 py-16 bg-card/30">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold mb-12 text-center">Security Features</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {securityFeatures.map((feature, index) => (
              <div key={index} className="bg-card border border-border rounded-xl p-6">
                <div className="inline-flex items-center justify-center w-14 h-14 rounded-xl bg-aegis-500/10 mb-4">
                  <feature.icon className="h-7 w-7 text-aegis-400" />
                </div>
                <h3 className="text-xl font-bold mb-3">{feature.title}</h3>
                <p className="text-muted-foreground mb-4">{feature.description}</p>
                <ul className="space-y-2">
                  {feature.details.map((detail, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm">
                      <div className="w-1.5 h-1.5 rounded-full bg-aegis-400 mt-1.5 flex-shrink-0" />
                      <span className="text-muted-foreground">{detail}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Security Practices */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold mb-12 text-center">Our Security Practices</h2>
          <div className="space-y-8">
            {[
              {
                title: 'Regular Security Audits',
                description: 'We conduct regular security audits and penetration testing to identify and address potential vulnerabilities.',
              },
              {
                title: 'Vulnerability Management',
                description: 'We maintain a comprehensive vulnerability management program with regular patching and updates.',
              },
              {
                title: 'Incident Response',
                description: 'Our dedicated security team is available 24/7 to respond to security incidents and threats.',
              },
              {
                title: 'Employee Training',
                description: 'All employees receive regular security training and must follow strict security protocols.',
              },
              {
                title: 'Data Backup & Recovery',
                description: 'We maintain multiple encrypted backups with tested recovery procedures to ensure data availability.',
              },
              {
                title: 'Access Control',
                description: 'We follow the principle of least privilege, ensuring users only have access to what they need.',
              },
            ].map((practice, index) => (
              <div key={index} className="flex items-start gap-4">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-aegis-500/10 flex items-center justify-center">
                  <div className="w-2 h-2 rounded-full bg-aegis-400" />
                </div>
                <div>
                  <h3 className="text-xl font-bold mb-2">{practice.title}</h3>
                  <p className="text-muted-foreground">{practice.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Responsible Disclosure */}
      <section className="container mx-auto px-4 py-16 bg-card/30">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-amber-500/10 mb-4">
            <AlertTriangle className="h-8 w-8 text-amber-400" />
          </div>
          <h2 className="text-3xl font-bold mb-4">Responsible Disclosure</h2>
          <p className="text-lg text-muted-foreground mb-6">
            If you discover a security vulnerability, please report it responsibly.
          </p>
          <div className="bg-card border border-border rounded-xl p-6 text-left max-w-2xl mx-auto">
            <h3 className="font-bold mb-4">How to Report:</h3>
            <ol className="space-y-3 text-sm">
              <li className="flex items-start gap-2">
                <span className="flex-shrink-0 w-6 h-6 rounded-full bg-aegis-500/10 flex items-center justify-center text-xs font-bold">1</span>
                <span>Email security@aegiscloud.in with details of the vulnerability</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="flex-shrink-0 w-6 h-6 rounded-full bg-aegis-500/10 flex items-center justify-center text-xs font-bold">2</span>
                <span>Include steps to reproduce and potential impact</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="flex-shrink-0 w-6 h-6 rounded-full bg-aegis-500/10 flex items-center justify-center text-xs font-bold">3</span>
                <span>We will acknowledge receipt within 24 hours</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="flex-shrink-0 w-6 h-6 rounded-full bg-aegis-500/10 flex items-center justify-center text-xs font-bold">4</span>
                <span>We will work with you to understand and resolve the issue</span>
              </li>
            </ol>
            <p className="text-sm text-muted-foreground mt-4">
              We appreciate responsible disclosure and will credit researchers who report valid vulnerabilities.
            </p>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto bg-gradient-to-br from-aegis-500/10 to-purple-500/10 rounded-2xl p-12 text-center">
          <h2 className="text-3xl font-bold mb-4">
            Security You Can Trust
          </h2>
          <p className="text-lg text-muted-foreground mb-8">
            Join thousands of organizations that trust Aegis Cloud for secure remote Windows management.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/auth/register"
              className="px-8 py-3 bg-aegis-600 text-white rounded-lg font-medium hover:bg-aegis-700 transition-colors"
            >
              Get Started Free
            </Link>
            <Link
              href="/contact"
              className="px-8 py-3 bg-card border border-border rounded-lg font-medium hover:bg-accent transition-colors"
            >
              Contact Security Team
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
