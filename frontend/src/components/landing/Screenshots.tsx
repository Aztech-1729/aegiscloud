"use client";

import { useState } from 'react';
import { cn } from '@/lib/utils';
import { Monitor, MessageSquare, FolderOpen, Activity } from 'lucide-react';

const screenshots = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: Monitor,
    title: 'Command Center',
    description: 'Overview of all your connected devices with real-time stats, quick actions, and activity feed.',
  },
  {
    id: 'ai',
    label: 'AI Assistant',
    icon: MessageSquare,
    title: 'AI-Powered Chat',
    description: 'Natural language interface for managing your PC. Streaming responses with task progress tracking.',
  },
  {
    id: 'files',
    label: 'File Manager',
    icon: FolderOpen,
    title: 'Remote File Access',
    description: 'Browse, upload, download, and manage files on your Windows PCs. Full desktop integration.',
  },
  {
    id: 'monitor',
    label: 'Monitoring',
    icon: Activity,
    title: 'Live Metrics',
    description: 'Real-time CPU, RAM, GPU, disk, network, and battery monitoring with historical charts.',
  },
];

export function LandingScreenshots() {
  const [active, setActive] = useState('dashboard');

  const activeScreenshot = screenshots.find((s) => s.id === active)!;

  return (
    <section className="py-24 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">
            A Dashboard That{' '}
            <span className="gradient-text">Just Works</span>
          </h2>
          <p className="text-lg text-muted-foreground">
            Beautiful, intuitive, and powerful. Every pixel designed for efficient remote management.
          </p>
        </div>

        <div className="flex flex-wrap justify-center gap-3 mb-12">
          {screenshots.map((screenshot) => (
            <button
              key={screenshot.id}
              onClick={() => setActive(screenshot.id)}
              className={cn(
                'flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium transition-all duration-200',
                active === screenshot.id
                  ? 'bg-aegis-600 text-white shadow-lg shadow-aegis-600/25'
                  : 'bg-card/50 text-muted-foreground hover:text-foreground hover:bg-card border border-white/5'
              )}
            >
              <screenshot.icon className="h-4 w-4" />
              {screenshot.label}
            </button>
          ))}
        </div>

        <div className="relative">
          <div className="rounded-2xl overflow-hidden border border-white/10 bg-card/30 backdrop-blur-sm shadow-2xl">
            <div className="flex items-center gap-2 px-4 py-3 border-b border-white/5">
              <div className="flex gap-1.5">
                <div className="w-3 h-3 rounded-full bg-red-500/80" />
                <div className="w-3 h-3 rounded-full bg-amber-500/80" />
                <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
              </div>
              <div className="flex-1 text-center text-xs text-muted-foreground">
                app.aegiscloud.io/dashboard/{active}
              </div>
            </div>
            <div className="p-8 min-h-[450px] bg-gradient-to-br from-card/50 to-secondary/30">
              {active === 'dashboard' && (
                <div className="space-y-6 animate-fade-in">
                  <div className="grid grid-cols-3 gap-4">
                    <div className="p-4 rounded-xl bg-card/60 border border-white/5">
                      <p className="text-xs text-muted-foreground">Total Devices</p>
                      <p className="text-3xl font-bold mt-1">12</p>
                      <p className="text-xs text-emerald-400 mt-1">+2 this week</p>
                    </div>
                    <div className="p-4 rounded-xl bg-card/60 border border-white/5">
                      <p className="text-xs text-muted-foreground">Online Now</p>
                      <p className="text-3xl font-bold mt-1">8</p>
                      <p className="text-xs text-aegis-400 mt-1">67% uptime</p>
                    </div>
                    <div className="p-4 rounded-xl bg-card/60 border border-white/5">
                      <p className="text-xs text-muted-foreground">Tasks Today</p>
                      <p className="text-3xl font-bold mt-1">24</p>
                      <p className="text-xs text-purple-400 mt-1">All successful</p>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 rounded-xl bg-card/60 border border-white/5 h-48">
                      <p className="text-sm font-medium mb-4">CPU Usage (24h)</p>
                      <div className="flex items-end gap-1 h-28">
                        {Array.from({ length: 24 }).map((_, i) => (
                          <div
                            key={i}
                            className="flex-1 rounded-t bg-gradient-to-t from-aegis-500/60 to-aegis-500/20"
                            style={{ height: `${(20 + (Math.sin(i) + 1) * 40).toFixed(2)}%` }}
                          />
                        ))}
                      </div>
                    </div>
                    <div className="p-4 rounded-xl bg-card/60 border border-white/5 h-48">
                      <p className="text-sm font-medium mb-4">Recent Activity</p>
                      <div className="space-y-3">
                        {['Cleaned temp files', 'Restarted explorer', 'Listed processes'].map((item) => (
                          <div key={item} className="flex items-center gap-3 text-sm">
                            <div className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                            <span className="text-muted-foreground">{item}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}
              {active === 'ai' && (
                <div className="max-w-2xl mx-auto space-y-4 animate-fade-in">
                  <div className="flex justify-end">
                    <div className="bg-aegis-600/20 border border-aegis-500/20 rounded-2xl rounded-tr-sm px-4 py-3 max-w-md">
                      <p className="text-sm">My PC is running slow. Can you help diagnose the issue?</p>
                    </div>
                  </div>
                  <div className="flex justify-start">
                    <div className="bg-card/80 border border-white/10 rounded-2xl rounded-tl-sm px-4 py-3 max-w-md">
                      <p className="text-sm mb-3">I&apos;ll check your system for you. Let me look at CPU, memory usage, and running processes.</p>
                      <div className="space-y-2">
                        <div className="flex items-center gap-2 text-xs text-emerald-400">
                          <div className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                          <span>cpu_usage — completed</span>
                        </div>
                        <div className="flex items-center gap-2 text-xs text-emerald-400">
                          <div className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                          <span>ram_usage — completed</span>
                        </div>
                        <div className="flex items-center gap-2 text-xs text-amber-400">
                          <div className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
                          <span>list_processes — running...</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              {active === 'files' && (
                <div className="animate-fade-in">
                  <div className="flex items-center gap-2 mb-4 p-3 rounded-xl bg-card/60 border border-white/5">
                    <span className="text-sm text-muted-foreground">C:\Users\User\</span>
                    <span className="text-sm text-foreground">Desktop</span>
                  </div>
                  <div className="grid grid-cols-4 gap-3">
                    {['Documents', 'Downloads', 'Pictures', 'Videos', 'report.docx', 'notes.txt', 'image.png', 'archive.zip'].map((name) => (
                      <div key={name} className="p-3 rounded-xl bg-card/40 border border-white/5 hover:bg-card/60 transition-colors cursor-pointer text-center">
                        <div className="text-2xl mb-1">{name.includes('.') ? '📄' : '📁'}</div>
                        <p className="text-xs text-muted-foreground truncate">{name}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              {active === 'monitor' && (
                <div className="grid grid-cols-2 gap-4 animate-fade-in">
                  {[
                    { label: 'CPU', value: '34%', usage: 34, color: 'from-aegis-500 to-blue-500' },
                    { label: 'Memory', value: '67%', usage: 67, color: 'from-purple-500 to-pink-500' },
                    { label: 'GPU', value: '12%', usage: 12, color: 'from-emerald-500 to-cyan-500' },
                    { label: 'Disk', value: '54%', usage: 54, color: 'from-amber-500 to-orange-500' },
                  ].map((metric) => (
                    <div key={metric.label} className="p-5 rounded-xl bg-card/60 border border-white/5">
                      <div className="flex justify-between items-center mb-3">
                        <span className="text-sm text-muted-foreground">{metric.label}</span>
                        <span className="text-lg font-bold">{metric.value}</span>
                      </div>
                      <div className="h-3 rounded-full bg-secondary overflow-hidden">
                        <div
                          className={`h-full rounded-full bg-gradient-to-r ${metric.color} transition-all duration-1000`}
                          style={{ width: `${metric.usage}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
          <div className="absolute -inset-4 bg-gradient-to-r from-aegis-500/10 via-purple-500/10 to-pink-500/10 rounded-3xl blur-xl -z-10" />
        </div>

        <div className="mt-8 text-center">
          <h3 className="text-xl font-semibold mb-2">{activeScreenshot.title}</h3>
          <p className="text-muted-foreground max-w-lg mx-auto">{activeScreenshot.description}</p>
        </div>
      </div>
    </section>
  );
}

