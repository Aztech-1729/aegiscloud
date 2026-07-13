'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Monitor, Cpu, MemoryStick, HardDrive, Activity, Clock,
  Power, RefreshCw, Terminal, MessageSquare, ArrowLeft,
  Wifi, Thermometer, Battery, Shield, Tag, Edit2,
  MoreHorizontal, Zap, BarChart3
} from 'lucide-react';

export default function DeviceDetailPage() {
  const device = {
    id: '1',
    name: 'Work Desktop',
    hostname: 'WORK-DESKTOP-01',
    status: 'online' as const,
    windowsVersion: 'Windows 11 Pro 23H2',
    windowsBuild: '22631.4460',
    agentVersion: 'v1.2.4',
    cpu: 'Intel Core i7-13700K',
    ram: '32 GB DDR5-5600',
    gpu: 'NVIDIA GeForce RTX 4070',
    diskTotal: 512,
    diskUsed: 234,
    uptime: '3d 14h 22m',
    lastSeen: 'Online now',
    tags: ['work', 'primary', 'engineering'],
    group: 'Office',
    ip: '192.168.1.105',
    publicIp: '203.0.113.42',
    autoUpdate: true,
  };

  const liveStats = {
    cpu: 34,
    ram: 67,
    gpu: 12,
    disk: 46,
    networkDown: 2.4,
    networkUp: 0.8,
    temperature: 62,
    battery: null,
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <a href="/dashboard/devices" className="p-2 rounded-lg hover:bg-accent transition-colors">
            <ArrowLeft className="h-4 w-4" />
          </a>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold">{device.name}</h1>
              <Badge variant="success" className="text-[10px]">{device.status}</Badge>
            </div>
            <p className="text-sm text-muted-foreground">{device.hostname} · {device.windowsVersion}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm"><Terminal className="h-4 w-4 mr-1" /> Terminal</Button>
          <Button variant="outline" size="sm"><MessageSquare className="h-4 w-4 mr-1" /> AI Chat</Button>
          <Button variant="outline" size="sm"><RefreshCw className="h-4 w-4 mr-1" /> Restart</Button>
          <Button variant="outline" size="sm"><Power className="h-4 w-4 mr-1" /> Shutdown</Button>
        </div>
      </div>

      {/* Tags */}
      <div className="flex items-center gap-2">
        <Tag className="h-4 w-4 text-muted-foreground" />
        {device.tags.map((tag) => (
          <Badge key={tag} variant="outline" className="text-xs">{tag}</Badge>
        ))}
        <button className="p-1 rounded hover:bg-accent transition-colors">
          <Edit2 className="h-3 w-3 text-muted-foreground" />
        </button>
      </div>

      {/* Live Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
        {[
          { label: 'CPU', value: `${liveStats.cpu}%`, icon: Cpu, color: 'text-aegis-400', bg: 'bg-aegis-500/10', percent: liveStats.cpu },
          { label: 'RAM', value: `${liveStats.ram}%`, icon: MemoryStick, color: 'text-purple-400', bg: 'bg-purple-500/10', percent: liveStats.ram },
          { label: 'GPU', value: `${liveStats.gpu}%`, icon: Zap, color: 'text-emerald-400', bg: 'bg-emerald-500/10', percent: liveStats.gpu },
          { label: 'Disk', value: `${liveStats.disk}%`, icon: HardDrive, color: 'text-amber-400', bg: 'bg-amber-500/10', percent: liveStats.disk },
          { label: '↓ Net', value: `${liveStats.networkDown} MB/s`, icon: Wifi, color: 'text-cyan-400', bg: 'bg-cyan-500/10', percent: null },
          { label: '↑ Net', value: `${liveStats.networkUp} MB/s`, icon: Wifi, color: 'text-blue-400', bg: 'bg-blue-500/10', percent: null },
          { label: 'Temp', value: `${liveStats.temperature}°C`, icon: Thermometer, color: 'text-orange-400', bg: 'bg-orange-500/10', percent: null },
          { label: 'Uptime', value: device.uptime, icon: Clock, color: 'text-muted-foreground', bg: 'bg-secondary/50', percent: null },
        ].map((stat) => (
          <Card key={stat.label} className="border-white/5">
            <CardContent className="p-3">
              <div className="flex items-center gap-2 mb-2">
                <div className={`p-1.5 rounded-lg ${stat.bg}`}>
                  <stat.icon className={`h-3.5 w-3.5 ${stat.color}`} />
                </div>
                <span className="text-xs text-muted-foreground">{stat.label}</span>
              </div>
              <p className="text-lg font-bold">{stat.value}</p>
              {stat.percent !== null && (
                <Progress value={stat.percent} className="h-1 mt-2" />
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="hardware">Hardware</TabsTrigger>
          <TabsTrigger value="history">History</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Card className="border-white/5">
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <BarChart3 className="h-4 w-4 text-aegis-400" />
                CPU Usage (24h)
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-end gap-0.5 h-32">
                {Array.from({ length: 48 }).map((_, i) => (
                  <div
                    key={i}
                    className="flex-1 rounded-t bg-gradient-to-t from-aegis-500/60 to-aegis-500/20 min-w-[3px]"
                    style={{ height: `${15 + Math.random() * 85}%` }}
                  />
                ))}
              </div>
              <div className="flex justify-between mt-2 text-xs text-muted-foreground">
                <span>24h ago</span>
                <span>12h ago</span>
                <span>Now</span>
              </div>
            </CardContent>
          </Card>

          <Card className="border-white/5">
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Activity className="h-4 w-4 text-purple-400" />
                RAM Usage (24h)
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-end gap-0.5 h-32">
                {Array.from({ length: 48 }).map((_, i) => (
                  <div
                    key={i}
                    className="flex-1 rounded-t bg-gradient-to-t from-purple-500/60 to-purple-500/20 min-w-[3px]"
                    style={{ height: `${40 + Math.random() * 40}%` }}
                  />
                ))}
              </div>
              <div className="flex justify-between mt-2 text-xs text-muted-foreground">
                <span>24h ago</span>
                <span>12h ago</span>
                <span>Now</span>
              </div>
            </CardContent>
          </Card>

          <Card className="border-white/5 lg:col-span-2">
            <CardHeader>
              <CardTitle className="text-base">Recent Activity</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[
                  { action: 'Cleaned temp files', time: '2 hours ago', status: 'completed' },
                  { action: 'CPU usage check', time: '3 hours ago', status: 'completed' },
                  { action: 'Restarted Explorer', time: '5 hours ago', status: 'completed' },
                  { action: 'Storage analysis', time: '1 day ago', status: 'completed' },
                  { action: 'Defender status check', time: '1 day ago', status: 'completed' },
                ].map((item, i) => (
                  <div key={i} className="flex items-center justify-between py-2 border-b border-white/5 last:border-0">
                    <div className="flex items-center gap-3">
                      <div className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                      <span className="text-sm">{item.action}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <Badge variant="success" className="text-[10px]">{item.status}</Badge>
                      <span className="text-xs text-muted-foreground">{item.time}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="hardware" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { label: 'CPU', value: device.cpu, icon: Cpu },
              { label: 'RAM', value: device.ram, icon: MemoryStick },
              { label: 'GPU', value: device.gpu, icon: Zap },
              { label: 'Disk', value: `${device.diskUsed} GB / ${device.diskTotal} GB`, icon: HardDrive },
              { label: 'OS', value: `${device.windowsVersion} (Build ${device.windowsBuild})`, icon: Monitor },
              { label: 'Agent', value: device.agentVersion, icon: Shield },
              { label: 'Local IP', value: device.ip, icon: Wifi },
              { label: 'Public IP', value: device.publicIp, icon: Wifi },
            ].map((item) => (
              <Card key={item.label} className="border-white/5">
                <CardContent className="p-4 flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-secondary/50">
                    <item.icon className="h-4 w-4 text-muted-foreground" />
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">{item.label}</p>
                    <p className="text-sm font-medium">{item.value}</p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="history">
          <Card className="border-white/5">
            <CardContent className="p-6 text-center text-muted-foreground">
              <Activity className="h-12 w-12 mx-auto mb-4 opacity-30" />
              <p>Full command history available in the History tab</p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="settings" className="space-y-4 max-w-lg">
          <Card className="border-white/5">
            <CardContent className="p-5 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">Auto Update</p>
                  <p className="text-xs text-muted-foreground">Automatically update the agent</p>
                </div>
                <button className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${device.autoUpdate ? 'bg-aegis-600' : 'bg-secondary'}`}>
                  <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${device.autoUpdate ? 'translate-x-6' : 'translate-x-1'}`} />
                </button>
              </div>
              <Separator />
              <div>
                <p className="text-sm font-medium mb-1.5">Device Name</p>
                <div className="flex gap-2">
                  <Input defaultValue={device.name} />
                  <Button variant="outline" size="sm">Save</Button>
                </div>
              </div>
              <Separator />
              <div>
                <p className="text-sm font-medium mb-1.5">Tags</p>
                <div className="flex flex-wrap gap-2">
                  {device.tags.map((tag) => (
                    <Badge key={tag} variant="outline" className="text-xs">{tag}</Badge>
                  ))}
                </div>
              </div>
              <Separator />
              <div>
                <p className="text-sm font-medium mb-1.5">Device Group</p>
                <select className="w-full h-10 rounded-lg border border-input bg-background px-3 text-sm">
                  <option>Office</option>
                  <option>Home</option>
                  <option>Gaming</option>
                  <option>Servers</option>
                </select>
              </div>
              <Separator />
              <div className="pt-2">
                <Button variant="destructive" className="w-full">Remove Device</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
