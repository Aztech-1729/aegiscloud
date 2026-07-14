'use client';

import { Button } from '@/components/ui/button';
import { ArrowRight, Download, Shield, Monitor, Cpu, CheckCircle2, LayoutDashboard } from 'lucide-react';
import Link from 'next/link';
import { useState, useEffect } from 'react';
import { useAuthStore } from '@/stores';

export function LandingHero() {
  const { isAuthenticated, isLoading } = useAuthStore();
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setVisible(true), 100);
    return () => clearTimeout(timer);
  }, []);

  return (
    <section className="relative pt-32 pb-20 px-4 sm:px-6 lg:px-8 overflow-hidden">
      <div className="max-w-7xl mx-auto">
        <div className="text-center max-w-4xl mx-auto">
          <div
            className={`inline-flex items-center gap-2 px-4 py-2 rounded-full glass mb-8 transition-all duration-700 ${
              visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
            }`}
          >
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
            </span>
            <span className="text-sm text-muted-foreground">Now in Public Beta — Free to get started</span>
          </div>

          <h1
            className={`text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight mb-6 transition-all duration-700 delay-200 ${
              visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
            }`}
          >
            <span className="text-foreground">Manage Your Windows PCs</span>
            <br />
            <span className="gradient-text">From Anywhere with AI</span>
          </h1>

          <p
            className={`text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto mb-10 leading-relaxed transition-all duration-700 delay-300 ${
              visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
            }`}
          >
            Aegis Cloud gives you complete control over your Windows devices through a beautiful web dashboard.
            AI-powered tasks, real-time monitoring, and enterprise-grade security.
          </p>

          <div
            className={`flex flex-col sm:flex-row items-center justify-center gap-4 transition-all duration-700 delay-500 ${
              visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
            }`}
          >
            {isAuthenticated ? (
              <Link href="/dashboard">
                <Button variant="gradient" size="xl" className="group w-full sm:w-auto">
                  <LayoutDashboard className="mr-2 h-5 w-5" />
                  Go to Dashboard
                </Button>
              </Link>
            ) : (
              <Link href="/auth/register">
                <Button variant="gradient" size="xl" className="group w-full sm:w-auto">
                  Get Started Free
                  <ArrowRight className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
                </Button>
              </Link>
            )}
            <a href="/AegisSetup.exe" download>
              <Button variant="outline" size="xl" className="group w-full sm:w-auto">
                <Download className="mr-2 h-5 w-5" />
                Download Agent
              </Button>
            </a>
          </div>

          <div
            className={`flex flex-wrap items-center justify-center gap-6 mt-12 text-sm text-muted-foreground transition-all duration-700 delay-700 ${
              visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
            }`}
          >
            {[
              { icon: Shield, label: '256-bit Encryption' },
              { icon: Monitor, label: 'Unlimited Devices' },
              { icon: Cpu, label: 'AI-Powered' },
              { icon: CheckCircle2, label: 'SOC 2 Target' },
            ].map((item) => (
              <div key={item.label} className="flex items-center gap-2">
                <item.icon className="h-4 w-4 text-aegis-400" />
                <span>{item.label}</span>
              </div>
            ))}
          </div>
        </div>

        <div className={`mt-20 relative transition-all duration-1000 delay-500 ${visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
          <div className="absolute inset-0 bg-gradient-to-t from-background via-transparent to-transparent z-10 pointer-events-none" />
          <div className="relative rounded-2xl overflow-hidden border border-white/10 shadow-2xl shadow-aegis-500/10">
            <div className="bg-card/80 backdrop-blur-xl p-1">
              <div className="flex items-center gap-2 px-4 py-3 border-b border-white/5">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-red-500/80" />
                  <div className="w-3 h-3 rounded-full bg-amber-500/80" />
                  <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
                </div>
                <div className="flex-1 text-center text-xs text-muted-foreground">
                  app.aegiscloud.io/dashboard
                </div>
                <div className="text-xs text-muted-foreground">⌘K</div>
              </div>
              <div className="bg-gradient-to-br from-card to-secondary/50 p-6 sm:p-8 min-h-[300px] sm:min-h-[400px]">
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4 mb-6">
                  {['Total Devices', 'Online', 'Active Tasks', 'Storage'].map((label, i) => (
                    <div key={label} className="rounded-xl bg-card/60 border border-white/5 p-3 sm:p-4">
                      <p className="text-xs text-muted-foreground">{label}</p>
                      <p className="text-xl sm:text-2xl font-bold mt-1">{[12, 8, 3, '67%'][i]}</p>
                    </div>
                  ))}
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                  {[
                    { name: 'Work Desktop', status: 'online', cpu: 23, ram: 67 },
                    { name: 'Gaming PC', status: 'online', cpu: 78, ram: 45 },
                    { name: 'Home Office', status: 'offline', cpu: 0, ram: 0 },
                    { name: 'Server', status: 'online', cpu: 45, ram: 89 },
                  ].map((device) => (
                    <div key={device.name} className="rounded-xl bg-card/60 border border-white/5 p-3 sm:p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium">{device.name}</span>
                        <span className={`w-2 h-2 rounded-full ${device.status === 'online' ? 'bg-emerald-500' : 'bg-gray-500'}`} />
                      </div>
                      <div className="flex gap-4 text-xs text-muted-foreground">
                        <span>CPU: {device.cpu}%</span>
                        <span>RAM: {device.ram}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
          <div className="absolute -inset-4 bg-gradient-to-r from-aegis-500/20 via-purple-500/20 to-pink-500/20 rounded-3xl blur-2xl -z-10" />
        </div>
      </div>
    </section>
  );
}
