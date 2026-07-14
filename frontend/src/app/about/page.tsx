import Link from 'next/link';
import { Users, Globe, Award, Target, Heart, Shield } from 'lucide-react';

export const metadata = {
  title: 'About Us - AI-Powered Windows Management',
  description: 'Learn about Aegis Cloud, our mission to revolutionize Windows endpoint management with AI. Meet the team building the future of remote device management.',
  keywords: 'about aegis cloud, ai endpoint management company, windows management platform',
};

export default function AboutPage() {
  const team = [
    {
      name: 'Engineering Team',
      role: 'Building the Future',
      description: 'Our engineers are experts in Rust, Python, TypeScript, and distributed systems.',
      emoji: '👨‍💻',
    },
    {
      name: 'Security Team',
      role: 'Protecting Your Data',
      description: 'Security experts ensuring enterprise-grade protection for all devices.',
      emoji: '🔒',
    },
    {
      name: 'AI Team',
      role: 'Making It Intelligent',
      description: 'AI researchers building intelligent automation and natural language interfaces.',
      emoji: '🤖',
    },
    {
      name: 'Support Team',
      role: 'Here to Help',
      description: 'Dedicated support ensuring you get the help you need, when you need it.',
      emoji: '💬',
    },
  ];

  const values = [
    {
      icon: Shield,
      title: 'Security First',
      description: 'Every feature is built with security as a priority. Zero-trust architecture by design.',
    },
    {
      icon: Target,
      title: 'Simplicity',
      description: 'Complex technology made simple. Natural language interface for everyone.',
    },
    {
      icon: Heart,
      title: 'User-Centric',
      description: 'Built for real users. Every feature solves actual problems.',
    },
    {
      icon: Award,
      title: 'Excellence',
      description: 'We strive for excellence in everything we do. Quality over quantity.',
    },
  ];

  const milestones = [
    { year: '2024', event: 'Aegis Cloud Founded', description: 'Started with a vision to revolutionize Windows management' },
    { year: '2024', event: 'Agent Development', description: 'Built lightweight Rust agent with zero-trust security' },
    { year: '2025', event: 'AI Integration', description: 'Integrated AI assistant for natural language management' },
    { year: '2025', event: 'Beta Launch', description: 'Launched beta with 100 early adopters' },
    { year: '2026', event: 'Public Launch', description: 'Opened platform to all users worldwide' },
    { year: '2026', event: '10,000+ Users', description: 'Reached milestone of 10,000 active users' },
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-16">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-4xl sm:text-5xl font-bold mb-4">
              About Aegis Cloud
            </h1>
            <p className="text-xl text-muted-foreground">
              Revolutionizing Windows endpoint management with AI-powered automation
            </p>
          </div>
        </div>
      </header>

      {/* Mission */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold mb-4">Our Mission</h2>
              <p className="text-lg text-muted-foreground mb-6">
                To make Windows endpoint management simple, secure, and intelligent for everyone.
              </p>
              <p className="text-muted-foreground mb-4">
                We believe that managing Windows devices shouldn't require complex tools, extensive training, or dedicated IT staff. With AI-powered automation and natural language interfaces, anyone can manage their Windows PCs remotely.
              </p>
              <p className="text-muted-foreground">
                Our platform combines cutting-edge technology with user-friendly design to deliver an experience that's powerful yet accessible.
              </p>
            </div>
            <div className="bg-gradient-to-br from-aegis-500/10 to-purple-500/10 rounded-2xl p-8">
              <div className="space-y-6">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-xl bg-aegis-500/20 flex items-center justify-center flex-shrink-0">
                    <Globe className="h-6 w-6 text-aegis-400" />
                  </div>
                  <div>
                    <h3 className="font-bold mb-1">Global Reach</h3>
                    <p className="text-sm text-muted-foreground">
                      Users in 150+ countries trust Aegis Cloud
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-xl bg-purple-500/20 flex items-center justify-center flex-shrink-0">
                    <Users className="h-6 w-6 text-purple-400" />
                  </div>
                  <div>
                    <h3 className="font-bold mb-1">Growing Community</h3>
                    <p className="text-sm text-muted-foreground">
                      10,000+ active users and counting
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-xl bg-emerald-500/20 flex items-center justify-center flex-shrink-0">
                    <Award className="h-6 w-6 text-emerald-400" />
                  </div>
                  <div>
                    <h3 className="font-bold mb-1">Enterprise Ready</h3>
                    <p className="text-sm text-muted-foreground">
                      Trusted by businesses worldwide
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Values */}
      <section className="container mx-auto px-4 py-16 bg-card/30">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold mb-12 text-center">Our Values</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {values.map((value, index) => (
              <div key={index} className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-aegis-500/10 mb-4">
                  <value.icon className="h-8 w-8 text-aegis-400" />
                </div>
                <h3 className="text-xl font-bold mb-2">{value.title}</h3>
                <p className="text-sm text-muted-foreground">{value.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Team */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold mb-12 text-center">Our Team</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {team.map((member, index) => (
              <div key={index} className="bg-card border border-border rounded-xl p-6 text-center">
                <div className="text-5xl mb-4">{member.emoji}</div>
                <h3 className="text-lg font-bold mb-1">{member.name}</h3>
                <p className="text-sm text-aegis-400 mb-3">{member.role}</p>
                <p className="text-sm text-muted-foreground">{member.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Timeline */}
      <section className="container mx-auto px-4 py-16 bg-card/30">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold mb-12 text-center">Our Journey</h2>
          <div className="space-y-8">
            {milestones.map((milestone, index) => (
              <div key={index} className="flex items-start gap-4">
                <div className="flex-shrink-0 w-20">
                  <div className="text-2xl font-bold text-aegis-400">{milestone.year}</div>
                </div>
                <div className="flex-1 pb-8 border-l-2 border-aegis-500/20 pl-6">
                  <h3 className="text-lg font-bold mb-1">{milestone.event}</h3>
                  <p className="text-sm text-muted-foreground">{milestone.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold mb-12 text-center">By The Numbers</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {[
              { value: '10,000+', label: 'Active Users' },
              { value: '50,000+', label: 'Devices Managed' },
              { value: '150+', label: 'Countries' },
              { value: '99.99%', label: 'Uptime' },
            ].map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-4xl font-bold text-aegis-400 mb-2">{stat.value}</div>
                <div className="text-sm text-muted-foreground">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto bg-gradient-to-br from-aegis-500/10 to-purple-500/10 rounded-2xl p-12 text-center">
          <h2 className="text-3xl font-bold mb-4">
            Join Our Mission
          </h2>
          <p className="text-lg text-muted-foreground mb-8">
            Be part of the future of Windows endpoint management
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
              Contact Us
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
