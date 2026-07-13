'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import {
  Monitor, Wifi, WifiOff, ListTodo, HardDrive, Activity,
  ArrowUpRight, Cpu, MemoryStick, Plus
} from 'lucide-react';
import Link from 'next/link';

const stats = [
  { label: 'Total Devices', value: '12', icon: Monitor, change: '+2 this week', color: 'text-aegis-400', bg: 'bg-aegis-500/10' },
  { label: 'Online', value: '8', icon: Wifi, change: '67% uptime', color: 'text-emerald-400', bg: 'bg-emerald-500/10' },
  { label: 'Active Tasks', value: '3', icon: ListTodo, change: '1 pending', color: 'text-purple-400', bg: 'bg-purple-500/10' },
  { label: 'Storage Used', value: '67%', icon: HardDrive, change: '342 GB free', color: 'text-amber-400', bg: 'bg-amber-500/10' },
];

const devices = [
  { name: 'Work Desktop', status: 'online', cpu: 23, ram: 67, os: 'Windows 11 Pro' },
  { name: 'Gaming PC', status: 'online', cpu: 78, ram: 45, os: 'Windows 11 Home' },
  { name: 'Home Office', status: 'offline', cpu: 0, ram: 0, os: 'Windows 10 Pro' },
  { name: 'Media Server', status: 'online', cpu: 45, ram: 89, os: 'Windows 11 Pro' },
  { name: 'Dev Machine', status: 'offline', cpu: 0, ram: 0, os: 'Windows 11 Pro' },
  { name: 'Backup NAS', status: 'online', cpu: 12, ram: 34, os: 'Windows Server 2022' },
];

const recentActivity = [
  { action: 'Cleaned temp files', device: 'Work Desktop', time: '2 min ago', status: 'completed' },
  { action: 'Restarted Explorer', device: 'Gaming PC', time: '15 min ago', status: 'completed' },
  { action: 'Listed installed apps', device: 'Media Server', time: '1h ago', status: 'completed' },
  { action: 'Storage analysis', device: 'Work Desktop', time: '2h ago', status: 'completed' },
  { action: 'Flush DNS cache', device: 'Gaming PC', time: '3h ago', status: 'completed' },
];

export default function DashboardPage() {
  return (
    <div className="space-y-6 animate-fade-in">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <Card key={stat.label} className="hover-lift border-white/5">
            <CardContent className="p-5">
              <div className="flex items-center justify-between mb-3">
                <div className={`p-2 rounded-lg ${stat.bg}`}>
                  <stat.icon className={`h-5 w-5 ${stat.color}`} />
                </div>
                <ArrowUpRight className="h-4 w-4 text-muted-foreground" />
              </div>
              <p className="text-2xl font-bold">{stat.value}</p>
              <p className="text-sm text-muted-foreground mt-1">{stat.label}</p>
              <p className={`text-xs ${stat.color} mt-2`}>{stat.change}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2 border-white/5">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-lg">Devices</CardTitle>
            <Link href="/dashboard/devices">
              <Button variant="ghost" size="sm">View All</Button>
            </Link>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {devices.slice(0, 5).map((device) => (
                <div
                  key={device.name}
                  className="flex items-center justify-between p-3 rounded-xl bg-secondary/30 hover:bg-secondary/50 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-2 h-2 rounded-full ${device.status === 'online' ? 'bg-emerald-400' : 'bg-gray-500'}`} />
                    <div>
                      <p className="text-sm font-medium">{device.name}</p>
                      <p className="text-xs text-muted-foreground">{device.os}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-6">
                    <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                      <Cpu className="h-3 w-3" />
                      {device.cpu}%
                    </div>
                    <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                      <MemoryStick className="h-3 w-3" />
                      {device.ram}%
                    </div>
                    <Badge variant={device.status === 'online' ? 'success' : 'secondary'}>
                      {device.status}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="border-white/5">
          <CardHeader>
            <CardTitle className="text-lg">Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivity.map((activity, i) => (
                <div key={i} className="flex items-start gap-3">
                  <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-2 shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium">{activity.action}</p>
                    <p className="text-xs text-muted-foreground">
                      {activity.device} · {activity.time}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="border-white/5">
          <CardHeader>
            <CardTitle className="text-lg">System Resources</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {[
              { label: 'CPU Usage', value: 34, color: 'from-aegis-500 to-blue-500' },
              { label: 'Memory', value: 67, color: 'from-purple-500 to-pink-500' },
              { label: 'Disk', value: 54, color: 'from-amber-500 to-orange-500' },
              { label: 'Network', value: 23, color: 'from-emerald-500 to-cyan-500' },
            ].map((metric) => (
              <div key={metric.label} className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">{metric.label}</span>
                  <span className="font-medium">{metric.value}%</span>
                </div>
                <Progress value={metric.value} className="h-2" />
              </div>
            ))}
          </CardContent>
        </Card>

        <Card className="border-white/5">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-lg">Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-3">
              {[
                { label: 'Pair New Device', icon: Plus },
                { label: 'AI Assistant', icon: Activity },
                { label: 'File Manager', icon: HardDrive },
                { label: 'Task History', icon: ListTodo },
              ].map((action) => (
                <button
                  key={action.label}
                  className="flex flex-col items-center gap-2 p-4 rounded-xl border border-white/5 bg-secondary/20 hover:bg-secondary/40 transition-all duration-200 hover-lift"
                >
                  <action.icon className="h-6 w-6 text-aegis-400" />
                  <span className="text-xs text-muted-foreground">{action.label}</span>
                </button>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
