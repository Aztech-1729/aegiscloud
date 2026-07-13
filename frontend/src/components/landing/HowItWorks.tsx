'use client';

import { Download, Link2, LayoutDashboard, Brain } from 'lucide-react';

const steps = [
  {
    icon: Download,
    step: '01',
    title: 'Download the Agent',
    description: 'Download our lightweight Rust-based Windows agent. It installs in seconds and runs as a background service.',
    color: 'from-aegis-500 to-blue-500',
  },
  {
    icon: Link2,
    step: '02',
    title: 'Pair Your Device',
    description: 'The agent generates a unique pairing code. Enter it in your dashboard to securely link your device.',
    color: 'from-purple-500 to-pink-500',
  },
  {
    icon: LayoutDashboard,
    step: '03',
    title: 'Access Your Dashboard',
    description: 'Instantly see your device stats, manage files, run tasks, and monitor everything in real-time.',
    color: 'from-emerald-500 to-cyan-500',
  },
  {
    icon: Brain,
    step: '04',
    title: 'Let AI Help',
    description: 'Use natural language to perform tasks. "Clean temp files", "Show installed apps" — the AI handles the rest.',
    color: 'from-amber-500 to-orange-500',
  },
];

export function LandingHowItWorks() {
  return (
    <section id="how-it-works" className="py-24 px-4 sm:px-6 lg:px-8 relative">
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-aegis-950/20 to-transparent" />
      <div className="max-w-7xl mx-auto relative">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">
            Up and Running in{' '}
            <span className="gradient-text">Minutes</span>
          </h2>
          <p className="text-lg text-muted-foreground">
            Four simple steps to remote PC management. No complex configuration, no IT team required.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {steps.map((step, index) => (
            <div key={step.title} className="relative">
              {index < steps.length - 1 && (
                <div className="hidden lg:block absolute top-12 left-[60%] w-[80%] h-px bg-gradient-to-r from-white/20 to-transparent" />
              )}
              <div className="text-center group">
                <div className="relative inline-flex mb-6">
                  <div className={`w-20 h-20 rounded-2xl bg-gradient-to-br ${step.color} flex items-center justify-center shadow-lg transition-transform group-hover:scale-110 duration-300`}>
                    <step.icon className="h-8 w-8 text-white" />
                  </div>
                  <div className="absolute -top-2 -right-2 w-8 h-8 rounded-full bg-card border border-border flex items-center justify-center text-xs font-bold text-foreground">
                    {step.step}
                  </div>
                </div>
                <h3 className="text-lg font-semibold mb-2">{step.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed max-w-xs mx-auto">
                  {step.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
