'use client';

import { cn } from '@/lib/utils';
import {
  Shield, Cpu, Brain, Monitor, HardDrive, Wifi,
  Zap, Eye, Lock
} from 'lucide-react';

const features = [
  {
    icon: Brain,
    title: 'AI-Powered Assistant',
    description: 'Natural language commands to optimize, troubleshoot, and manage your PC. The AI only uses approved tools for safety.',
    color: 'text-aegis-400',
    bg: 'bg-aegis-500/10',
  },
  {
    icon: Monitor,
    title: 'Real-Time Monitoring',
    description: 'Live CPU, RAM, GPU, disk, network, and battery stats with auto-refresh. See everything at a glance.',
    color: 'text-emerald-400',
    bg: 'bg-emerald-500/10',
  },
  {
    icon: Shield,
    title: 'Enterprise Security',
    description: 'End-to-end encrypted WebSockets, JWT auth, 2FA, RBAC, and secure device pairing with one-time codes.',
    color: 'text-purple-400',
    bg: 'bg-purple-500/10',
  },
  {
    icon: HardDrive,
    title: 'File Management',
    description: 'Browse, upload, download, rename, and organize files on your remote Windows PCs from the browser.',
    color: 'text-amber-400',
    bg: 'bg-amber-500/10',
  },
  {
    icon: Zap,
    title: 'Instant Tasks',
    description: 'Run approved operations like cleanup, process management, service control, and system maintenance instantly.',
    color: 'text-cyan-400',
    bg: 'bg-cyan-500/10',
  },
  {
    icon: Wifi,
    title: 'Auto-Connect',
    description: 'Pair once, connect forever. The lightweight Windows agent starts with your system and reconnects automatically.',
    color: 'text-pink-400',
    bg: 'bg-pink-500/10',
  },
  {
    icon: Eye,
    title: 'Complete History',
    description: 'Full audit trail of every action, task, and connection. Search, filter, and export for compliance needs.',
    color: 'text-orange-400',
    bg: 'bg-orange-500/10',
  },
  {
    icon: Lock,
    title: 'Zero Trust Architecture',
    description: 'The AI never executes arbitrary commands. Only pre-approved tools exposed by the agent can run on your system.',
    color: 'text-indigo-400',
    bg: 'bg-indigo-500/10',
  },
  {
    icon: Cpu,
    title: 'Lightweight Agent',
    description: 'Built in Rust for minimal resource usage. Runs as a Windows service with auto-updates and crash recovery.',
    color: 'text-violet-400',
    bg: 'bg-violet-500/10',
  },
];

export function LandingFeatures() {
  return (
    <section id="features" className="py-24 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">
            Everything You Need to{' '}
            <span className="gradient-text">Manage Remotely</span>
          </h2>
          <p className="text-lg text-muted-foreground">
            A comprehensive suite of tools for monitoring, managing, and optimizing your Windows devices from anywhere in the world.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <div
              key={feature.title}
              className={cn(
                'group relative rounded-2xl p-6 border border-white/5 bg-card/50 backdrop-blur-sm',
                'hover:border-white/10 hover:bg-card/80 transition-all duration-300 hover-lift',
                'animate-fade-in'
              )}
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <div className={cn('inline-flex p-3 rounded-xl mb-4', feature.bg)}>
                <feature.icon className={cn('h-6 w-6', feature.color)} />
              </div>
              <h3 className="text-lg font-semibold mb-2 text-foreground group-hover:text-white transition-colors">
                {feature.title}
              </h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
